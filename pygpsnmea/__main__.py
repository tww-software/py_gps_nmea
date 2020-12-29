"""
command line interface for PY GPS NMEA
"""


import argparse

import pygpsnmea.capturefile as capturefile
import pygpsnmea.version as version


def cli_arg_parser():
    """
    get the cli arguments and run the program

    Returns:
        parser(argparse.ArgumentParser): the command line options parser
    """
    desc = 'tool to decode GPS nmea sentences'
    versiontxt = 'pygpsnmea version = {}'.format(version.VERSION)
    parser = argparse.ArgumentParser(description=desc, epilog=versiontxt)
    gpsoptions = parser.add_mutually_exclusive_group()
    gpsoptions.add_argument('-i', help='input file path', dest='inputfile')
    gpsoptions.add_argument('--gui', action='store_true', help='open the GUI')
    return parser


def main():
    """
    get the command line arguments and decide what to run
    """
    cliparser = cli_arg_parser()
    cliargs = cliparser.parse_args()
    if cliargs.inputfile:
        capturefile.open_text_file(cliargs.inputfile)


if __name__ == '__main__':
    main()
