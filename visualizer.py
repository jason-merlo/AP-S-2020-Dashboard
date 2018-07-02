# -*- coding: utf-8 -*-
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
# import numpy as np
import DAQ
import signal
import sys
import threading
import time
import traceback
import h5py
from radar_widget import RadarWidget

# === CONSTANTS ===============================================================
DAQ_SAMPLE_SIZE = 4096   # Hardware max = 4096
DAQ_SAMPLE_RATE = 31000  # Hz
FFT_SIZE = DAQ_SAMPLE_SIZE * 16

class GraphPanel(pg.LayoutWidget):
    def __init__(self, daq, fft_size):
        pg.LayoutWidget.__init__(self)

        # Copy member objects
        self.daq = daq

        # Instantiate RadarWidget objects
        self.rw1 = RadarWidget(100, fft_size, self.daq, 0)
        self.rw2 = RadarWidget(100, fft_size, self.daq, 1)
        self.rw3 = RadarWidget(100, fft_size, self.daq, 2)
        self.rw4 = RadarWidget(100, fft_size, self.daq, 3)

        # Add elements to layout
        self.addWidget(self.rw1)
        self.addWidget(self.rw2)
        self.nextRow()
        self.addWidget(self.rw3)
        self.addWidget(self.rw4)

        # Remove extra margins around plot widgets
        self.layout.setContentsMargins(0, 0, 0, 0)

    def update(self):
        self.rw1.update()
        self.rw2.update()
        self.rw3.update()
        self.rw4.update()

    def reset(self):
        self.rw1.reset()
        self.rw2.reset()
        self.rw3.reset()
        self.rw4.reset()


class ControlPanel(pg.LayoutWidget):
    '''
    Keeps track of stop/start, reset, load/save datasets, and label controls
    '''
    def __init__(self, daq, graph_panel):
        pg.LayoutWidget.__init__(self)

        # Copy member objects
        self.daq = daq
        self.graph_panel = graph_panel

        # Add buttons to screen
        self.add_control_buttons()
        self.nextRow()
        self.add_dataset_buttons()
        self.nextRow()
        self.add_dataset_list()
        self.nextRow()
        # Add spacer item to shift all buttons to top of screen
        self.verticalSpacer = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.layout.addItem(self.verticalSpacer)

        # Remove extra margins around button widgets
        self.layout.setContentsMargins(0, 0, 0, 0)

    def add_control_buttons(self):
        # Add buttons
        self.pause_button = QtGui.QPushButton('Start/Stop')
        self.pause_button.clicked.connect(self.pause_button_handler)
        self.reset_button = QtGui.QPushButton('Clear Data')
        self.reset_button.clicked.connect(self.reset_button_handler)

        # Add widgets to layout
        self.addWidget(self.pause_button)
        self.nextRow()
        self.addWidget(self.reset_button)

        # Align widgets to top instead of center
        self.layout.setAlignment(self.pause_button, QtCore.Qt.AlignTop)
        self.layout.setAlignment(self.reset_button, QtCore.Qt.AlignTop)

    def add_dataset_buttons(self):
        # Add buttons
        self.load_dataset_button = QtGui.QPushButton('Load Dataset...')
        self.load_dataset_button.clicked.connect(self.load_dataset_button_handler)
        self.save_dataset_button = QtGui.QPushButton('Save Dataset')
        self.save_dataset_button.clicked.connect(self.save_dataset_button_handler)
        self.save_dataset_as_button = QtGui.QPushButton('Save Dataset as...')
        self.save_dataset_as_button.clicked.connect(self.save_dataset_as_button_handler)

        # Add widgets to layout
        self.addWidget(self.load_dataset_button)
        self.nextRow()
        self.addWidget(self.save_dataset_button)
        self.nextRow()
        self.addWidget(self.save_dataset_as_button)

        # Align widgets to top instead of center
        self.layout.setAlignment(self.load_dataset_button, QtCore.Qt.AlignTop)
        self.layout.setAlignment(self.save_dataset_button, QtCore.Qt.AlignTop)
        self.layout.setAlignment(self.save_dataset_as_button, QtCore.Qt.AlignTop)

    def add_dataset_list(self):
        self.dataset_list = QtGui.QListWidget()
        # self.dataset_list.addItem("Item 1");
        # self.dataset_list.addItem("Item 2");
        # self.dataset_list.addItem("Item 3");
        # self.dataset_list.addItem("Item 4");
        self.dataset_list.itemClicked.connect(self.load_dataset_button_handler)

        # Add widget to main window
        self.addWidget(self.dataset_list)

    def load_dataset_button_handler(self):
        print("load datset...")

    def save_dataset_button_handler(self):
        print("save dataset")

    def save_dataset_as_button_handler(self):
        print("save dataset as...")

    def pause_button_handler(self):
        if self.daq.pause:
            self.daq.pause = False
            print("DAQ running.")
        else:
            self.daq.pause = True
            print("DAQ paused.")

    def reset_button_handler(self):
        self.graph_panel.reset()


class DataWindow(pg.LayoutWidget):
    def __init__(self, daq, fft_size):
        pg.LayoutWidget.__init__(self)

        # Copy member objects
        self.daq = daq

        # Create layout
        self.setWindowTitle('Radar Tracking Visualizer')

        # Add panels to data window
        self.graph_panel = GraphPanel(self.daq, fft_size)
        self.control_panel = ControlPanel(self.daq, self.graph_panel)

        # Add GUI items to window layout
        self.addWidget(self.control_panel)
        self.nextCol()
        self.addWidget(self.graph_panel)

    # Set gui update timer
    def update_gui(self):
        # Only update if new data is available
        if self.daq.data_available.is_set():
            self.graph_panel.update()
            # Clear event once GUI update ends
            self.daq.data_available.clear()


# === Main Function ===========================================================
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
    try:
        data_win = DataWindow(daq, FFT_SIZE)
        data_win.show()
    except:
        # Catch all errors and exit for dev purposes
        print (traceback.format_exc())
        signal_handler()

    # Set data-viewing window update timer
    timer = pg.QtCore.QTimer()
    timer.timeout.connect(data_win.update_gui)
    # Only update 2x as fast as new data arrives
    timer.start(daq.sample_size / daq.sample_rate * 500)  # in ms

    # ------ Run Qt program ------ #
    sys.exit(app.exec_())
    # ---------------------------- #
