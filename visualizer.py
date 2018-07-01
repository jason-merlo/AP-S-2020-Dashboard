# -*- coding: utf-8 -*-
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui
# import numpy as np
import DAQ
import signal
import sys
import threading
import time
from radar_widget import RadarWidget

# === CONSTANTS ===============================================================
DAQ_SAMPLE_SIZE = 4096   # Hardware max = 4096
DAQ_SAMPLE_RATE = 31000  # Hz
FFT_SIZE = DAQ_SAMPLE_SIZE

class QuadGraph(pg.LayoutWidget):
    pass

class DataWindow(pg.LayoutWidget):
    def __init__(self, daq):
        pg.LayoutWidget.__init__(self)

        # Copy member objects
        self.daq = daq

        # Instantiate RadarWidget objects
        self.rw1 = RadarWidget(100, FFT_SIZE, self.daq, 0)
        self.rw2 = RadarWidget(100, FFT_SIZE, self.daq, 1)
        self.rw3 = RadarWidget(100, FFT_SIZE, self.daq, 2)
        self.rw4 = RadarWidget(100, FFT_SIZE, self.daq, 3)

        # Create layout
        self.setWindowTitle('Quad-Radar')

        # Add button
        button = QtGui.QPushButton('Test')
        button.clicked.connect(button_handler)
        self.addWidget(button, rowspan=2, colspan=1)
        self.nextCol()

        # Add elements to layout
        self.addWidget(self.rw1)
        self.addWidget(self.rw2)
        self.nextRow()
        self.nextCol()

        self.nextCol()
        self.addWidget(self.rw3)
        self.addWidget(self.rw4)

    # Set gui update timer
    def update_gui(self):
        if self.daq.data_available.is_set():
            self.rw1.update()
            self.rw2.update()
            self.rw3.update()
            self.rw4.update()
            # Clear event once GUI update ends
            self.daq.data_available.clear()
            print("GUI update ran...")
        else:
            # sleep 1/2 of a DAQ update cycle
            print("sleeping..........")
            time.sleep((DAQ_SAMPLE_SIZE / DAQ_SAMPLE_RATE) * 0.5)


def button_handler():
    print("Button Clicked!")

if __name__ == '__main__':

    # --- DAQ Setup -----------------------------------------------------------
    # Instantiate DAQ object
    daq = DAQ.DAQ(sample_rate=DAQ_SAMPLE_RATE, sample_size=DAQ_SAMPLE_SIZE, fake_data=False)

    # Create sampling and drawing threads
    daq_thread = threading.Thread(target=daq.get_samples)

    # Spawn threads
    daq_thread.start()

    # --- Application Setup ---------------------------------------------------
    # Create application context
    app = QtGui.QApplication([])

    # ------ Exit handlers ------ #
    def signal_handler(signal=0, frame=0):
            print('Program exiting...')
            daq.running = False
            daq_thread.join()
            sys.exit(0)
    # ctrl-c handler
    signal.signal(signal.SIGINT, signal_handler)
    # Window close handler
    app.aboutToQuit.connect(signal_handler)
    # --------------------------- #

    # Instantiate and display data-viewing window
    data_win = DataWindow(daq)
    data_win.show()

    # Set data-viewing window update timer
    timer = pg.QtCore.QTimer()
    timer.timeout.connect(data_win.update_gui)
    timer.start(0)

    # ------ Run Qt program ------ #
    sys.exit(app.exec_())
    # ---------------------------- #
