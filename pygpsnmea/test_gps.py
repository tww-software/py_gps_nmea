"""
Unit Tests for PY GPS NMEA
"""

import unittest

import pygpsnmea.geojson as geojson
import pygpsnmea.kml as kml
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


class GeoJSONTests(unittest.TestCase):
    """
    tests for GEOJSON output
    """

    def setUp(self):
        self.parser = geojson.GeoJsonParser()

    def test_feature_point(self):
        """
        Tests adding a point on the map.
        """
        testinfo = {'Name': 'Blackpool Tower', 'Height(m)': 158}
        testlat = 53.815964
        testlon = -3.055468
        expected = {"type": "Feature",
                    "geometry": {"type": "Point",
                                 "coordinates": [testlon, testlat]},
                    "properties": testinfo}
        returned = self.parser.create_feature_point(testlon, testlat, testinfo)
        self.assertEqual(expected, returned)

    def test_feature_linestring(self):
        """
        Tests adding a line on the map.
        """
        positions = [
            [-4.328763333333334, 53.864983333333335],
            [-3.6327133333333332, 53.90793333333333],
            [-3.3356966666666668, 53.90606666666667]]
        testinfo = {'description': 'coords in Morcambe Bay'}
        expected = {"type": "Feature", "geometry": {"type": "LineString",
                                                    "coordinates": positions},
                    "properties": testinfo}
        returned = self.parser.create_feature_linestring(positions, testinfo)
        self.assertEqual(expected, returned)


class KMLTimingTests(unittest.TestCase):
    """
    test formatting timestamps for KML/KMZ files and other related tests
    """

    def test_suitable_timestamp(self):
        """
        test a valid timestamp in the correct format
        """
        testinput = '2020/06/02 19:03:17'
        expected = '2020-06-02T19:03:17Z'
        teststring = kml.convert_timestamp_to_kmltimestamp(testinput)
        self.assertEqual(expected, teststring)

    def test_suitable_estimated_timestamp(self):
        """
        test a valid timestamp in the correct format
        """
        testinput = '2020/07/03 00:34:17 (estimated)'
        expected = '2020-07-03T00:34:17Z'
        teststring = kml.convert_timestamp_to_kmltimestamp(testinput)
        self.assertEqual(expected, teststring)

    def test_unsuitable_timestamp_regex_fail(self):
        """
        test a timestamp that doesn't match the regex

        Note:
            change this when i come up with a better regex for datetimes
        """
        testinput = '2020-06-02 19:03:17'
        with self.assertRaises(kml.InvalidDateTimeString):
            kml.convert_timestamp_to_kmltimestamp(testinput)

    def test_unsuitable_timestamp_regex_fail_month(self):
        """
        test a timestamp with an invalid month

        Note:
            change this when i come up with a better regex for datetimes
        """
        testinput = '2020/16/06 20:34:09'
        with self.assertRaises(kml.InvalidDateTimeString):
            kml.convert_timestamp_to_kmltimestamp(testinput)

    def test_unsuitable_timestamp_regex_fail_day(self):
        """
        test a timestamp with an invalid day

        Note:
            change this when i come up with a better regex for datetimes
        """
        testinput = '2020/11/62 20:34:09'
        with self.assertRaises(kml.InvalidDateTimeString):
            kml.convert_timestamp_to_kmltimestamp(testinput)

    def test_unsuitable_timestamp_regex_fail_hour(self):
        """
        test a timestamp with an invalid hour

        Note:
            change this when i come up with a better regex for datetimes
        """
        testinput = '2020/11/30 26:34:09'
        with self.assertRaises(kml.InvalidDateTimeString):
            kml.convert_timestamp_to_kmltimestamp(testinput)

    def test_unsuitable_timestamp_regex_fail_minutes(self):
        """
        test a timestamp with an invalid minutes field

        Note:
            change this when i come up with a better regex for datetimes
        """
        testinput = '2020/11/30 17:67:09'
        with self.assertRaises(kml.InvalidDateTimeString):
            kml.convert_timestamp_to_kmltimestamp(testinput)

    def test_unsuitable_timestamp_regex_fail_seconds(self):
        """
        test a timestamp with an invalid seconds field

        Note:
            change this when i come up with a better regex for datetimes
        """
        testinput = '2020/11/30 17:02:78'
        with self.assertRaises(kml.InvalidDateTimeString):
            kml.convert_timestamp_to_kmltimestamp(testinput)


if __name__ == '__main__':
    unittest.main()
