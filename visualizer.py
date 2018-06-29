# -*- coding: utf-8 -*-
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui
# import numpy as np
import DAQ
import signal
import sys
import threading
from radar_widget import RadarWidget

# === CONSTANTS ===============================================================
DAQ_SAMPLE_SIZE = 4096   # Hardware max = 4096
DAQ_SAMPLE_RATE = 50000  # Hz
FFT_SIZE = 256
FFT_OVERLAP = 128


if __name__ == '__main__':

    # list used to keep track of all running threaded objects to stop
    threaded_object_list = []

    app = QtGui.QApplication([])
    daq = DAQ.DAQ(sample_rate=DAQ_SAMPLE_RATE, sample_size=DAQ_SAMPLE_SIZE)

    # Set up signal handler for ctrl-c
    def signal_handler(signal, frame):
            print('Program exiting...')
            daq.running = False
            sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)

    win = pg.LayoutWidget()
    win.setWindowTitle('Quad-Radar')

    rw1 = RadarWidget(100, FFT_SIZE, daq, 0)
    rw2 = RadarWidget(100, FFT_SIZE, daq, 1)
    rw3 = RadarWidget(100, FFT_SIZE, daq, 2)
    rw4 = RadarWidget(100, FFT_SIZE, daq, 3)
    win.addWidget(rw1)
    win.addWidget(rw2)
    win.nextRow()
    win.addWidget(rw3)
    win.addWidget(rw4)

    win.show()

    # Create sampling and drawing threads
    daq_thread = threading.Thread(target=daq.get_samples)

    # Spawn threads
    daq_thread.start()

    # Set gui update timer
    def update_gui():
        rw1.update()
        rw2.update()
        rw3.update()
        rw4.update()
    sample_period = (daq.sample_size/daq.sample_rate) * 1000
    timer = pg.QtCore.QTimer()
    timer.timeout.connect(update_gui)
    timer.start(sample_period)

    # Run Qt program
    app.exec_()

    # will be called on ctrl-c or exit
    daq_thread.join()
