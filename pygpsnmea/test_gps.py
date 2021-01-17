"""
Unit Tests for PY GPS NMEA
"""

import unittest


import pygpsnmea.sentences.sentence as sentence


class NMEASentenceTests(unittest.TestCase):
    """
    tests related to the interpretation of GPS NMEA 0183 sentences
    """


    def test_correct_nmea_checksum(self):
        """
        feed in an NMEA 0183 sentence and calculate its checksum
        checksum should be correct and True
        """
        testsentence = ('$GPRMC,152904.000,A,4611.1699,N,00117.8182,'
                        'W,000.00,0.0,240714,,,E*46')
        self.assertTrue(sentence.calculate_nmea_checksum(testsentence))

    def test_incorrect_nmea_checksum(self):
        """
        feed in an NMEA 0183 sentence and calculate its checksum
        checksum should be incorrect and False
        """
        testsentence = ('$GPRMC,152904.000,A,4611.1699,N,00117.8182,'
                        'W,000.00,0.0,240714,,,E*48')
        self.assertFalse(sentence.calculate_nmea_checksum(testsentence))

    def test_incomplete_sentence(self):
        """
        feed in an incomplete NMEA sentence with no checksum
        should return False as we are unable to calculate the checksum as there
        isn't one!
        """
        testsentence = '$GPRMC,165629.00,V,,'
        self.assertFalse(sentence.calculate_nmea_checksum(testsentence))


class MiscTests(unittest.TestCase):
    """
    misc tests that don't fit into other catagories
    """

if __name__ == '__main__':
    unittest.main()
