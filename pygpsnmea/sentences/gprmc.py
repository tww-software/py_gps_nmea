"""
GPS RMC sentence

Recommended minimum GPS data
provides Lat/Lon, Speed in knots, time and date
"""

import datetime

import pygpsnmea.sentences.sentence as sentence


class GPRMC(sentence.NMEASentence):
    """
    GPS RMC sentence

    $GPRMC
    0 - sentence name should be $GPRMC
    1 - time in format hhmmss.microseconds
    2 - status (A data valid, V data invalid)
    3 - latitude
    4 - latitude compass
    5 - longitude
    6 - longitude compass
    7 - speed in knots
    8 - course over ground
    9 - date in ddmmyy
    10 - magnetic notation
    11 - mode
    12 - checksum
    """

    def __init__(self, sentencelist, errorcheck=True):
        super().__init__(sentencelist)
        self.latitude, self.longitude = \
            sentence.latlon_decimaldegrees(
                self.sentencelist[3], self.sentencelist[4],
                self.sentencelist[5], self.sentencelist[6])
        self.time = self.sentencelist[1]
        self.date = self.sentencelist[9]
        self.datetime = datetime.datetime.strptime(
            '{} {}'.format(self.time, self.date), '%H%M%S.%f %d%m%y')
        self.valid = self.check_validity(self.sentencelist[2])
        self.speed = self.sentencelist[7]
        self.cog = self.sentencelist[8]
