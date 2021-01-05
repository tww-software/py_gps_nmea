"""
manage the NMEA sentences
"""

import collections
import datetime
import statistics

import pygpsnmea.sentences.sentence
import pygpsnmea.sentences.gprmc
import pygpsnmea.sentences.gpgga
import pygpsnmea.sentences.gpgll
import pygpsnmea.sentences.gptxt


ALLSENTENCES = {
    '$GPRMC': pygpsnmea.sentences.gprmc.GPRMC,
    '$GPGGA': pygpsnmea.sentences.gpgga.GPGGA,
    '$GPGLL': pygpsnmea.sentences.gpgll.GPGLL,
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

    latlons = ('$GPRMC', '$GPGGA', '$GPGLL')
    validationchecks = ('$GPRMC', '$GPGLL', '$GPGGA')
    speeds = ('$GPRMC')
    altitudes = ('$GPGGA')
    dateandtime = ('$GPRMC')

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
            except pygpsnmea.sentences.sentence.CheckSumFailed as err:
                print(str(err))
                self.checksumerrors += 1
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
