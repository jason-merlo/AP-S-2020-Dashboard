# -*- coding: utf-8 -*-
# === Window / UI ===
import pyqtgraph as pg                  # GUI event timer
import signal                           # Handle ctrl-c
import sys                              # Exit gracefully
# === Error Handling ===
import traceback                        # Handling errors gracefully
# === Sampling / Hardware ===
import DAQ                              # DAQ hardware
import threading                        # Independant sampling thread
# === Database ===
import h5py                             # Database storage
# === GUI Elements ===
from DataWindow import DataWindow

# === CONSTANTS ===============================================================
DAQ_SAMPLE_SIZE = 4096   # Hardware max = 4096
DAQ_SAMPLE_RATE = 31000  # Hz
ZERO_PAD_FACTOR = 16
FFT_SIZE = DAQ_SAMPLE_SIZE * ZERO_PAD_FACTOR

def init_daq():
    # --- DAQ Setup -----------------------------------------------------------
    # Instantiate DAQ object
    daq = DAQ.DAQ(sample_rate=DAQ_SAMPLE_RATE, sample_size=DAQ_SAMPLE_SIZE)
    # Start sampling
    daq.start_sampling()

    return daq

def signal_handler(signal=0, frame=0):
    print('Program exiting...')
    daq.close()
    sys.exit(0)

def init_signal_handler(app, daq):
    # ctrl-c handler
    signal.signal(signal.SIGINT, signal_handler)
    # Window close handler
    app.aboutToQuit.connect(signal_handler)

# === Main Function ===========================================================
if __name__ == '__main__':
    # Create application context and setup sampler and signal handler
    app = pg.QtGui.QApplication([])
    daq = init_daq()
    init_signal_handler(app, daq)

    # Instantiate and display data-viewing window (close gracefully on failure)
    try:
        data_win = DataWindow(daq, FFT_SIZE)
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
