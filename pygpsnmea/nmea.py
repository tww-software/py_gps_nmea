"""
manage the NMEA sentences
"""

import datetime

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
    """
    timediff = end - start
    totalseconds = timediff.total_seconds()
    days, remainder = divmod(totalseconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    duration = {
        'days': days, 'hours': hours, 'minutes': minutes, 'seconds': seconds}
    return duration


class NoSuitablePositionReport(Exception):
    """
    raise when we have no position data
    """


class NMEASentenceManager():
    """
    class to keep track of all the NMEA sentences
    """

    latlons = ('$GPRMC', '$GPGGA', '$GPGLL')

    def __init__(self):
        self.sentences = []
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
        errorflag = False
        if sentencetype in ALLSENTENCES.keys():
            try:
                newsentence = ALLSENTENCES[sentencetype](sentencelist)
                self.sentences.append(newsentence)
                newpos = {}
                if sentencetype in ('$GPRMC', '$GPGLL'):
                    if not newsentence.valid:
                        errorflag = True
                if sentencetype in self.latlons:
                    newpos['latitude'] = newsentence.latitude
                    newpos['longitude'] = newsentence.longitude
                    newpos['time'] = newsentence.time
                    if sentencetype == '$GPRMC':
                        self.datetimes.append(newsentence.datetime)
            except pygpsnmea.sentences.sentence.CheckSumFailed as err:
                print(str(err))
                self.checksumerrors += 1
                errorflag = True
            if not errorflag:
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
        """
        stats = {}
        stats['total sentences'] = len(self.sentences)
        stats['total positions'] = len(self.positions)
        try:
            firstpos = self.get_start_position()
            lastpos = self.get_latest_position()
        except NoSuitablePositionReport:
            return stats
        stats['start position'] = firstpos
        stats['end position'] = lastpos
        stats['checksum errors'] = self.checksumerrors
        stats['duration'] = calculate_time_duration(
            self.datetimes[0], self.datetimes[len(self.datetimes) - 1])
        return stats
