"""
contains the base class for all NMEA sentences
"""


def latlon_decimaldegrees(nmealat, latchar, nmealon, lonchar):
    """
    Converts the nmea lat & lon into decimal degrees

    Note:
        West (of prime meridian) longitude as negative
        East (of prime meridian) longitude as positive
        North (of the equator) latitude is positive
        South (of the equator) latitude is negative

    Args:
        nmealat(str): latitude
        latchar(str): N or S
        nmealon(str): longitude
        lonchar(str): E or W

    Returns:
        latdeg(float): the latitude in decimal degrees
        londeg(float): the longitude in decimal degrees
    """
    nmealon = float(nmealon)
    nmealat = float(nmealat)
    londegwhole = int(nmealon/100)
    londecdeg = (nmealon - londegwhole * 100)/60
    londeg = londegwhole + londecdeg
    if lonchar == 'W':
        londeg = (-1)*londeg
    latdegwhole = int(nmealat/100)
    latdecdeg = (nmealat - latdegwhole * 100)/60
    latdeg = latdegwhole + latdecdeg
    if latchar == 'S':
        latdeg = (-1)*latdeg
    return latdeg, londeg


def calculate_nmea_checksum(sentence, start='$', seperator=','):
    """
    XOR each char with the last, compare the last 2 characters
    with the computed checksum

    Args:
        sentence(str): the ais sentence as a string
        start(str): the start of the sentence default = $
        separator(str): character that separates the parts of the nmea sentence
                        default = ,

    Returns:
        True: if calculated checksum = checksum at the end of the sentence
        False: if checksums do not match
    """
    try:
        sentencelist = sentence.rstrip().split(seperator)
        csum = hex(int(sentencelist[len(sentencelist) - 1].split('*')[1], 16))
        start = sentence.find(start) + 1
        end = sentence.find('*')
        data = sentence[start:end]
        chksum = 0
        for char in data:
            chksum ^= ord(char)
        chksum = hex(int(chksum))
    except IndexError:
        return False
    return bool(csum == chksum)


class CheckSumFailed(Exception):
    """
    raise if the checksum calculation fails
    """


class NMEASentence():
    """
    the base class for NMEA sentences

    Args:
        sentencelist(list): the NMEA sentence parts as a list
        errorcheck(bool): if set to true, the checksum will be calculated to
                          ensure the sentence is correctly formed
                          default is True
    """

    def __init__(self, sentencelist, errorcheck=True):
        self.sentencelist = sentencelist
        nmeatext = ','.join(sentencelist)
        self.type = self.sentencelist[0]
        if errorcheck:
            self.checksumok = calculate_nmea_checksum(nmeatext)
            if not self.checksumok:
                raise CheckSumFailed(
                    'nmea sentence checksum failed - {}'.format(
                        ','.join(self.sentencelist)))
