"""
tab to allow the user to export data in different formats
"""

import tkinter

import pygpsnmea.export as export


EXPORTHELP = {
    'CSV': ('Comma Separated Values file containing latitudes, longitudes and'
            'timestamps'),
    'TSV': ('Tab Separated Values file containing latitudes, longitudes and'
            'timestamps'),
    'KML':  'KML map of all the positions',
    'GEOJSON': 'GEOJSON map of all the positions',
    'JSON LINES': 'line delimited JSON output of all positions',
    'NMEA': 'NMEA sentences - content of the sentences tab'}


class ExportAborted(Exception):
    """
    raise if we cancel an export operation
    """


class ExportTab(tkinter.ttk.Frame):
    """
    the tab in the main window that contains the export file options

    Args:
        tabcontrol(tkinter.ttk.Notebook): ttk notebook to add this tab to
    """

    def __init__(self, tabcontrol):
        tkinter.ttk.Frame.__init__(self, tabcontrol)
        self.tabs = tabcontrol
        self.exportoptions = tkinter.ttk.Combobox(self, state='readonly')
        self.orderby = tkinter.ttk.Combobox(self, state='readonly')
        self.exporthelplabel = tkinter.Label(self)
        self.export_options()
        self.exportoptions.bind("<<ComboboxSelected>>", self.show_export_help)
        self.show_export_help()

    def export_options(self):
        """
        populate the export options drop down menu with file export options
        and add an export button next to it
        """
        self.exportoptions['values'] = (
            'CSV', 'TSV', 'KML', 'GEOJSON', 'JSON LINES', 'NMEA')
        self.exportoptions.set('KML')
        self.exportoptions.grid(column=1, row=1)
        self.exporthelplabel.grid(column=2, row=1)
        exportbutton = tkinter.Button(self, text='Export',
                                      command=self.export_files)
        exportbutton.grid(column=1, row=4)

    def export_files(self):
        """
        choose which export command to run from the exportoptions drop down
        in the Export tab
        """
        if self.tabs.window.serialread:
            tkinter.messagebox.showwarning(
                'WARNING',
                'Cannot export files whilst reading from serial interface')
        elif len(self.tabs.window.sentencemanager.positions) == 0:
            tkinter.messagebox.showwarning(
                'WARNING', 'No positions to export.')
        else:
            commands = {
                'CSV': self.export_csv,
                'TSV': self.export_tsv,
                'KML': self.export_kml,
                'GEOJSON': self.export_geojson,
                'JSON LINES': self.export_jsonlines,
                'NMEA': self.export_nmea}
            option = self.exportoptions.get()
            try:
                commands[option]()
                tkinter.messagebox.showinfo(
                    'Export Files', 'Export Successful')
            except Exception as err:
                tkinter.messagebox.showerror(type(err).__name__, str(err))

    def show_export_help(self, event=None):
        """
        Display help text for each export option as the user selects each one

        Args:
            event(tkinter.Event): event from the user changing the export
                                  combobox dropdown menu options
        """
        option = self.exportoptions.get()
        helptext = EXPORTHELP[option]
        self.exporthelplabel.configure(text=helptext)

    def export_csv(self):
        """
        pop open a file browser to allow the user to choose where to save the
        file and then save file to that location

        Raises:
            ExportAborted: if the user clicks cancel
        """
        outputfile = tkinter.filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=(("comma seperated values", "*.csv"),
                       ("All Files", "*.*")))
        if outputfile:
            tabledata = \
                self.tabs.window.sentencemanager.create_positions_table()
            export.write_csv_file(tabledata, outputfile)
        else:
            raise ExportAborted('Export cancelled by user.')

    def export_tsv(self):
        """
        pop open a file browser to allow the user to choose where to save the
        file and then save file to that location

        Raises:
            ExportAborted: if the user clicks cancel
        """
        outputfile = tkinter.filedialog.asksaveasfilename(
            defaultextension=".tsv",
            filetypes=(("tab seperated values", "*.tsv"),
                       ("All Files", "*.*")))
        if outputfile:
            tabledata = \
                self.tabs.window.sentencemanager.create_positions_table()
            export.write_csv_file(tabledata, outputfile, dialect='excel-tab')
        else:
            raise ExportAborted('Export cancelled by user.')

    def export_kml(self):
        """
        pop open a file browser to allow the user to choose where to save the
        file and then save file to that location

        Raises:
            ExportAborted: if the user clicks cancel
        """
        outputfile = tkinter.filedialog.asksaveasfilename(
            defaultextension=".kml",
            filetypes=(("keyhole markup language", "*.kml"),
                       ("All Files", "*.*")))
        if outputfile:
            self.tabs.window.sentencemanager.create_kml_map(
                outputfile)
        else:
            raise ExportAborted('Export cancelled by user.')

    def export_geojson(self):
        """
        pop open a file browser to allow the user to choose where to save the
        file and then save file to that location

        Raises:
            ExportAborted: if the user clicks cancel
        """
        outputfile = tkinter.filedialog.asksaveasfilename(
            defaultextension=".geojson",
            filetypes=(("geo json", "*.geojson"),
                       ("All Files", "*.*")))
        if outputfile:
            self.tabs.window.sentencemanager.create_geojson_map(outputfile)
        else:
            raise ExportAborted('Export cancelled by user.')

    def export_jsonlines(self):
        """
        pop open a file browser to allow the user to choose where to save the
        file and then save file to that location

        Raises:
            ExportAborted: if the user clicks cancel
        """
        outputfile = tkinter.filedialog.asksaveasfilename(
            defaultextension=".jsonl",
            filetypes=(("JSON lines", "*.jsonl"),
                       ("All Files", "*.*")))
        if outputfile:
            poslist = list(self.tabs.window.sentencemanager.positions.values())
            export.write_json_lines(poslist, outputfile)
        else:
            raise ExportAborted('Export cancelled by user.')

    def export_nmea(self):
        """
        pop open a file browser to allow the user to choose where to save the
        file and then save file to that location

        Raises:
            ExportAborted: if the user clicks cancel
        """
        outputfile = tkinter.filedialog.asksaveasfilename(
            defaultextension=".nmea",
            filetypes=(("NMEA 0183 text files", "*.txt *.nmea"),
                       ("All Files", "*.*")))
        if outputfile:
            sentences = self.tabs.sentencestab.txtbox.get(1.0, "end-1c")
            export.write_text_file(sentences, outputfile)
        else:
            raise ExportAborted('Export cancelled by user.')
