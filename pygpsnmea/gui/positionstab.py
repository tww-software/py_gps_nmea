"""
tab to display a table of all the positions we have recorded
"""

import tkinter

import pygpsnmea.export as export


class PosRepTab(tkinter.ttk.Frame):
    """
    tab to display all the NMEA Sentences and descriptions + times

    Note:
        basically a tab with a table inside

    Args:
        tabcontrol(tkinter.ttk.Notebook): ttk notebook to add this tab to
    """
    
    def __init__(self, tabcontrol):
        tkinter.ttk.Frame.__init__(self, tabcontrol)
        self.autoscroll = tkinter.BooleanVar()
        self.autoscroll.set(1)
        self.autoscrollchk = tkinter.Checkbutton(
            self, text='autoscroll as new positions are added',
            var=self.autoscroll)
        self.autoscrollchk.select()
        self.autoscrollchk.pack(side=tkinter.TOP)
        self.tabs = tabcontrol
        self.counter = 0
        self.tree = tkinter.ttk.Treeview(self)
        verticalscrollbar = tkinter.ttk.Scrollbar(
            self, orient=tkinter.VERTICAL, command=self.tree.yview)
        verticalscrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        horizontalscrollbar = tkinter.ttk.Scrollbar(
            self, orient=tkinter.HORIZONTAL, command=self.tree.xview)
        horizontalscrollbar.pack(side=tkinter.BOTTOM, fill=tkinter.X)
        self.tree.configure(yscrollcommand=verticalscrollbar.set,
                            xscrollcommand=horizontalscrollbar.set)
        self.create_message_table()



    def create_message_table(self):
        """
        draw a large table in messagetab of all the NMEA sentences we have
        """
        self.tree.delete(*self.tree.get_children())
        headers = ['Position No', 'Latitude', 'Longitude', 'Timestamp']
        self.tree["columns"] = headers
        for column in headers:
            self.tree.column(column, width=200, minwidth=70,
                             stretch=tkinter.YES)
            self.tree.heading(column, text=column, anchor=tkinter.W)
        self.tree.pack(side=tkinter.TOP, fill='both', expand=tkinter.TRUE)
        self.tree['show'] = 'headings'

    def add_new_line(self, line):
        """
        add a new line to the tree table and scroll down to it

        Note:
            line[2] is the message type refered to in msg_line_colours
        """
        self.tree.insert('', self.counter, values=line, tags=(line[2],))
        self.counter += 1
        if self.autoscroll.get() == 1:
            self.tree.yview_moveto(1)
