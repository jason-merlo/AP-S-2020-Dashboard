# -*- coding: utf-8 -*-
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui
# import numpy as np
import DAQ
import signal
import sys
import threading
import asyncio
from radar_widget import RadarWidget

# === CONSTANTS ===============================================================
DAQ_SAMPLE_SIZE = 4096   # Hardware max = 4096
DAQ_SAMPLE_RATE = 30000  # Hz
FFT_SIZE = 4096


if __name__ == '__main__':

    # Create application context
    app = QtGui.QApplication([])

    # Create semaphore for controlling access to numpy data buffer for r/w
    sem = asyncio.BoundedSemaphore()
    # Decriments semaphore to zero. Will not draw until data is received.
    sem.acquire()

    # Instantiate DAQ object
    daq = DAQ.DAQ(sem=sem, sample_rate=DAQ_SAMPLE_RATE, sample_size=DAQ_SAMPLE_SIZE, fake_data=False)

    # Instantiate RadarWidget objects
    rw1 = RadarWidget(sem, 100, FFT_SIZE, daq, 0)
    rw2 = RadarWidget(sem, 100, FFT_SIZE, daq, 1)
    rw3 = RadarWidget(sem, 100, FFT_SIZE, daq, 2)
    rw4 = RadarWidget(sem, 100, FFT_SIZE, daq, 3)

    # Set up signal handler for ctrl-c
    def signal_handler(signal=0, frame=0):
            print('Program exiting...')
            daq.running = False
            sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)

    # Create layout
    win = pg.LayoutWidget()
    win.setWindowTitle('Quad-Radar')

    # Add elements to layout
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
    #sample_period = (daq.sample_size/daq.sample_rate) * 100
    timer = pg.QtCore.QTimer()
    timer.timeout.connect(update_gui)
    timer.start(0)

    # Set up exit handler
    #app = QApplication(sys.argv)
    app.aboutToQuit.connect(signal_handler)

    # Run Qt program
    app.exec_()

    # will be called on ctrl-c or exit
    daq_thread.join()
