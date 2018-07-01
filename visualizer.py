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
DAQ_SAMPLE_RATE = 30000  # Hz
FFT_SIZE = 4096


if __name__ == '__main__':

    # Create application context
    app = QtGui.QApplication([])

    # Create sevent for controlling draw events only when there is new data
    update_event = threading.Event()

    # Instantiate DAQ object
    daq = DAQ.DAQ(event=update_event, sample_rate=DAQ_SAMPLE_RATE, sample_size=DAQ_SAMPLE_SIZE, fake_data=False)

    # Calculate DAQ sample period
    sample_period = DAQ_SAMPLE_SIZE / DAQ_SAMPLE_RATE

    # Instantiate RadarWidget objects
    rw1 = RadarWidget(100, FFT_SIZE, daq, 0)
    rw2 = RadarWidget(100, FFT_SIZE, daq, 1)
    rw3 = RadarWidget(100, FFT_SIZE, daq, 2)
    rw4 = RadarWidget(100, FFT_SIZE, daq, 3)

    # Set up signal handler for ctrl-c
    def signal_handler(signal=0, frame=0):
            print('Program exiting...')
            daq.running = False
            sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)

    # Set up exit handler
    # app = QApplication(sys.argv)
    app.aboutToQuit.connect(signal_handler)

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
        if update_event.is_set():
            rw1.update()
            rw2.update()
            rw3.update()
            rw4.update()
            # Clear event once GUI update ends
            update_event.clear()
            print("GUI update ran...")
        else:
            # sleep 1/2 of a DAQ update cycle
            print("sleeping..........")
            time.sleep(sample_period * 0.5)

    # sample_period = (daq.sample_size/daq.sample_rate) * 100
    timer = pg.QtCore.QTimer()
    timer.timeout.connect(update_gui)
    timer.start(0)

    # Run Qt program
    app.exec_()

    # will be called on ctrl-c or exit
    daq_thread.join()
