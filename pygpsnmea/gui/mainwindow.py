"""
A GUI for PY GPS NMEA written with tkinter
"""

import datetime
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
import pygpsnmea.kml as kml
import pygpsnmea.nmea as nmea
import pygpsnmea.serialinterface as serialinterface
import pygpsnmea.version as version

import pygpsnmea.gui.exporttab as exporttab
import pygpsnmea.gui.positionstab as positionstab
import pygpsnmea.gui.statustab as statustab
import pygpsnmea.gui.textboxtab as textboxtab
import pygpsnmea.gui.serialsettingswindow as serialsettingswindow


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
        self.statustab = statustab.StatusTab(self)
        self.add(self.statustab, text='Status')
        self.sentencestab = textboxtab.TextBoxTab(self)
        self.add(self.sentencestab, text='Sentences')
        self.positionstab = positionstab.PosRepTab(self)
        self.add(self.positionstab, text='Position Reports')
        self.exporttab = exporttab.ExportTab(self)
        self.add(self.exporttab, text='Export')


class BasicGUI(tkinter.Tk):
    """
    a basic GUI using tkinter to control the program

    Attributes:
        sentencemanager(nmea.NMEASentenceManager):deals with the NMEA sentences
        statuslabel(tkinter.Label): forms the status bar at the top of the
                                    main window
    """

    serialsettings = {'Serial Device': '',
                      'Baud Rate': 9600,
                      'Log File Path': '',
                      'KML File Path': ''}

    def __init__(self):
        tkinter.Tk.__init__(self)
        self.sentencemanager = nmea.NMEASentenceManager()
        self.protocol("WM_DELETE_WINDOW", self.quit)
        self.title('PY GPS NMEA - ' + version.VERSION)
        self.statuslabel = tkinter.Label(self, text='', bg='light grey')
        self.statuslabel.pack(fill=tkinter.X)
        self.serialread = False
        self.serialprocess = None
        self.livemap = None
        self.poscounter = 1
        self.recordedtimes = []
        self.mpq = multiprocessing.Queue()
        
        
        self.stopevent = threading.Event()
        
        
        self.updateguithread = None
        self.currentupdatethreadid = None
        
        self.tabcontrol = TabControl(self)
        self.tabcontrol.pack(expand=1, fill='both')
        self.top_menu()
        self.threadlock = threading.Lock()

    def clear_gui(self, prompt=True):
        """
        clear the gui of all data
        """
        if prompt:
            res = tkinter.messagebox.askyesno('Clearing GUI', 'Are you sure?')
        else:
            res = True
        if res:
            if self.serialread:
                tkinter.messagebox.showwarning(
                    'WARNING',
                    'Cannot clear GUI whilst reading from the serial device.')
            else:
                self.statuslabel.config(text='', bg='light grey')
                self.tabcontrol.sentencestab.clear()
                self.tabcontrol.positionstab.tree.delete(
                    *self.tabcontrol.positionstab.tree.get_children())
                self.poscounter = 1

    def serial_settings(self):
        """
        open the serial settings window
        """
        serialsettingswindow.SerialSettingsWindow(self)

    def top_menu(self):
        """
        format and add the top menu to the main window
        """
        menu = tkinter.Menu(self)
        openfileitem = tkinter.Menu(menu, tearoff=0)
        openfileitem.add_command(label='Open', command=self.open_file)
        openfileitem.add_command(label='Clear GUI', command=self.clear_gui)
        openfileitem.add_command(label='Quit', command=self.quit)
        settingsitem = tkinter.Menu(menu, tearoff=0)
        settingsitem.add_command(
            label='Serial Settings', command=self.serial_settings)
        settingsitem.add_command(
            label='Start read from serial port',
            command=self.start_serial_read)
        settingsitem.add_command(
            label='Stop read from serial port', command=self.stop_serial_read)
        helpitem = tkinter.Menu(menu, tearoff=0)
        helpitem.add_command(label='Help', command=self.help)
        helpitem.add_command(label='About', command=self.about)
        menu.add_cascade(label='File', menu=openfileitem)
        menu.add_cascade(label='Settings', menu=settingsitem)
        menu.add_cascade(label='Help', menu=helpitem)
        self.config(menu=menu)

    def about(self):
        """
        display version, licence and who created it
        """
        pass

    def help(self):
        """
        display the help window
        """
        pass

    def start_serial_read(self):
        """
        start reading from a serial device
        """
        if self.serialsettings['Serial Device'] == '':
            tkinter.messagebox.showwarning(
                'Serial Device', 'please specify a serial device to read from')
            return
        if self.serialsettings['KML File Path'] != '':
            self.livemap = kml.LiveKMLMap(self.serialsettings['KML File Path'])
            self.livemap.create_netlink_file()
        self.serialread = True
        self.stopevent.clear()
        self.updateguithread = threading.Thread(
            target=self.updategui, args=(self.stopevent,))
        self.updateguithread.setDaemon(True) 
        if not self.updateguithread.is_alive():
            self.updateguithread.start()
            self.currentupdatethreadid = self.updateguithread.ident
        self.serialprocess = multiprocessing.Process(
            target=serialinterface.mp_serial_interface,
            args=[self.mpq, self.serialsettings['Serial Device'],
                  self.serialsettings['Baud Rate']],
            kwargs={'logpath': self.serialsettings['Log File Path']})
        self.serialprocess.start()

        self.statuslabel.config(
            text='Reading NMEA sentences from {}'.format(
                self.serialsettings['Serial Device']),
            fg='black', bg='green2')

    def stop_serial_read(self):
        """
        stop reading from the serial device
        """
        self.serialread = False
        self.serialprocess.terminate()
        self.serialprocess = None
        self.stopevent.set()
        self.updateguithread.join(timeout=1)
        self.currentupdatethreadid = None
        self.updateguithread = None

        tkinter.messagebox.showinfo(
            'Serial Device', 'Stopped read from {}'.format(
                self.serialsettings['Serial Device']))
        self.statuslabel.config(text='', bg='light grey')

    def open_file(self):
        """
        pop open a file browser to allow the user to choose which NMEA 0183
        text file they want to process and then process it
        """
        if self.serialread:
            tkinter.messagebox.showwarning(
                'WARNING', 'Stop reading from the serial device first!')
        else:
            inputfile = tkinter.filedialog.askopenfilename(
                filetypes=(("NMEA 0183 text files", "*.txt *.nmea"),))
            self.clear_gui(prompt=False)
            self.statuslabel.config(
                text='Loading capture file - {}'.format(inputfile),
                fg='black', bg='gold')
            self.update_idletasks()
            self.sentencemanager = capturefile.open_text_file(inputfile)
            for ts in self.sentencemanager.positions:
                pos = self.sentencemanager.positions[ts]
                latestpos = [self.poscounter, pos['latitude'],
                             pos['longitude'], pos['time']]
                self.tabcontrol.positionstab.add_new_line(latestpos)
                self.poscounter += 1
            for sentence in self.sentencemanager.sentences:
                self.tabcontrol.sentencestab.append_text(sentence)
            self.statuslabel.config(
                text='Loaded capture file - {}'.format(inputfile),
                fg='black', bg='light grey')
            self.update_idletasks()

    def updategui(self, stopevent):
        """
        update the nmea sentence manager from the serial port

        run in another thread whist the server is running and
        get NMEA sentences from the queue and process them

        Args:
            stopevent(threading.Event): a threading stop event
        """
        while not stopevent.is_set():
            if threading.get_ident() == self.currentupdatethreadid:
                qdata = self.mpq.get()
                if qdata:
                    with self.threadlock:
                        self.tabcontrol.sentencestab.append_text(qdata)
                        self.sentencemanager.process_sentence(qdata)
                        try:
                            posrep = self.sentencemanager.get_latest_position()
                            if posrep['time'] not in self.recordedtimes:
                                self.tabcontrol.sentencestab.append_text(qdata)
                                latestpos = [
                                    self.poscounter, posrep['latitude'],
                                    posrep['longitude'], posrep['time']]
                                self.tabcontrol.positionstab.add_new_line(
                                    latestpos)
                                self.poscounter += 1
                                self.recordedtimes.append(posrep['time'])
                                if self.livemap:
                                    self.livemap.create_kml_header('live map')
                                    self.livemap.add_kml_placemark(
                                        posrep['time'], 'last known position',
                                        str(posrep['longitude']),
                                        str(posrep['latitude']))
                                    self.livemap.close_kml_file()
                                    self.livemap.write_kml_doc_file()
                            self.tabcontrol.statustab.write_stats()
                        except nmea.NoSuitablePositionReport:
                            continue

    def quit(self):
        """
        open a confirmation box asking if the user wants to quit if yes then
        stop the serial device and exit the program
        """
        res = tkinter.messagebox.askyesno('Exiting Program', 'Are you sure?')
        if res:
            if self.serialread:
                self.stop_serial_read()
            self.destroy()
