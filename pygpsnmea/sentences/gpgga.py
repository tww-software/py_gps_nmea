"""
GPS GGA sentence

Global Positioning System Fix Data
provides Lat/Lon, height above sea level and time
"""

import pygpsnmea.sentences.sentence as sentence


class GPGGA(sentence.NMEASentence):
    """
    GPS GGA sentence

    $GPGGA
    0 - sentence name should be $GPGGA
    1 - time in format hhmmss.microseconds
    2 - latitude
    3 - latitude compass
    4 - longitude
    5 - longitude compass
    6 - fix quality (1 means gps)
    7 - no of satellites tracked
    8 - horizontal dilution of position
    9 - height above sea level
    10 - height unit (M for metres)
    11 - height of geoid (mean sea level) above WGS84 ellipsoid
    """

    def __init__(self, sentencelist, errorcheck=True)
        super().__init__(self, sentencelist, errorcheck=True)
        self.latitude, self.longitude = \
            sentence.latlon_decimaldegrees(
                self.sentencelist[2], self.sentencelist[3],
                self.sentencelist[4], self.sentencelist[5])
        self.time = self.sentencelist[1]

