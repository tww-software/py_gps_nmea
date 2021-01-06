"""
GLL sentence

Geographic position, latitude, longitude
"""

import pygpsnmea.sentences.sentence as sentence


class GLL(sentence.NMEASentence):
    """
    GLL sentence

    0 - sentence name should be $GPGLL
    1 - latitude
    2 - north/south
    3 - longitude
    4 - east/west
    5 - UTC time hhmmss.sss
    6 - status A = data valid, V = data not valid
    """

    def __init__(self, sentencelist, errorcheck=True):
        super().__init__(sentencelist)
        self.latitude, self.longitude = \
            sentence.latlon_decimaldegrees(
                self.sentencelist[1], self.sentencelist[2],
                self.sentencelist[3], self.sentencelist[4])
        self.time = self.sentencelist[5]
        if self.sentencelist[6] == 'A':
            self.valid = True
        else:
            self.valid = False


class GPGLL(GLL):
    """
    GPS GLL sentence
    """


class GNGLL(GLL):
    """
    Global Navigation Satellite System GLL sentence
    """


class GLGLL(GLL):
    """
    GLONASS GLL sentence
    """
