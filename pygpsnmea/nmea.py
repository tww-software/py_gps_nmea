"""
manage the NMEA sentences
"""


import pygpsnmea.sentences.sentence
import pygpsnmea.sentences.gprmc
import pygpsnmea.sentences.gpgga
import pygpsnmea.sentences.gpgll


ALLSENTENCES = {
    '$GPRMC': pygpsnmea.sentences.gprmc.GPRMC,
    '$GPGGA': pygpsnmea.sentences.gpgga.GPGGA,
    '$GPGLL': pygpsnmea.sentences.gpgll.GPGLL}


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

    def stats(self):
        """
        return stats from this NMEA manager
        """
        stats = {}
        stats['total sentences'] = len(self.sentences)
        stats['total positions'] = len(self.positions)
        stats['start time'] = self.positions[0]['time']
        stats['end time'] = self.positions[len(self.positions) - 1]['time']
        stats['checksum errors'] = self.checksumerrors
        return stats
