"""
Unit Tests for PY GPS NMEA
"""

import collections
import datetime
import unittest
import xml.etree.ElementTree

import pygpsnmea.geojson as geojson
import pygpsnmea.kml as kml
import pygpsnmea.nmea as nmea
import pygpsnmea.sentences.sentence as sentence


GNRMCSENTENCES = [
    '$GNRMC,135734.00,A,5152.423142,N,00210.276118,W,0.0,,100221,4.2,W,A*0D',
    '$GNRMC,135903.00,A,5152.386269,N,00210.303457,W,1.9,188.3,100221,4.2,W,A*2C',
    '$GNRMC,135916.00,A,5152.379876,N,00210.312674,W,2.4,270.4,100221,4.2,W,A*22',
    '$GNRMC,140004.00,A,5152.341964,N,00210.322560,W,2.0,195.8,100221,4.2,W,A*26',
    '$GNRMC,140044.00,A,5152.312863,N,00210.319179,W,1.4,130.8,100221,4.2,W,A*2E',
    '$GNRMC,140118.00,A,5152.299668,N,00210.288279,W,2.2,137.6,100221,4.2,W,A*27',
    '$GNRMC,140244.00,A,5152.252641,N,00210.212289,W,1.8,160.6,100221,4.2,W,A*26',
    '$GNRMC,140326.00,A,5152.216883,N,00210.211729,W,1.0,170.5,100221,4.2,W,A*25',
    '$GNRMC,140447.00,A,5152.186537,N,00210.276817,W,2.8,238.9,100221,4.2,W,A*26',
    '$GNRMC,140616.00,A,5152.192250,N,00210.341328,W,2.8,4.8,100221,4.2,W,A*2D',
    '$GNRMC,140620.00,A,5152.195351,N,00210.341639,W,2.2,21.0,100221,4.2,W,A*1F',
    '$GNRMC,140721.00,A,5152.227082,N,00210.332037,W,0.0,,100221,4.2,W,A*09']


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


class NMEASentenceManagerTests(unittest.TestCase):
    """
    tests for the NMEA Sentence Manager class
    """

    def setUp(self):
        self.sentencemanager = nmea.NMEASentenceManager()

    def feed_in_sentences(self):
        """
        feed in test data into the sentence manager
        """
        for gnrmc in GNRMCSENTENCES:
            self.sentencemanager.process_sentence(gnrmc)

    def test_no_suitable_last_position(self):
        """
        if there are no positions an exception should be raised
        """
        with self.assertRaises(nmea.NoSuitablePositionReport):
            self.sentencemanager.get_latest_position()

    def test_no_suitable_start_position(self):
        """
        if there are no positions an exception should be raised
        """
        with self.assertRaises(nmea.NoSuitablePositionReport):
            self.sentencemanager.get_start_position()

    def test_suitable_start_position(self):
        """
        test returning the correct start position
        """
        self.feed_in_sentences()
        start = self.sentencemanager.get_start_position()
        expected = {
            'latitude': 51.87371903333333, 'longitude': -2.1712686333333333,
            'time': '2021/02/10 13:57:34', 'speed (knots)': '0.0',
            'position no': 1}
        self.assertEqual(start, expected)

    def test_suitable_latest_position(self):
        """
        test returning the correct start position
        """
        self.feed_in_sentences()
        start = self.sentencemanager.get_latest_position()
        expected = {
            'latitude': 51.87045136666667, 'longitude': -2.1722006166666668,
            'time': '2021/02/10 14:07:21', 'speed (knots)': '0.0',
            'position no': 12}
        self.assertEqual(start, expected)

    def test_positions_table(self):
        """
        test creating a positions table ready for CSV export
        """
        expected = [
            ['latitude', 'longitude', 'time'],
            [51.87371903333333, -2.1712686333333333, '2021/02/10 13:57:34'],
            [51.87310448333333, -2.1717242833333334, '2021/02/10 13:59:03'],
            [51.87299793333333, -2.1718778999999997, '2021/02/10 13:59:16'],
            [51.87236606666667, -2.172042666666667, '2021/02/10 14:00:04'],
            [51.87188105, -2.1719863166666666, '2021/02/10 14:00:44'],
            [51.871661133333326, -2.1714713166666666, '2021/02/10 14:01:18'],
            [51.87087735, -2.1702048166666668, '2021/02/10 14:02:44'],
            [51.870281383333335, -2.170195483333333, '2021/02/10 14:03:26'],
            [51.86977561666666, -2.171280283333333, '2021/02/10 14:04:47'],
            [51.86987083333334, -2.1723554666666667, '2021/02/10 14:06:16'],
            [51.86992251666667, -2.17236065, '2021/02/10 14:06:20'],
            [51.87045136666667, -2.1722006166666668, '2021/02/10 14:07:21']]
        self.feed_in_sentences()
        postable = self.sentencemanager.create_positions_table()
        self.assertEqual(expected, postable)

    def test_clear_data(self):
        """
        test the method to clear the position data from the object
        """
        test = {}
        expected = {
            'positions before': 12,
            'positions after': 0}
        self.feed_in_sentences()
        test['positions before'] = self.sentencemanager.positioncount
        self.sentencemanager.clear_data()
        test['positions after'] = self.sentencemanager.positioncount
        self.assertEqual(test, expected)

    def test_empty_stats(self):
        """
        test stats on an empty sentence manager, only checksum errors and
        total messages should be returned and both should be 0
        """
        expected = {'total positions': 0, 'checksum errors': 0}
        test = self.sentencemanager.stats()
        self.assertEqual(expected, test)

    def test_stats(self):
        """
        test the stats method with actual NMEA data
        """
        self.feed_in_sentences()
        test = self.sentencemanager.stats()
        expected = {
            'total positions': 12, 'checksum errors': 0,
            'sentence types': collections.Counter({'$GNRMC': 12}),
            'start position': {
                'latitude': 51.87371903333333,
                'longitude': -2.1712686333333333,
                'time': '2021/02/10 13:57:34',
                'speed (knots)': '0.0',
                'position no': 1},
            'end position': {
                'latitude': 51.87045136666667,
                'longitude': -2.1722006166666668,
                'time': '2021/02/10 14:07:21',
                'speed (knots)': '0.0',
                'position no': 12},
            'duration': {
                'days': 0.0, 'hours': 0.0, 'minutes': 9.0, 'seconds': 47},
            'speeds and altitudes': {
                'maximum speed (knots)': 2.8, 'average speed (knots)': 1.708}}
        self.assertEqual(expected, test)


class MiscTests(unittest.TestCase):
    """
    misc tests that don't fit into other catagories
    """

    def test_time_duration(self):
        """
        test calculating the time duration
        """
        expected = {'days': 6.0, 'hours': 5.0, 'minutes': 49.0, 'seconds': 30}
        start = datetime.datetime(2021, 2, 14, 12, 25, 30)
        end = datetime.datetime(2021, 2, 20, 18, 15)
        duration = nmea.calculate_time_duration(start, end)
        self.assertEqual(expected, duration)

    def test_convert_to_decimal_degrees(self):
        """
        test converting latitude and longitude to decimal degrees
        """
        nmealat = '5152.227082'
        latchar = 'N'
        nmealon = '00210.332037'
        lonchar = 'W'
        result = sentence.latlon_decimaldegrees(
            nmealat, latchar, nmealon, lonchar)
        expected = (51.87045136666667, -2.1722006166666668)
        self.assertEqual(result, expected)


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


class KMLTests(unittest.TestCase):
    """
    test the generation of Keyhole Markup Language
    """

    def setUp(self):
        self.maxDiff = None
        self.parser = kml.KMLOutputParser(None)

    def test_basic_kml_doc(self):
        """
        create a very basic kml file with a folder containing a point
        """
        testcoords = [
            {'latitude': 53.81631259853631, 'longitude': -3.055718449226172},
            {'latitude': 53.81637571982642, 'longitude': -3.054978876647683},
            {'latitude': 53.81553582648765, 'longitude': -3.054681431837341},
            {'latitude': 53.81547082550122, 'longitude': -3.055649507902522},
            {'latitude': 53.81631259853631, 'longitude': -3.055718449226172}]
        self.parser.create_kml_header('test basic KML')
        self.parser.open_folder('Blackpool')
        self.parser.add_kml_placemark('Blackpool Tower',
                                      ('Blackpool tower is 158m tall and'
                                       ' was completed in 1894.'),
                                      '-3.055468', '53.815964')
        self.parser.add_kml_placemark_linestring('Perimeter', testcoords)
        self.parser.close_folder()
        self.parser.close_kml_file()
        kmldoc = xml.etree.ElementTree.fromstring(''.join(self.parser.kmldoc))
        self.assertIsInstance(kmldoc,
                              xml.etree.ElementTree.Element)

    def test_placemark_html_formatting(self):
        """
        test the formatting of dictionaries into html for the placemarks
        """
        testdict = {
            'name': 'Blackpool Tower', 'completed': '1894', 'height': '158m',
            'location': 'Blackpool, Fylde Coast, North West England'}
        testhtml = self.parser.format_kml_placemark_description(testdict)
        expectedhtml = """<![CDATA[NAME - Blackpool Tower<br  />
COMPLETED - 1894<br  />
HEIGHT - 158m<br  />
LOCATION - Blackpool, Fylde Coast, North West England<br  />
]]>"""
        self.assertEqual(testhtml, expectedhtml)

    def test_kml_invalid_chars(self):
        """
        test removal of invalid characters for KML placemarks
        """
        teststr = '"<hello world>" &\ttest\n'
        clean = kml.remove_invalid_chars(teststr)
        expected = '&quot;&lt;hello world&gt;&quot; &amp;    test'
        self.assertEqual(clean, expected)


if __name__ == '__main__':
    unittest.main()
