"""
dealing with NMEA sentences from a text file
"""

import pygpsnmea.nmea as nmea


def open_file_generator(filepath):
    """
    open a file line by line using a generator

    Args:
        filepath(str): path to the file

    Yields:
        line(str): a line from the open file
    """
    with open(filepath, 'r') as infile:
        for line in infile:
            if line in ('\n', '\r\n'):
                continue
            yield line


def open_text_file(filepath):
    """
    open a text file and read NMEA sentences from it

    Args:
        filepath(str): full path to NMEA text file

    Returns:
        sentencemanager(nmea.NMEASentenceManager): object to organise the
                                                   nmea sentences
    """
    sentences = []
    sentencemanager = nmea.NMEASentenceManager()
    for line in open_file_generator(filepath):
        sentencemanager.process_sentence(line)
        sentences.append(line)
    return sentencemanager, sentences
