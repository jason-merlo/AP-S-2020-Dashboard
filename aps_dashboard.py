# -*- coding: utf-8 -*-
"""
Tracker Dashboard Class.

Main file for quad doppler radar tracking project.

Author: Jason Merlo
Maintainer: Jason Merlo (merlojas@msu.edu)
"""
# === Window / UI ===
import pyqtgraph as pg                  # GUI event timer
import signal                           # Handle ctrl-c
import sys                              # Exit gracefully
# === Error Handling ===
import traceback                        # Handling errors gracefully
# === Sampling / Hardware ===
from pyratk.acquisition.data_mgr import DataManager
from pyratk.acquisition.mcdaq_win import mcdaq_win
from pyratk.radars import radar    # RadaryArray object
# === Tracking ===
from pyratk.trackers import tracker  # 2D tracker object
# === Geometry primatives ===
from pyratk.datatypes.geometry import Point  # Radar locations
from pyratk.datatypes.motion import StateMatrix
# === GUI Elements ===
from data_window import DataWindow
# === DEBUG ===
import warnings

import numpy as np
import time
from collections import namedtuple


# === CONSTANTS ===============================================================
DEFAULT_PATH = 'aps_radar_testing.hdf5'

DURATION = 1500e-6
PRF = int(1/DURATION)
BW = 100e6

DAQ_SAMPLE_RATE = int(100e3)
DAQ_CHUNK_SIZE = int(DAQ_SAMPLE_RATE * DURATION)

# FFT_WIN_SIZE = int(DAQ_CHUNK_SIZE * 1)
FFT_WIN_SIZE = DAQ_CHUNK_SIZE
# FFT_SIZE = 2**12
FFT_SIZE = FFT_WIN_SIZE * 100
print('FFT_WIN_SIZE:', FFT_WIN_SIZE)
print('FFT_SIZE:', FFT_SIZE)

# == Debug Stats ===
min_freq = DAQ_SAMPLE_RATE / FFT_SIZE
print('FREQUENCY_RES: {:1.6f} Hz'.format(min_freq))
c = 299792458  # m/s
min_dist = DURATION / BW * c * min_freq
print('VELOCITY_RES: {:1.6f} mm'.format(min_dist * 1000))


# === DEBUG ===================================================================
def warn_with_traceback(message, category, filename, lineno, file=None,
                        line=None):
    """Handle error gracefully, but write traceback to terminal."""
    log = file if hasattr(file, 'write') else sys.stderr
    traceback.print_stack(file=log)
    log.write(warnings.formatwarning(
        message, category, filename, lineno, line))


warnings.showwarning = warn_with_traceback
# =============================================================================


class Application(object):
    """Main multi-doppler tracker application class."""

    def __init__(self):
        """Start application on initialization."""
        self.run()

    def init_signal_handler(self, app):
        """Handle signals for ctrl-c event and window 'X' button event."""
        # ctrl-c handler
        signal.signal(signal.SIGINT, self.signal_handler)
        # Window close handler
        app.aboutToQuit.connect(self.signal_handler)

    def signal_handler(self, signal=0, frame=0):
        """Gracefully handle program shutdown by closing all daq sources."""
        print('Closing sources...')
        self.data_mgr.close()

        print('Program exiting...')
        sys.exit(0)

    # def update_step(self):
    #     """Update tracker with new data and draw to graphs."""
    #     self.data_win.update()

    def run(self):
        """Configure main multi-doppler tracking application functions."""
        # === INIT ============================================================
        # Create application context and setup sampler and signal handler
        app = pg.QtGui.QApplication([])

        # Create data manager object for DAQ and playback
        self.data_mgr = DataManager(db=DEFAULT_PATH)

        try:
            mcdaq_daq = mcdaq_win(sample_rate=DAQ_SAMPLE_RATE,
                            sample_chunk_size=DAQ_CHUNK_SIZE)
            self.data_mgr.add_source(mcdaq_daq)
            self.data_mgr.set_source(mcdaq_daq)
        except Exception as e:
            print('Could not start DAQ:', e)


        # Set up program exit routine
        self.init_signal_handler(app)

        # Transmitter parameters
        Pulse = namedtuple('Pulse', ['fc', 'bw', 'delay'])
        pulses = (Pulse(5.825e9, 100e6, 1500e-6),)
        TransmitterTuple = namedtuple('Transmitter', ['location', 'pulses'])
        transmitter_list = (TransmitterTuple(Point(0, 0, 0), pulses),)

        # Receiver parameters
        ReceiverTuple = namedtuple('Receiver', ['daq_index', 'location'])
        receiver_list = (
            ReceiverTuple(daq_index=(1, 3), location=Point(0, 0, 0)),
            ReceiverTuple(daq_index=(5, 7), location=Point(0, 0, 0)),
            ReceiverTuple(daq_index=(0, 2), location=Point(0, 0, 0)),
            ReceiverTuple(daq_index=(4, 6), location=Point(0, 0, 0))
        )

        receiver_array = radar.Radar(
            self.data_mgr,
            transmitter_list,
            receiver_list,
            fast_fft_size=2**8,
            slow_fft_size=2**10,
            slow_fft_len=100
        )

        # === GUI =============================================================
        # Instantiate and display data-viewing window
        # (close gracefully on failure)
        try:
            self.data_win = DataWindow(
                app, self.data_mgr, (*receiver_array.receivers,))
            self.data_win.setGeometry(160, 140, 1400, 1000)
            # self.data_win.showMaximized()
            self.data_win.show()
        except Exception:
            # Catch all errors and exit for dev purposes
            print(traceback.format_exc())
            self.signal_handler()

        # Connect events for data processing
        # receiver_array.data_available_signal.connect(self.data_win.update)
        timer = pg.QtCore.QTimer()
        timer.timeout.connect(self.data_win.update)
        timer.start(30)

        # Start sampling
        # daq.start()

        # ------ Run Qt program ------ #
        sys.exit(app.exec_())

if __name__ == '__main__':
    app = Application()
