"""
manage the NMEA sentences
"""

import collections
import datetime
import statistics

import pygpsnmea.allsentences as allsentences
import pygpsnmea.geojson as geojson
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
        altunits(str): altitude units, default is metres (M)

    Returns:
        records(dict): dictionary of stats for speeds and altitudes
    """
    altlabel = 'altitude ({})'.format(altunits)
    alts = []
    speeds = []
    records = {}
    for posrep in positions:
        try:
            speeds.append(float(posrep['speed (knots)']))
        except KeyError:
            pass
        try:
            altfloat = float(posrep[altlabel].rstrip(' ' + altunits))
            alts.append(altfloat)
        except KeyError:
            pass
    if speeds:
        maxspeed = max(speeds)
        avgspeed = round(statistics.mean(speeds), 3)
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

    Attributes:
        sentencetypes(collections.Counter): a count of the different sentence
                                            types we have encountered
        positions(collections.OrderedDict): all the positions in order of which
                                            we recieved them
        datetimes(list): all the datetimes - used to calculate duration
        lastdate(str): the last known date we have
        checksumerrors(int): the number of sentences with checksum errors we
                             have encountered
        positioncount(int): number of positions we have processed
        altitudeunits(str): what do we measure altitude as
    """

    def __init__(self):
        self.clear_data()

    def clear_data(self):
        """
        clear and start afresh
        """
        self.sentencetypes = collections.Counter()
        self.positions = collections.OrderedDict()
        self.datetimes = []
        self.lastdate = ''
        self.checksumerrors = 0
        self.positioncount = 0
        self.altitudeunits = ''

    def process_sentence(self, sentence):
        """
        take an NMEA 0183 GPS sentence and process it

        Args:
            sentence(str): NMEA sentence
        """
        sentencelist = sentence.split(',')
        sentencetype = sentencelist[0]
        errorflag = False
        if sentencetype in allsentences.ALLSENTENCES.keys():
            self.sentencetypes[sentencetype] += 1
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
                        if self.altitudeunits == '':
                            self.altitudeunits = newsentence.altitudeunits
                        altlabel = \
                            'altitude ({})'.format(newsentence.altitudeunits)
                        newpos[altlabel] = newsentence.altitude
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
                            self.positioncount += 1
                            newpos['position no'] = self.positioncount
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
            self.positions(dict): first item in self.positions
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
        stats['total positions'] = self.positioncount
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
            list(self.positions.values()), altunits=self.altitudeunits)
        return stats

    def create_kml_map(self, outputfile, verbose=True):
        """
        create a kml map from all the positions we have

        Args:
            outputfile(str): full file path to output
            verbose(bool): should we plot every single position (default) or
                           just the start and end with a linestring
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
        startdesc = kmlmap.format_kml_placemark_description(start)
        kmlmap.add_kml_placemark(
            'start', startdesc, str(start['longitude']),
            str(start['latitude']))
        if verbose:
            kmlmap.open_folder('points')
            poscount = 2
            for posrep in poslist[1:len(self.positions) - 1]:
                kmltime = kml.convert_timestamp_to_kmltimestamp(posrep['time'])
                posdesc = kmlmap.format_kml_placemark_description(posrep)
                kmlmap.add_kml_placemark(
                    str(poscount), posdesc, str(posrep['longitude']),
                    str(posrep['latitude']), timestamp=kmltime)
                poscount += 1
            kmlmap.close_folder()
        enddesc = kmlmap.format_kml_placemark_description(end)
        kmlmap.add_kml_placemark(
            'end', enddesc, str(end['longitude']),
            str(end['latitude']))
        kmlmap.close_kml_file()
        kmlmap.write_kml_doc_file()

    def create_geojson_map(self, outputfile, verbose=True):
        """
        create a geojson map from the positions we have

        Args:
            outputfile(str): full file path to output
            verbose(bool): should we plot every single position (default) or
                           just the start and end with a linestring
        """
        try:
            start = self.get_start_position()
            end = self.get_latest_position()
        except NoSuitablePositionReport as err:
            print('unable to make GEOJSON map')
            raise err
        poslist = list(self.positions.values())
        geojsonmap = geojson.GeoJsonParser()
        coords = [[pos['latitude'], pos['longitude']] for pos in poslist]
        stats = self.stats()
        linestrproperties = {
            'total positions': stats['total positions'],
            'duration': stats['duration']}
        geojsonmap.add_map_linestring(coords, linestrproperties)
        geojsonmap.add_map_point(start, start['longitude'],
                                 start['latitude'])
        if verbose:
            for posrep in poslist[1:len(self.positions) - 1]:
                geojsonmap.add_map_point(
                    posrep, posrep['longitude'], posrep['latitude'])
        geojsonmap.add_map_point(end, end['longitude'],
                                 end['latitude'])
        geojsonmap.save_to_file(outputfile)

    def create_positions_table(self):
        """
        create a list of lists for csv file export of all the position reports

        Returns:
            positiontable(list): list of lists, each list inside
                                 is a row in the position table
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
