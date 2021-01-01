"""
code for exporting to different formats
"""

import json
import re


def create_summary_text(summary):
    """
    format a dictionary so it can be printed to screen or written to a plain
    text file

    Args:
        summary(dict): the data to format

    Returns:
        textsummary(str): the summary dict formatted as a string
    """
    summaryjson = json.dumps(summary, indent=3)
    textsummary = re.sub('[{},"]', '', summaryjson)
    return textsummary
