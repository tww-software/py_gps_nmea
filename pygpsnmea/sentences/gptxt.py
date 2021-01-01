"""
GPS TXT sentence

"""

import datetime

import pygpsnmea.sentences.sentence as sentence


class GPTXT(sentence.NMEASentence):
    """
    GPS TXT sentence

    plain ASCII text
    """

