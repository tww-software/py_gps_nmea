"""
a window to allow the user to configure the settings for connected serial
GPS devices
"""

import tkinter


class SerialSettingsWindow(tkinter.Toplevel):
    """
    window to configure serial device settings

    Args:
        window(tkinter.Tk): the main window this spawns from
    """

    def __init__(self, window):
        tkinter.Toplevel.__init__(self, window)
        self.window = window
        self.serial_settings_group()
        self.nmea_settings_group()
        self.kml_settings_group()
        savesettingsbutton = tkinter.Button(
            self, text='Save Settings', command=self.save_settings)
        savesettingsbutton.pack()
        self.transient(self.window)

    def serial_settings_group(self):
        """
        group all the network settings within a tkinter LabelFrame
        """
        serialgroup = tkinter.LabelFrame(
            self, text="Network settings", padx=10, pady=10)
        serialgroup.pack(fill="both", expand="yes")
        devicelabel = tkinter.Label(serialgroup, text='Serial Device')
        devicelabel.pack()
        self.device = tkinter.Entry(serialgroup)
        self.device.insert(0, self.window.serialsettings['Serial Device'])
        self.device.pack()
        baudratelabel = tkinter.Label(serialgroup, text='Baud Rate')
        baudratelabel.pack()
        self.baudrate = tkinter.ttk.Combobox(serialgroup)
        self.baudrate['values'] = (
            1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200)
        self.baudrate.set(self.window.serialsettings['Baud Rate'])
        self.baudrate.pack()

    def nmea_settings_group(self):
        """
        group all the nmea settings within a tkinter LabelFrame
        """
        nmeagroup = tkinter.LabelFrame(
            self, text="NMEA logging settings", padx=20, pady=20)
        nmeagroup.pack(fill="both", expand="yes")
        loglabel = tkinter.Label(nmeagroup, text='Log NMEA Sentences')
        loglabel.pack()
        self.logpath = tkinter.Entry(nmeagroup)
        self.logpath.insert(0, self.window.serialsettings['Log File Path'])
        self.logpath.pack()
        logpathbutton = tkinter.Button(
            nmeagroup, text='Choose Log Path', command=self.set_log_path)
        logpathbutton.pack()

    def kml_settings_group(self):
        """
        group all the kml settings within a tkinter LabelFrame
        """
        kmlgroup = tkinter.LabelFrame(
            self, text="Live KML map settings", padx=20, pady=20)
        kmlgroup.pack(fill="both", expand="yes")
        kmllabel = tkinter.Label(kmlgroup, text='Ouput Live KML Map')
        kmllabel.pack()
        self.kmlpath = tkinter.Entry(kmlgroup)
        self.kmlpath.insert(0, self.window.serialsettings['KML File Path'])
        self.kmlpath.pack()
        kmlpathbutton = tkinter.Button(
            kmlgroup, text='Choose KML Path', command=self.set_kml_path)
        kmlpathbutton.pack()

    def set_log_path(self):
        """
        open a dialogue box to choose where we save NMEA sentences to
        """
        outputfile = tkinter.filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=(("nmea text file", "*.txt"),
                       ("All Files", "*.*")))
        self.logpath.insert(0, outputfile)

    def set_kml_path(self):
        """
        open a dialogue box to choose where we save KMl data to
        """
        outputfile = tkinter.filedialog.asksaveasfilename(
            defaultextension=".kml",
            filetypes=(("KML Keyhole Markup Language", "*.kml"),
                       ("All Files", "*.*")))
        self.kmlpath.insert(0, outputfile)

    def save_settings(self):
        """
        get the settings from the form
        """
        if self.window.serialread:
            tkinter.messagebox.showwarning(
                'Network Settings',
                'cannot change settings whilst reading from serial port')
        else:
            self.window.serialsettings['Serial Device'] = self.device.get()
            self.window.serialsettings['Baud Rate'] = self.baudrate.get()
            self.window.serialsettings['Log File Path'] = self.logpath.get()
            self.window.serialsettings['KML File Path'] = self.kmlpath.get()
            tkinter.messagebox.showinfo(
                'Serial Settings', 'Serial Settings Saved', parent=self)
        self.destroy()
