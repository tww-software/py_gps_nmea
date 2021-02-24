# Py GPS NMEA

PY GPS NMEA is a program designed to read NMEA 0183 sentences from GPS serial
devices or from plain text files. It is written in Python 3 and has
a GUI made with TKinter.

## Unit Tests
To run the unit tests.

```
python3 -m unittest pygpsnmea.test_gps
```

## Running the program

to run PY GPS NMEA

```
python3 -m pygpsnmea
```

## PY GPS NMEA GUI
The GUI is the main interface to the program and was written using Tkinter.

### Reading from a serial device
To read GPS positions from a serial device:
1. go to 'Settings' on the top menu and select 'Serial Settings'
2. enter the path (if on linux) or COM port (if on windows) in the Serial Device box
3. choose the appropriate baud rate
4. if you want to log NMEA sentences as they are recieved click the 'Choose Log Path' button and select a file path
5. click 'Choose KML Path' to output live KML positions to a file which can then be viewed in Google Earth. This will create 2 files the kml data file and a KML netlink file that you will open in Google Earth to view a live position
6. click the 'Save Settings' at the bottom of the form
7. from 'Settings' on the top of the main window click 'Start read from serial port' to start recieving and processing GPS NMEA data
8. from 'Settings' on the top of the main window click 'Stop read from serial port' to stop recieving and processing GPS NMEA data

### Status Tab
The status tab shows the total number of position reports received
and the number of checksum errors for the GPS receiver
or imported NMEA text file.

The Last Position Report section gives the last Latitude, Longitude and Time
of the last position received from the GPS serial device or the last postition
in the NMEA text file.

### Sentences Tab
Displays the raw NMEA0183 sentences.

### Position Reports Tab
The position reports tab provides a table for all the position reports.
Positions are sorted oldest at the top and newest at the bottom.
Each position has a reference number, latitude, longitude and timestamp in UTC.

### Export Tab
This tab allows you to export all the positions we have from the NMEA file or
GPS serial device.

The export options are:

CSV - Comma Separated Values file containing latitudes, longitudes andtimestamps
TSV - Tab Separated Values file containing latitudes, longitudes andtimestamps
KML - KML map of all the positions
GEOJSON - GEOJSON map of all the positions
JSON LINES - line delimited JSON output of all positions
NMEA - NMEA sentences - content of the sentences tab

Data cannot be exported whilst we are reading from a GPS serial device.

## Licence

MIT License

Copyright (c) 2020 Thomas W Whittam

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
