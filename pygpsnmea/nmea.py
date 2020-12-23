"""
manage the NMEA sentences
"""


import pygpsnmea.sentences.sentence
import pygpsnmea.sentences.gprmc
import pygpsnmea.sentences.gpgga


ALLSENTENCES = {
    '$GPRMC': pygpsnmea.sentences.gprmc.GPRMC,
    '$GPGGA': pygpsnmea.sentences.gpgga.GPGGA}


class NoSuitablePositionReport(Exception):
    """
    raise when we have no position data
    """


class NMEASentenceManager():
    """
    class to keep track of all the NMEA sentences
    """
    
    latlons = ('$GPRMC', '$GPGGA')

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
        if sentencetype in ALLSENTENCES.keys():
            try:
                newsentence = ALLSENTENCES[sentencetype](sentencelist)
            except pygpsnmea.sentences.sentence.CheckSumFailed as err:
                print(str(err))
                self.checksumerrors += 1
            self.sentencelist.append(newsentence)
            newpos = {}
            if sentencetype in self.latlons:
                newpos['latitude'] = newsentence.latitude
                newpos['longitude'] = newsentence.longitude
                newpos['time'] = newsentence.time

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
