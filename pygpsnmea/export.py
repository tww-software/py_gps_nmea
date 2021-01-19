"""
code for exporting to different formats
"""

import csv
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


def write_csv_file(lines, outpath, dialect='excel'):
    """
    write out the details to a csv file

    Note:
        default dialect is 'excel' to create a CSV file
        we change this to 'excel-tab' for TSV output

    Args:
        lines(list): list of lines to write out to the csv, each line is a list
        outpath(str): full path to write the csv file to
        dialect(str): type of seperated values file we are creating
    """
    with open(outpath, 'w') as outfile:
        csvwriter = csv.writer(outfile, dialect=dialect)
        csvwriter.writerows(lines)

def write_text_file(text, outpath):
    """
    write out text to a file
    
    Args:
        text(str): text to write out to a file
        outpath(str): path to write to
    """
    with open(outpath, 'w') as outfile:
        outfile.write(text)
