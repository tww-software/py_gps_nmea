"""
start PY GPS NMEA
"""

import pygpsnmea.gui.mainwindow as gui


def main():
    """
    main program code
    """
    maingui = gui.BasicGUI()
    maingui.mainloop()


if __name__ == '__main__':
    main()
