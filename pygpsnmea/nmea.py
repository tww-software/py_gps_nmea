"""
manage the NMEA sentences
"""

import collections
import datetime
import statistics

import pygpsnmea.kml as kml
import pygpsnmea.sentences.sentence
import pygpsnmea.sentences.rmc
import pygpsnmea.sentences.gga
import pygpsnmea.sentences.gll
import pygpsnmea.sentences.gptxt


ALLSENTENCES = {
    '$GPRMC': pygpsnmea.sentences.rmc.GPRMC,
    '$GNRMC': pygpsnmea.sentences.rmc.GNRMC,
    '$GPGGA': pygpsnmea.sentences.gga.GPGGA,
    '$GNGGA': pygpsnmea.sentences.gga.GNGGA,
    '$GPGLL': pygpsnmea.sentences.gll.GPGLL,
    '$GNGLL': pygpsnmea.sentences.gll.GNGLL,
    '$GPTXT': pygpsnmea.sentences.gptxt.GPTXT}


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
        'days': days, 'hours': hours, 'minutes': minutes, 'seconds': seconds}
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
        avgspeed = round(statistics.fmean(speeds),  3)
        records['maximum speed (knots)'] = maxspeed
        records['average speed (knots)'] = avgspeed
    if alts:
        maxalt = round(max(alts), 3)
        minalt = round(min(alts), 3)
        altitudeclimbed = round(maxalt - minalt, 3)
        records['maximum altitude ({})'.format(altunits)] = maxalt
        records['minimum altitude ({})'.format(altunits)] = minalt
        records['altitude climbed ({})'.format(altunits)] = altitudeclimbed
    return records


class NoSuitablePositionReport(Exception):
    """
    raise when we have no position data
    """


class NMEASentenceManager():
    """
    class to keep track of all the NMEA sentences
    """

    latlons = ('$GPRMC', '$GNRMC', '$GPGGA', '$GNGGA', '$GPGLL', '$GNGLL')
    validationchecks = ('$GPRMC', '$GPGLL', '$GPGGA')
    speeds = ('$GPRMC', '$GNRMC')
    altitudes = ('$GPGGA', '$GNGGA')
    dateandtime = ('$GPRMC', '$GNRMC')

    def __init__(self):
        self.sentences = []
        self.sentencetypes = collections.Counter()
        self.positions = []
        self.datetimes = []
        self.checksumerrors = 0

    def process_sentence(self, sentence):
        """
        take an NMEA 0183 GPS sentence and process it

        Args:
            sentence(str): NMEA sentence
        """
        sentencelist = sentence.split(',')
        sentencetype = sentencelist[0]
        self.sentencetypes[sentencetype] += 1
        errorflag = False
        if sentencetype in ALLSENTENCES.keys():
            try:
                newsentence = ALLSENTENCES[sentencetype](sentencelist)
                self.sentences.append(newsentence)
                newpos = {}
                if sentencetype in self.validationchecks:
                    if not newsentence.valid:
                        errorflag = True
                if sentencetype in self.latlons:
                    newpos['latitude'] = newsentence.latitude
                    newpos['longitude'] = newsentence.longitude
                    newpos['time'] = newsentence.time
                if sentencetype in self.dateandtime:
                    self.datetimes.append(newsentence.datetime)
                if sentencetype in self.altitudes:
                    newpos['altitude'] = newsentence.altitude
                if sentencetype in self.speeds:
                    newpos['speed (knots)'] = newsentence.speed
            except (pygpsnmea.sentences.sentence.CheckSumFailed) as err:
                self.checksumerrors += 1
                errorflag = True
            except ValueError:
                errorflag = True
            if not errorflag and sentencetype in self.latlons:
                self.positions.append(newpos)

    def get_latest_position(self):
        """
        return the last known position we have

        Raises:
            NoSuitablePositionReport: if no position found

        Returns:
            self.positions(dict): last item in self.positions
        """
        try:
            return self.positions[len(self.positions) - 1]
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
            return self.positions[0]
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
            self.positions)
        return stats
        
    def create_kml_map(self, outputfile):
        """
        create a kml map from all the positions we have
        """
        try:
            start = self.get_start_position()
            end = self.get_latest_position()
        except NoSuitablePositionReport:
            print('unable to make KML map')
            return
        kmlmap = kml.KMLOutputParser(outputfile)
        kmlmap.create_kml_header('test')
        kmlmap.add_kml_placemark('start', 'starting position', str(start['longitude']), str(start['latitude']))
        kmlmap.add_kml_placemark_linestring('linestring', self.positions)    
        kmlmap.add_kml_placemark('end', 'ending position', str(end['longitude']), str(end['latitude']))
        kmlmap.close_kml_file()
        kmlmap.write_kml_doc_file()
            
