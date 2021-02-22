"""
a parser to generate Keyhole Markup Language (KML) for Google Earth
"""

import datetime
import os
import re


DATETIMEREGEX = re.compile(
    r'\d{4}/(0[1-9]|1[0-2])/(0[1-9]|1[0-9]|2[0-9]|3[01]) '
    r'(0[0-9]|1[0-9]|2[0-3]):([0-5][0-9]):([0-5][0-9])')


class KMLOutputParser():
    """
    Class to parse KML into an output file.

    Attributes:
        kmldoc(list): list of strings to make up the doc.kml
        kmlfilepath(str): path to output KML file
        kmlheader(str): first part of a KML file
        placemarktemplate(str): template for a KML placemark (pin on map)
        lineplacemarktemplate(str): template for KML linestring (line on map)
    """
    def __init__(self, kmlfilepath):
        self.kmldoc = []
        self.kmlfilepath = kmlfilepath
        self.kmlheader = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
<Document>
<name>%s</name>
<open>1</open>"""
        self.placemarktemplate = """
<Placemark>
<name>%s</name>
<description>%s</description>
<TimeStamp>
<when>%s</when>
</TimeStamp>
<LookAt>
<longitude>%s</longitude>
<latitude>%s</latitude>
<altitude>%s</altitude>
<heading>-0</heading>
<tilt>0</tilt>
<range>500</range>
</LookAt>
<Point>
<coordinates>%s</coordinates>
</Point>
</Placemark>"""
        self.lineplacemarktemplate = """
<Placemark>
<name>%s</name>
<LineString>
<coordinates>%s</coordinates>
</LineString>
</Placemark>"""

    @staticmethod
    def format_kml_placemark_description(placemarkdict):
        """
        format html tags for inside a kml placemark from a dictionary

        Args:
            placemarkdict(dict): dictionary of information for a placemark

        Returns:
            description(str): the dictionary items formatted as HTML string
                              suitable to be in a KML placemark description
        """
        starttag = "<![CDATA["
        newlinetag = "<br  />\n"
        endtag = "]]>"
        descriptionlist = []
        descriptionlist.append(starttag)
        for item in placemarkdict:
            if isinstance(placemarkdict[item], dict):
                descriptionlist.append(newlinetag)
                descriptionlist.append(item.upper())
                descriptionlist.append(newlinetag)
                for subitem in placemarkdict[item]:
                    descriptionlist.append(str(subitem).upper())
                    descriptionlist.append(' - ')
                    descriptionlist.append(str(placemarkdict[item][subitem]))
                    descriptionlist.append(newlinetag)
                continue
            descriptionlist.append(str(item).upper())
            descriptionlist.append(' - ')
            descriptionlist.append(str(placemarkdict[item]))
            descriptionlist.append(newlinetag)
        descriptionlist.append(endtag)
        description = ''.join(descriptionlist)
        return description

    def create_kml_header(self, name):
        """
        Write the first part of the KML output file.
        This only needs to be called once at the start of the kml file.

        Args:
            name(str): name to use for this kml document
        """
        self.kmldoc.append(self.kmlheader % (name))

    def add_kml_placemark(self, placemarkname, description, lon, lat,
                          altitude='0', timestamp=''):
        """
        Write a placemark to the KML file (a pin on the map!)

        Args:
            placemarkname(str): text that appears next to the pin on the map
            description(str): text that will appear in the placemark
            lon(str): longitude in decimal degrees
            lat(str): latitude in decimal degrees
            altitude(str): altitude in metres
            timestamp(str): time stamp in XML format
        """
        placemarkname = remove_invalid_chars(placemarkname)
        coords = lon + ',' + lat + ',' + altitude
        placemark = self.placemarktemplate % (
            placemarkname, description, timestamp, lon, lat,
            altitude, coords)
        self.kmldoc.append(placemark)

    def open_folder(self, foldername):
        """
        open a folder to store placemarks

        Args:
            foldername(str): the name of the folder
        """
        cleanfoldername = remove_invalid_chars(foldername)
        openfolderstr = "<Folder>\n<name>{}</name>".format(cleanfoldername)
        self.kmldoc.append(openfolderstr)

    def close_folder(self):
        """
        close the currently open folder
        """
        closefolderstr = "</Folder>"
        self.kmldoc.append(closefolderstr)

    def add_kml_placemark_linestring(self, placemarkname, coords):
        """
        Write a linestring to the KML file (a line on the map!)

        Args:
            placemarkname(str): name of the linestring
            coords(list): list of dicts containing Lat/Lon
        """
        placemarkname = remove_invalid_chars(placemarkname)
        newcoordslist = []
        for item in coords:
            lon = str(item['longitude'])
            lat = str(item['latitude'])
            try:
                alt = str(item['altitude (M)'])
            except KeyError:
                alt = '0'
            coordsline = '{},{},{}'.format(lon, lat, alt)
            newcoordslist.append(coordsline)
        placemark = self.lineplacemarktemplate % (placemarkname,
                                                  '\n'.join(newcoordslist))
        self.kmldoc.append(placemark)

    def close_kml_file(self):
        """
        Write the end of the KML file.
        This needs to be called once at the end of the file
        to ensure the tags are closed properly.
        """
        endtags = "\n</Document></kml>"
        self.kmldoc.append(endtags)

    def write_kml_doc_file(self):
        """
        write the tags to the kml doc.kml file
        """
        with open(self.kmlfilepath, 'w') as kmlout:
            for kmltags in self.kmldoc:
                kmlout.write(kmltags)
            kmlout.flush()


class LiveKMLMap(KMLOutputParser):
    """
    live plot positions on a map
    """

    kmlnetlink = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
    <NetworkLink>
      <name>Live GPS Positon</name>
      <description>current GPS position</description>
      <Link>
        <href>{}</href>
        <refreshVisibility>1</refreshVisibility>
        <refreshMode>onInterval</refreshMode>
        <refreshInterval>1</refreshInterval>
      </Link>
    </NetworkLink>
</kml>"""

    def __init__(self, kmlfilepath):
        super().__init__(kmlfilepath)
        outputpath = os.path.dirname(kmlfilepath)
        self.netlinkpath = os.path.join(outputpath, 'open_this.kml')

    def create_netlink_file(self):
        """
        write the netlink file
        """
        with open(os.path.join(self.netlinkpath), 'w') as netlinkfile:
            netlinkfile.write(self.kmlnetlink.format(self.kmlfilepath))


class InvalidDateTimeString(Exception):
    """
    raise if timestamp is the wrong format
    """


def remove_invalid_chars(xmlstring):
    """
    remove invalid chars from a string

    Args:
        xmlstring(str): input string to clean

    Returns:
        cleanstring(str): return string with invalid chars replaced or removed
    """
    invalidchars = {'<': '&lt;', '>': '&gt;', '"': '&quot;',
                    '\t': '    ', '\n': ''}
    cleanstring = xmlstring.replace('&', '&amp;')
    for invalidchar in invalidchars:
        cleanstring = cleanstring.replace(
            invalidchar, invalidchars[invalidchar])
    return cleanstring


def convert_timestamp_to_kmltimestamp(timestamp):
    """
    convert the pygps timestamp string to one suitable for KML

    Args:
        timestamp(str): the timestamp string in the format '%Y/%m/%d %H:%M:%S'

    Raises:
        InvalidDateTimeString: when the timestamp is not correctly formatted

    Returns:
        xmltimestamp(str): the timestamp in the format '%Y-%m-%dT%H:%M:%SZ'
    """
    if DATETIMEREGEX.match(timestamp):
        if timestamp.endswith(' (estimated)'):
            timestamp = timestamp.rstrip(' (estimated)')
        try:
            dtobj = datetime.datetime.strptime(timestamp, '%Y/%m/%d %H:%M:%S')
            kmltimestamp = dtobj.strftime('%Y-%m-%dT%H:%M:%SZ')
        except ValueError as err:
            raise InvalidDateTimeString('wrong') from err
        return kmltimestamp
    raise InvalidDateTimeString('timestamp must be %Y/%m/%d %H:%M:%S')
