"""
help for PY GPS NMEA
"""

import tkinter


import pygpsnmea.gui.exporttab as exporttab
import pygpsnmea.version as version


INTRO = """
PY GPS NMEA is a program designed to read NMEA 0183 sentences from GPS serial
devices or from plain text files.
"""


STATUS = """
The status tab shows the total number of position reports received
and the number of checksum errors for the GPS receiver
or imported NMEA text file.

The Last Position Report section gives the last Latitude, Longitude and Time
of the last position received from the GPS serial device or the last postition
in the NMEA text file.
"""


POSITIONREPORTS = """
The position reports tab provides a table for all the position reports.
Positions are sorted oldest at the top and newest at the bottom.
Each position has a reference number, latitude, longitude and timestamp in UTC.
"""


EXPORTHELPLIST = []
for key, var in exporttab.EXPORTHELP.items():
    EXPORTHELPLIST.append('{} - {}'.format(key, var))
EXPORTHELP = '\n'.join(EXPORTHELPLIST)
EXPORT = """
This tab allows you to export all the positions we have from the NMEA file or
GPS serial device.

The export options are:

{}

Data cannot be exported whilst we are reading from a GPS serial device.
""".format(EXPORTHELP)


LICENCE = """

Version {}

MIT License

Copyright (c) {} Thomas W Whittam

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
""".format(version.VERSION, version.YEAR)


class HelpTab(tkinter.ttk.Frame):
    """
    tab to provide a help description

    Args:
        window(tkinter.Toplevel): the help window to attach this frame to

    Attributes:
        helpoptions(tkinter.ttk.Combobox): drop down to select help topics
        helptxt(tkinter.scrolledtext.ScrolledText): text box to display help
        
    """

    help = {'Introduction': INTRO,
            'Status Tab': STATUS,
            'Position Reports Tab': POSITIONREPORTS,
            'Export Tab': EXPORT,
            'Licence': LICENCE}

    def __init__(self, window):
        tkinter.ttk.Frame.__init__(self, window)
        self.helpoptions = tkinter.ttk.Combobox(self, state='readonly')
        self.helpoptions.pack(side='top')
        self.helptxt = tkinter.scrolledtext.ScrolledText(self)
        self.helptxt.pack(side='left', fill='both', expand=tkinter.TRUE)
        self.helpoptions['values'] = list(self.help.keys())
        self.helptxt.delete(1.0, tkinter.END)
        self.helptxt.insert(tkinter.INSERT, self.help['Introduction'])
        self.helpoptions.bind("<<ComboboxSelected>>", self.show_help)

    def show_help(self, event=None):
        """
        show help topic

        Args:
            event(tkinter.Event): event from the user changing the help
                                  combobox dropdown menu options
        """
        self.helptxt.delete(1.0, tkinter.END)
        helptopic = self.helpoptions.get()
        if helptopic != '':
            try:
                self.helptxt.insert(tkinter.INSERT, self.help[helptopic])
            except KeyError:
                tkinter.messagebox.showerror(
                    'AIS Decoder Help',
                    'no help for topic - {}'.format(helptopic))


class HelpWindow(tkinter.Toplevel):
    """
    main help window

    Args:
        window(tkinter.Tk): the main window to spawn from

    Attributes:
        window(tkinter.Tk): window to spawn from
        helpbox(HelpTab): help tab with dropdown to select help topics
    """

    def __init__(self, window):
        tkinter.Toplevel.__init__(self, window)
        self.window = window
        self.helpbox = HelpTab(self)
        self.helpbox.pack()
