# -*- coding: utf-8 -*-
'''
tracker_dashboard.py
Main file for quad doppler radar tracking project

Author: Jason Merlo
Maintainer: Jason Merlo (merlojas@msu.edu)
last_modified: 7/25/2018
'''
# === Window / UI ===
import pyqtgraph as pg                  # GUI event timer
import signal                           # Handle ctrl-c
import sys                              # Exit gracefully
# === Error Handling ===
import traceback                        # Handling errors gracefully
# === Sampling / Hardware ===
import daq_mgr                          # DAQ hardware
import data_mgr
import threading                        # Independant sampling thread
import radar                            # RadaryArray object
# === Tracking ===
import tracker                          # 2D tracker object
# === Database ===
import h5py                             # Database storage
# === Geometry primatives ===
from geometry import Point              # Radar locations
# === GUI Elements ===
from data_window import DataWindow

# === CONSTANTS ===============================================================
DAQ_SAMPLE_SIZE = 2048   # Hardware max = 4096
DAQ_SAMPLE_RATE = 31250  # Hz - hardware max = 31250
FFT_WINDOW_SIZE = 4096
FFT_SIZE = 2**16

# saved parameters - Working well for slow shapes - 8/3/2018
# DAQ_SAMPLE_SIZE = 2048   # Hardware max = 4096
# DAQ_SAMPLE_RATE = 31250  # Hz - hardware max = 31250
# FFT_WINDOW_SIZE = 4096
# FFT_SIZE = 2**15


# ===============================
# DEBUG
import traceback
import warnings
import sys

def warn_with_traceback(message, category, filename, lineno, file=None, line=None):

    log = file if hasattr(file,'write') else sys.stderr
    traceback.print_stack(file=log)
    log.write(warnings.formatwarning(message, category, filename, lineno, line))

warnings.showwarning = warn_with_traceback

# ===============================


def init_signal_handler(app, daq):
    '''
    Connects signals for ctrl-c event and window 'X' button event to the
    signal handler function to gracefully shutdown program
    '''
    # ctrl-c handler
    signal.signal(signal.SIGINT, signal_handler)
    # Window close handler
    app.aboutToQuit.connect(signal_handler)


def signal_handler(signal=0, frame=0):
    '''
    Handler function to gracefully shutdown program
    '''
    global daq

    print('Program exiting...')
    daq.close()
    sys.exit(0)


def main():
    global daq

    # Create application context and setup sampler and signal handler
    app = pg.QtGui.QApplication([])
    daq = daq_mgr.DAQ(sample_rate=DAQ_SAMPLE_RATE, sample_size=DAQ_SAMPLE_SIZE)

    data_mgr = DataManager()
    data_mgr.add_source(daq)

    init_signal_handler(app, daq)

    # Create array and trackers
    array_shape = (2, 2)
    array_indices = ((0, 3),
                     (1, 2))
    # array_dims = ((Point(0,     0),  Point(0.081,      0)),
    #               (Point(0, -0.081), Point(0.081, -0.081)))  # m
    array_dims = ((Point(-0.0405,  0.0405), Point(0.0405,  0.0405)),
                  (Point(-0.0405, -0.0405), Point(0.0405, -0.0405)))  # m
    radar_array = radar.RadarArray(
        daq, fft_size=FFT_SIZE, fft_window_size=FFT_WINDOW_SIZE, locations=array_dims, indices=array_indices)
    tracker2d = tracker.Tracker2D(daq, radar_array)

    # Instantiate and display data-viewing window (close gracefully on failure)
    try:
        data_win = DataWindow(daq, radar_array, tracker2d)
        data_win.setGeometry(160, 140, 1400, 800)
        data_win.showMaximized()
        data_win.show()
    except:
        # Catch all errors and exit for dev purposes
        print(traceback.format_exc())
        signal_handler()

    # Set data-viewing window update timer
    gui_timer = pg.QtCore.QTimer()
    gui_timer.timeout.connect(data_win.update_gui)
    # Only update 2x as fast as new data arrives
    gui_timer.start(daq.sample_size / daq.sample_rate * 500)  # in ms

    # Radar update timer
    tracker_timer = pg.QtCore.QTimer()
    tracker_timer.timeout.connect(tracker2d.update)
    # Only update 2x as fast as new data arrives
    tracker_timer.start(daq.sample_size / daq.sample_rate * 500)  # in ms

    # ------ Run Qt program ------ #
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
