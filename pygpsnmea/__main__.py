"""
command line interface for PY GPS NMEA
"""


import argparse

import pygpsnmea.gui.mainwindow as gui
import pygpsnmea.capturefile as capturefile
import pygpsnmea.export as export
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
        sentencemanager = capturefile.open_text_file(cliargs.inputfile)
        filestats = sentencemanager.stats()
        filesummary = export.create_summary_text(filestats)
        print(filesummary)
        sentencemanager.create_kml_map('test.kml')
        postable = sentencemanager.create_positions_table()
        export.write_csv_file(postable, 'test.csv')
    elif cliargs.gui:
        maingui = gui.BasicGUI()
        maingui.mainloop()


if __name__ == '__main__':
    main()
