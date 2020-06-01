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


# === CONSTANTS ===============================================================
DEFAULT_PATH = 'aps_radar_testing.hdf5'

PRF = int(1/4000e-6)

DAQ_SAMPLE_RATE = 50000
DAQ_CHUNK_SIZE = int(DAQ_SAMPLE_RATE / PRF)

# FFT_WIN_SIZE = int(DAQ_CHUNK_SIZE * 1)
FFT_WIN_SIZE = DAQ_CHUNK_SIZE
# FFT_SIZE = 2**12
FFT_SIZE = FFT_WIN_SIZE

# == Debug Stats ===
min_freq = DAQ_SAMPLE_RATE / FFT_SIZE
print('FREQUENCY_RES: {:1.6f} Hz'.format(min_freq))
c = 299792458  # m/s
min_vel = (c * 5.8e9 / (-min_freq + 5.8e9)) - c
print('VELOCITY_RES: {:1.6f} mm/s'.format(min_vel * 1000))


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
        daq = mcdaq_win(sample_rate=DAQ_SAMPLE_RATE,
                        sample_chunk_size=DAQ_CHUNK_SIZE)

        # Create data manager object for DAQ and playback
        self.data_mgr = DataManager(db=DEFAULT_PATH, daq=daq)
        self.data_mgr.set_source(daq)

        # Set up program exit routine
        self.init_signal_handler(app)

        # Array discription
        receiver_list = (radar.Radar(self.data_mgr, (1, 3), Point(-0.0405, -0.0405),
                                     f0=5.8e9, fft_size=FFT_SIZE, fft_win_size=FFT_WIN_SIZE),
                         radar.Radar(self.data_mgr, (5, 7), Point(+0.0405, -0.0405),
                                     f0=5.8e9, fft_size=FFT_SIZE, fft_win_size=FFT_WIN_SIZE),
                         radar.Radar(self.data_mgr, (0, 2), Point(+.0405, +0.0405),
                                     f0=5.8e9, fft_size=FFT_SIZE, fft_win_size=FFT_WIN_SIZE),
                         radar.Radar(self.data_mgr, (4, 6), Point(-0.0405, +0.0405),
                                     f0=5.8e9, fft_size=FFT_SIZE, fft_win_size=FFT_WIN_SIZE))

        receiver_array = radar.RadarArray(self.data_mgr, receiver_list)

        # === GUI =============================================================
        # Instantiate and display data-viewing window
        # (close gracefully on failure)
        try:
            radar_graph_list = ((*receiver_list,),)
            # radar_graph_list = ((radar_list[0],),)
            self.data_win = DataWindow(
                app, self.data_mgr, radar_graph_list)
            self.data_win.setGeometry(160, 140, 2000, 800)
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
        timer.start(50)

        # Start sampling
        daq.start()

        # ------ Run Qt program ------ #
        sys.exit(app.exec_())

if __name__ == '__main__':
    app = Application()
