"""
helper module to keep track of all the sentences we have
"""

import pygpsnmea.sentences.sentence
import pygpsnmea.sentences.rmc
import pygpsnmea.sentences.gga
import pygpsnmea.sentences.gll


ALLSENTENCES = {
    '$GPRMC': pygpsnmea.sentences.rmc.GPRMC,
    '$GNRMC': pygpsnmea.sentences.rmc.GNRMC,
    '$GLRMC': pygpsnmea.sentences.rmc.GLRMC,
    '$GPGGA': pygpsnmea.sentences.gga.GPGGA,
    '$GNGGA': pygpsnmea.sentences.gga.GNGGA,
    '$GLGGA': pygpsnmea.sentences.gga.GLGGA,
    '$GPGLL': pygpsnmea.sentences.gll.GPGLL,
    '$GNGLL': pygpsnmea.sentences.gll.GNGLL,
    '$GLGLL': pygpsnmea.sentences.gll.GLGLL}


LATLONTIME = ('$GPRMC', '$GNRMC', '$GPGGA', '$GNGGA', '$GPGLL', '$GNGLL')
VALIDATIONCHECKS = ('$GPRMC', '$GNRMC', '$GPGGA', '$GNGGA', '$GPGLL', '$GNGLL')
SPEEDS = ('$GPRMC', '$GNRMC')
ALTITUDES = ('$GPGGA', '$GNGGA')
DATE = ('$GPRMC', '$GNRMC')
DATETIME = ('$GPRMC', '$GNRMC')
FIXQUALITY = ('$GPGGA', '$GNGGA')
SATELLITESTRACKED = ('$GPGGA', '$GNGGA')
