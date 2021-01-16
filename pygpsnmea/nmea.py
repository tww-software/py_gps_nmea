"""
manage the NMEA sentences
"""

import collections
import datetime
import statistics

import pygpsnmea.allsentences as allsentences
import pygpsnmea.kml as kml
import pygpsnmea.sentences.sentence as sentences


def calculate_time_duration(start, end):
    """
    calculate how long between two times

    Args:
        start(datetime.datetime): the start time
        end(datetime.datetime): the end time

    Returns:
        duration(dict): dict containing the duration in days, hours,
                        minutes and seconds
    """
    timediff = end - start
    totalseconds = timediff.total_seconds()
    days, remainder = divmod(totalseconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    duration = {
        'days': days, 'hours': hours, 'minutes': minutes,
        'seconds': int(seconds)}
    return duration


def calculate_altitudes_and_speeds(positions, altunits='M'):
    """
    calculate the highest, fastest and lowest values for speed and altitude

    Args:
        positions(list): list of dicts, each dict is a position report

    Returns:
        records(dict): dictionary of stats for speeds and altitudes
    """
    alts = []
    speeds = []
    records = {}
    for posrep in positions:
        try:
            speeds.append(float(posrep['speed (knots)']))
        except KeyError:
            pass
        try:
            altfloat = float(posrep['altitude'].rstrip(' ' + altunits))
            alts.append(altfloat)
        except KeyError:
            pass
    if speeds:
        maxspeed = max(speeds)
        avgspeed = round(statistics.fmean(speeds), 3)
        records['maximum speed (knots)'] = maxspeed
        records['average speed (knots)'] = avgspeed
    if alts:
        maxalt = round(max(alts), 3)
        minalt = round(min(alts), 3)
        altitudeclimbed = round(maxalt - minalt, 3)
        records['maximum altitude ({})'.format(altunits)] = maxalt
        records['minimum altitude ({})'.format(altunits)] = minalt
        records['altitude difference ({})'.format(altunits)] = altitudeclimbed
    return records


class NoSuitablePositionReport(Exception):
    """
    raise when we have no position data
    """


class NMEASentenceManager():
    """
    class to keep track of all the NMEA sentences
    """

    def __init__(self):
        self.sentences = []
        self.sentencetypes = collections.Counter()
        self.positions = collections.OrderedDict()
        self.datetimes = []
        self.lastdate = ''
        self.checksumerrors = 0

    def process_sentence(self, sentence):
        """
        take an NMEA 0183 GPS sentence and process it

        Args:
            sentence(str): NMEA sentence

        Returns:
            newpos(dict): position report
        """
        self.sentences.append(sentence)
        sentencelist = sentence.split(',')
        sentencetype = sentencelist[0]
        self.sentencetypes[sentencetype] += 1
        errorflag = False
        if sentencetype in allsentences.ALLSENTENCES.keys():
            try:
                newsentence = \
                    allsentences.ALLSENTENCES[sentencetype](sentencelist)
                newpos = {}
                if sentencetype in allsentences.VALIDATIONCHECKS:
                    if not newsentence.valid:
                        errorflag = True
                if sentencetype in allsentences.DATE:
                    if newsentence.date != self.lastdate:
                        self.lastdate = newsentence.date
                if sentencetype in allsentences.LATLONTIME:
                    newpos['latitude'] = newsentence.latitude
                    newpos['longitude'] = newsentence.longitude
                    if self.lastdate != '':
                        tstr = self.lastdate + ' ' + newsentence.time
                        newdt = datetime.datetime.strptime(
                            tstr, '%d%m%y %H%M%S.%f')
                        timestr = newdt.strftime('%Y/%m/%d %T')
                        newpos['time'] = timestr 
                    if sentencetype in allsentences.DATETIME:
                        self.datetimes.append(newsentence.datetime)
                    if sentencetype in allsentences.ALTITUDES:
                        newpos['altitude'] = newsentence.altitude
                    if sentencetype in allsentences.SPEEDS:
                        newpos['speed (knots)'] = newsentence.speed
                    if sentencetype in allsentences.FIXQUALITY:
                        newpos['fix quality'] = newsentence.fixquality
                    if sentencetype in allsentences.SATELLITESTRACKED:
                        newpos['satellites tracked'] = \
                            newsentence.satellitestracked
                    if not errorflag:
                        try:
                            self.positions[timestr].update(newpos)
                        except KeyError:
                            self.positions[timestr] = newpos
            except sentences.CheckSumFailed:
                self.checksumerrors += 1
                errorflag = True
            except ValueError:
                errorflag = True

    def get_latest_position(self):
        """
        return the last known position we have

        Raises:
            NoSuitablePositionReport: if no position found

        Returns:
            self.positions(dict): last item in self.positions
        """
        try:
            positionlist = list(self.positions.values())
            return positionlist[len(positionlist) - 1]
        except (IndexError, AttributeError) as err:
            raise NoSuitablePositionReport('Unknown') from err

    def get_start_position(self):
        """
        return the first known position we have

        Raises:
            NoSuitablePositionReport: if no position found

        Returns:
            self.positions(dict): last item in self.positions
        """
        try:
            positionlist = list(self.positions.values())
            return positionlist[0]
        except (IndexError, AttributeError) as err:
            raise NoSuitablePositionReport('Unknown') from err

    def stats(self):
        """
        return stats from this NMEA manager

        Returns:
            stats(dict): dict full of stats from this NMEA manager object
        """
        stats = {}
        stats['total sentences'] = len(self.sentences)
        stats['total positions'] = len(self.positions)
        stats['checksum errors'] = self.checksumerrors
        try:
            firstpos = self.get_start_position()
            lastpos = self.get_latest_position()
        except NoSuitablePositionReport:
            return stats
        stats['sentence types'] = self.sentencetypes
        stats['start position'] = firstpos
        stats['end position'] = lastpos
        stats['duration'] = calculate_time_duration(
            self.datetimes[0], self.datetimes[len(self.datetimes) - 1])
        stats['speeds and altitudes'] = calculate_altitudes_and_speeds(
            list(self.positions.values()))
        return stats

    def create_kml_map(self, outputfile, verbose=True):
        """
        create a kml map from all the positions we have
        """
        try:
            start = self.get_start_position()
            end = self.get_latest_position()
        except NoSuitablePositionReport as err:
            print('unable to make KML map')
            raise err
        poslist = list(self.positions.values())
        kmlmap = kml.KMLOutputParser(outputfile)
        kmlmap.create_kml_header('test')
        kmlmap.add_kml_placemark_linestring('linestring', poslist)
        kmlmap.add_kml_placemark(
            'start', 'starting position', str(start['longitude']),
            str(start['latitude']))
        if verbose:
            poscount = 2
            for posrep in poslist[1:len(self.positions) - 2]:
                kmltime = kml.convert_timestamp_to_kmltimestamp(posrep['time'])
                posdesc = kmlmap.format_kml_placemark_description(posrep)
                kmlmap.add_kml_placemark(
                    str(poscount), posdesc, str(posrep['longitude']),
                    str(posrep['latitude']), timestamp=kmltime)
                poscount += 1
        kmlmap.add_kml_placemark(
            'end', 'ending position', str(end['longitude']),
            str(end['latitude']))
        kmlmap.close_kml_file()
        kmlmap.write_kml_doc_file()

    def create_positions_table(self):
        """
        create a list of lists for csv file export of all the position reports
        """
        positiontable = []
        headers = ['latitude', 'longitude', 'time']
        positiontable.append(headers)
        for posrep in list(self.positions.values()):
            line = []
            line.append(posrep['latitude'])
            line.append(posrep['longitude'])
            line.append(posrep['time'])
            positiontable.append(line)
        return positiontable
