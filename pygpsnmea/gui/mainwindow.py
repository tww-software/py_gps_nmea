"""
A GUI for PY GPS NMEA written with tkinter
"""

import datetime
import logging
import multiprocessing
import threading
import time
import tkinter
import tkinter.filedialog
import tkinter.messagebox
import tkinter.scrolledtext
import tkinter.ttk

import pygpsnmea.capturefile as capturefile
import pygpsnmea.export as export
import pygpsnmea.nmea as nmea
import pygpsnmea.version as version

import pygpsnmea.gui.statstab as statstab
import pygpsnmea.gui.sentencestab as sentencestab
import pygpsnmea.gui.positionstab as positionstab


class TabControl(tkinter.ttk.Notebook):
    """
    organise the main tabs

    Note:
        tabs go from left to right

    Args:
        window(tkinter.Tk): the main window this spawns from
    """

    def __init__(self, window):
        tkinter.ttk.Notebook.__init__(self, window)
        self.window = window
        self.statstab = statstab.StatsTab(self)
        self.add(self.statstab, text='Stats')
        self.sentencestab = sentencestab.TextBoxTab(self)
        self.add(self.sentencestab, text='Sentences')
        self.positionstab = positionstab.PosRepTab(self)
        self.add(self.positionstab, text='Position Reports')

class BasicGUI(tkinter.Tk):
    """
    a basic GUI using tkinter to control the program

    Attributes:
        sentencemanager(nmea.NMEASentenceManager):deals with the NMEA sentences
        statuslabel(tkinter.Label): forms the status bar at the top of the
                                    main window
        
    """

    def __init__(self):
        tkinter.Tk.__init__(self)
        self.sentencemanager = nmea.NMEASentenceManager()
        self.protocol("WM_DELETE_WINDOW", self.quit)
        self.title('PY GPS NMEA - ' + version.VERSION)
        self.statuslabel = tkinter.Label(self, text='', bg='light grey')
        self.statuslabel.pack(fill=tkinter.X)
        self.tabcontrol = TabControl(self)
        self.tabcontrol.pack(expand=1, fill='both')
        self.top_menu()

    def clear_gui(self, prompt=True):
        """
        clear the gui of all data
        """
        if prompt:
            res = tkinter.messagebox.askyesno('Clearing GUI', 'Are you sure?')
        else:
            res = True
        if res:
            self.statuslabel.config(text='', bg='light grey')
            self.tabcontrol.sentencestab.clear()
            self.tabcontrol.statstab.statsbox.delete(1.0, tkinter.END)
            self.tabcontrol.positionstab.tree.delete(
                    *self.tabcontrol.positionstab.tree.get_children())

    def top_menu(self):
        """
        format and add the top menu to the main window
        """
        menu = tkinter.Menu(self)
        openfileitem = tkinter.Menu(menu, tearoff=0)
        openfileitem.add_command(label='Open', command=self.open_file)
        openfileitem.add_command(label='Clear GUI', command=self.clear_gui)
        openfileitem.add_command(label='Quit', command=self.quit)
        menu.add_cascade(label='File', menu=openfileitem)
        helpitem = tkinter.Menu(menu, tearoff=0)
        helpitem.add_command(label='Help', command=self.help)
        helpitem.add_command(label='About', command=self.about)
        menu.add_cascade(label='Help', menu=helpitem)
        self.config(menu=menu)

    def about(self):
        """
        display version, licence and who created it
        """
        messagewindow = aismessagetab.MessageWindow(self)
        messagewindow.msgdetailsbox.append_text(guihelp.LICENCE)

    def help(self):
        """
        display the help window
        """
        guihelp.HelpWindow(self)

    def open_file(self):
        """
        pop open a file browser to allow the user to choose which NMEA 0183
        text file they want to process and then process it
        """
        inputfile = tkinter.filedialog.askopenfilename()
        self.clear_gui(prompt=False)
        filetypes=(("NMEA 0183 text files", "*.txt *.nmea"))
        self.statuslabel.config(
            text='Loading capture file - {}'.format(inputfile),
            fg='black', bg='gold')
        self.update_idletasks() 
        self.sentencemanager = capturefile.open_text_file(inputfile)
        poscounter = 1
        for pos in self.sentencemanager.positions:
            latestpos = [poscounter, pos['latitude'],
                         pos['longitude'], pos['time']]
            self.tabcontrol.positionstab.add_new_line(latestpos)
            poscounter += 1
        for sentence in self.sentencemanager.sentences:
            self.tabcontrol.sentencestab.append_text(sentence)
        filestats = self.sentencemanager.stats()
        printablestats = export.create_summary_text(filestats)
        self.tabcontrol.statstab.statsbox.insert(
            tkinter.INSERT, printablestats)
        self.statuslabel.config(
            text='Loaded capture file - {}'.format(inputfile),
            fg='black', bg='light grey')
        self.update_idletasks() 

    def quit(self):
        """
        open a confirmation box asking if the user wants to quit if yes then
        stop the server and exit the program
        """
        res = tkinter.messagebox.askyesno('Exiting Program', 'Are you sure?')
        if res:
            self.destroy()
