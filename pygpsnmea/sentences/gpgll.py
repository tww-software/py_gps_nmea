"""
GPS GLL sentence

Geographic position, latitude, longitude
"""

import pygpsnmea.sentences.sentence as sentence


class GPGLL(sentence.NMEASentence):
    """
    GPS GLL sentence

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
        self.valid = self.check_validity(self.sentencelist[6])
