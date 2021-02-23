"""
useful tab with a single scrollable text box
"""

import tkinter


class TextBoxTab(tkinter.ttk.Frame):
    """
    tab to display NMEA Sentences, statistics and large text strings

    Note:
        basically a tab with a big text box on it that autoscrolls as you
        update it

    Args:
        tabcontrol(tkinter.ttk.Notebook): ttk notebook to add this tab to

    Attributes:
        tabs(tkinter.ttk.Notebook): ttk notebook to add this tab to
        txtbox(tkinter.scrolledtext.ScrolledText): text box to display text
    """

    def __init__(self, tabcontrol):
        tkinter.ttk.Frame.__init__(self, tabcontrol)
        self.tabs = tabcontrol
        self.txtbox = tkinter.scrolledtext.ScrolledText(
            self, selectbackground='cyan')
        self.txtbox.pack(side='left', fill='both', expand=tkinter.TRUE)
        self.txtbox.bind('<Control-c>', self.copy)
        self.txtbox.bind('<Control-C>', self.copy)
        self.txtbox.bind('<Control-a>', self.select_all)
        self.txtbox.bind('<Control-A>', self.select_all)
        self.txtbox.bind('<Button-3>', self.select_all)

    def append_text(self, text):
        """
        write text into the box and append a newline after it

        Args:
            text(str): text to write in the box
        """
        self.txtbox.insert(tkinter.INSERT, text)
        self.txtbox.insert(tkinter.INSERT, '\n')
        self.txtbox.see(tkinter.END)

    def copy(self, event):
        """
        put highlighted text onto the clipboard when ctrl+c is used

        Args:
            event(tkinter.Event): event from the user (ctrl + c)
        """
        try:
            self.txtbox.clipboard_clear()
            self.txtbox.clipboard_append(
                self.txtbox.selection_get())
        except tkinter.TclError:
            pass

    def select_all(self, event):
        """
        select all the text in the textbox when ctrl+a is used

        Args:
            event(tkinter.Event): event from the user (ctrl + a)
        """
        self.txtbox.tag_add(tkinter.SEL, "1.0", tkinter.END)
        self.txtbox.mark_set(tkinter.INSERT, "1.0")
        self.txtbox.see(tkinter.INSERT)
        return 'break'

    def clear(self):
        """
        clear the text box
        """
        self.txtbox.delete(1.0, tkinter.END)
