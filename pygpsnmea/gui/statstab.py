"""
tab that displays overall stats about the stations received
"""

import tkinter


class StatsTab(tkinter.ttk.Frame):
    """
    provide overall statistics for all the AIS Stations we can see

    Args:
        tabcontrol(tkinter.ttk.Notebook): ttk notebook to add this tab to
    """
    
    def __init__(self, tabcontrol):
        tkinter.ttk.Frame.__init__(self, tabcontrol)
        self.statsbox = tkinter.scrolledtext.ScrolledText(self)
        self.statsbox.pack(side='left', fill='both', expand=tkinter.TRUE)
