# -*- coding: utf-8 -*-
'''
tracker_dashboard.py
Main file for quad doppler radar tracking project

Author: Jason Merlo
Maintainer: Jason Merlo (merlojas@msu.edu)
last_modified: 7/3/2018
'''
# === Window / UI ===
import pyqtgraph as pg                  # GUI event timer
import signal                           # Handle ctrl-c
import sys                              # Exit gracefully
# === Error Handling ===
import traceback                        # Handling errors gracefully
# === Sampling / Hardware ===
import daq_mgr                          # DAQ hardware
import threading                        # Independant sampling thread
import radar                            # RadaryArray object
# === Tracking ===
import tracker                          # 2D tracker object
# === Database ===
import h5py                             # Database storage
# === GUI Elements ===
from data_window import DataWindow

# === CONSTANTS ===============================================================
DAQ_SAMPLE_SIZE = 4096   # Hardware max = 4096
DAQ_SAMPLE_RATE = 31250  # Hz - hardware max = 31250
ZERO_PAD_FACTOR = 24     # FFT_SIZE = 65536
FFT_SIZE = DAQ_SAMPLE_SIZE * ZERO_PAD_FACTOR


def init_daq():
    '''
    Creates DAQ object, starts sampling, returns object
    '''
    daq = daq_mgr.DAQ(sample_rate=DAQ_SAMPLE_RATE, sample_size=DAQ_SAMPLE_SIZE)
    daq.start_sampling()
    return daq


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
    daq = init_daq()
    init_signal_handler(app, daq)

    # Create array and trackers
    array_shape = (2, 2)
    array_dims = (((0,     0),  (0,     105.6)),
                  ((105.6, 0),  (105.6, 105.6)))  # mm
    radar_array = radar.RadarArray(
        daq, array_shape, array_dims, fft_size=FFT_SIZE)
    tracker2d = tracker.Tracker2D(radar_array)

    # Instantiate and display data-viewing window (close gracefully on failure)
    try:
        data_win = DataWindow(daq, radar_array, tracker2d)
        data_win.setGeometry(160, 140, 1400, 800)
        data_win.show()
    except:
        # Catch all errors and exit for dev purposes
        print(traceback.format_exc())
        signal_handler()

    # Set data-viewing window update timer
    timer = pg.QtCore.QTimer()
    timer.timeout.connect(data_win.update_gui)
    # Only update 2x as fast as new data arrives
    timer.start(daq.sample_size / daq.sample_rate * 500)  # in ms

    # ------ Run Qt program ------ #
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
