"""
tab that displays status of the GPS receiver
"""

import tkinter

import pygpsnmea.nmea as nmea


class StatusTab(tkinter.ttk.Frame):
    """
    display GPS current position status

    Args:
        tabcontrol(tkinter.ttk.Notebook): ttk notebook to add this tab to
    """

    def __init__(self, tabcontrol):
        tkinter.ttk.Frame.__init__(self, tabcontrol)
        self.tabs = tabcontrol

        statsgroup = tkinter.LabelFrame(
            self, text="Overall Statistics", padx=10, pady=10)
        statsgroup.pack(fill="both", expand="yes")

        totalpositionslabel = tkinter.Label(
            statsgroup, text='Total Position Reports')
        totalpositionslabel.pack()
        self.totalpositions = tkinter.Label(statsgroup, text='')
        self.totalpositions.pack()
        checksumerrorslabel = tkinter.Label(
            statsgroup, text='Checksum Errors')
        checksumerrorslabel.pack()
        self.checksumerrors = tkinter.Label(statsgroup, text='')
        self.checksumerrors.pack()

        positiongroup = tkinter.LabelFrame(
            self, text="Last Known Position", padx=10, pady=10)
        positiongroup.pack(fill="both", expand="yes")
        latlabel = tkinter.Label(
            positiongroup, text='Latitude')
        latlabel.pack()
        self.latitude = tkinter.Label(positiongroup, text='')
        self.latitude.pack()
        lonlabel = tkinter.Label(
            positiongroup, text='Longitude')
        lonlabel.pack()
        self.longitude = tkinter.Label(positiongroup, text='')
        self.longitude.pack()
        timelabel = tkinter.Label(
            positiongroup, text='Time')
        timelabel.pack()
        self.time = tkinter.Label(positiongroup, text='')
        self.time.pack()

    def write_stats(self):
        """
        write the statistics from the ais and nmea trackers
        """
        self.totalpositions.configure(
            text=self.tabs.window.sentencemanager.positioncount)
        self.checksumerrors.configure(
            text=self.tabs.window.sentencemanager.checksumerrors)
        try:
            lastpos = self.tabs.window.sentencemanager.get_latest_position()
            self.latitude.configure(text=lastpos['latitude'])
            self.longitude.configure(text=lastpos['longitude'])
            self.time.configure(text=lastpos['time'])
        except nmea.NoSuitablePositionReport:
            self.latitude.configure(text='unavailable')
            self.longitude.configure(text='unavailable')
            self.time.configure(text='unavailable')

    def clear_stats(self):
        """
        clear the statistics
        """
        self.totalpositions.configure(text='')
        self.checksumerrors.configure(text='')
        self.latitude.configure(text='')
        self.longitude.configure(text='')
        self.time.configure(text='')
