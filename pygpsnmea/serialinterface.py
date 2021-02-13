"""
a simple program to log data from a serial port
"""


import logging
import logging.handlers


import serial


class SerialInterface():
    """
    class for the serial interface
    """

    def __init__(self, serialdevice, baudrate, logpath=False):
        self.interface = serial.Serial(serialdevice, baudrate)
        self.seriallog = logging.getLogger('serialport')
        self.seriallog.setLevel(logging.INFO)
        if logpath:
            self.setup_file_handler(logpath)

    def setup_file_handler(self, outputpath):
        """
        setup the logger to save NMEA sentences to a file

        Args:
            outputpath(str): path to save to
        """
        logformatstr = '%(message)s'
        logformatter = logging.Formatter(fmt=logformatstr)
        rotatinghandler = logging.handlers.RotatingFileHandler(
            outputpath, maxBytes=1000000)
        rotatinghandler.setFormatter(logformatter)
        self.seriallog.addHandler(rotatinghandler)
        self.seriallog.propagate = False

    def read_from_serial(self, dataqueue):
        """
        read data from the serial port constantly
        decode it to ASCII and log it
        """
        while True:
            try:
                sentence = self.interface.readline().decode('ascii')
                self.seriallog.info(sentence.rstrip())
                dataqueue.put(sentence)
            except UnicodeDecodeError:
                continue


def test_serial_interface_connection(serialdevice, baudrate):
    """
    test if we can successfully read from this serial device by reading
    1 bytes from the interface

    Args:
        serialdevice(str): path to the serial device to test
        baudrate(int): baud rate in bps for the device

    Returns:
        True: if we can read from the device

    Raises:
        serial.SerialException: if we cannot read from the device
        """
    try:
        interface = serial.Serial(serialdevice, baudrate, timeout=2)
        interface.read()
        return True
    except serial.SerialException as err:
        raise err


def mp_serial_interface(dataqueue, device, baud, logpath=None):
    """
    meant to be run in another process by the GUI
    """
    serialint = SerialInterface(device, baud, logpath=logpath)
    serialint.read_from_serial(dataqueue)
