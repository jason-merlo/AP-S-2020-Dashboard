# -*- coding: utf-8 -*-
'''
Data Window Class.

Author: Jason Merlo
Maintainer: Jason Merlo (merlojas@msu.edu)
'''

# === Window / UI ===
from pyqtgraph import QtCore, QtGui     # Qt Elements
# === GUI Elements ===
from gui_panels import GraphPanel, ControlPanel

import os
import signal                       # handle escape to exit
import multiprocessing
import time
import sys

from profilehooks import profile

class DataWindow(QtGui.QTabWidget):
    def __init__(self, app, data_mgr, radar, tracker, parent=None):
        super(DataWindow, self).__init__(parent)
        # Copy member objects
        self.app = app
        self.data_mgr = data_mgr
        self.radar = radar
        self.tracker = tracker

        # Setup window
        self.setWindowTitle('Radar Tracking Visualizer')

        # Allow tabs to switch with keys
        # self.setUsesScrollButtons(True)

        # Create tabs
        self.tab_data = QtGui.QWidget()
        self.addTab(self.tab_data, "Data Viewer")

        # Initialize tab layouts
        self.tab_dataUI()

        # Setup stepping data variable
        self.step_data = 0

        # Create thread for updates
        # self.t_update = multiprocessing.Process(target=self.update())
        # self.t_update.start()

        self.connect_signals()

    def tab_dataUI(self):
        # Create panel objects
        layout = QtGui.QGridLayout()
        self.graph_panel = GraphPanel(self.radar, self.tracker)

        panel_list = [self.graph_panel]
        self.control_panel = ControlPanel(
            self.app, self.data_mgr, panel_list)

        # Create splitter widget
        h_split = QtGui.QSplitter(QtCore.Qt.Horizontal)

        # Add panels to splitter widget
        h_split.addWidget(self.control_panel)
        h_split.addWidget(self.graph_panel)

        layout.addWidget(h_split)

        self.tab_data.setLayout(layout)

    def connect_signals(self):
        self.data_mgr.reset_signal.connect(self.reset)

    # @profile(immediate=True)
    def update(self):
        # Do not update graphs is no new data is being produced
        if not self.data_mgr.source.paused or self.step_data:
            try:
                self.graph_panel.update()
                if self.data_mgr.source is self.data_mgr.virt_daq:
                    self.step_data -= 1  # decrease step from button once update occurs
            except Exception as e:
                print('Exception in update:', e)
                self.data_mgr.close()
                print(sys.last_traceback)

    def reset(self):
        """Reset all gui elements."""
        print('Graph Panel resetting.....')
        self.graph_panel.reset()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Space:
            self.control_panel.pause_button_handler()
        elif event.key() == QtCore.Qt.Key_R:
            self.data_mgr.reset()
            self.reset()
        elif event.key() == QtCore.Qt.Key_Escape:
            self.data_mgr.close()
            os.kill(os.getpid(), signal.SIGINT)
        elif event.key() == QtCore.Qt.Key_Right:
            self.control_panel.step_right_button_handler()
            self.step_data = 1
        event.accept()
