# -*- coding: utf-8 -*-
# === Window / UI ===
import pyqtgraph as pg                  # Graph Elements
from pyqtgraph import QtCore, QtGui     # Qt Elements
# === GUI Elements ===
from gui_panels import GraphPanel, ControlPanel, Tracker2DPanel


class DataWindow(QtGui.QTabWidget):
    def __init__(self, daq, radar_array, tracker, parent=None):
        super(DataWindow, self).__init__(parent)
        # Copy member objects
        self.daq = daq
        self.radar_array = radar_array
        self.tracker = tracker

        # Setup window
        self.setWindowTitle('Radar Tracking Visualizer')

        # Create tabs
        self.tab_data = QtGui.QWidget()
        self.tab_tracker2d = QtGui.QWidget()
        self.addTab(self.tab_data, "Data Viewer")
        self.addTab(self.tab_tracker2d, "Tracker2D")

        # Initialize tab layouts
        self.tab_dataUI()
        self.tab_tracker2dUI()

    def tab_dataUI(self):
        # Create panel objects
        layout = QtGui.QGridLayout()
        self.graph_panel = GraphPanel(self.daq, self.radar_array)
        self.control_panel = ControlPanel(self.daq, self.graph_panel)

        # Create splitter widget
        h_split = QtGui.QSplitter(QtCore.Qt.Horizontal)

        # Add panels to splitter widget
        h_split.addWidget(self.control_panel)
        h_split.addWidget(self.graph_panel)

        layout.addWidget(h_split)

        self.tab_data.setLayout(layout)

    def tab_tracker2dUI(self):
        # Create panel objects
        layout = QtGui.QGridLayout()
        self.tracker2d_widget = Tracker2DPanel(self.tracker)
        layout.addWidget(self.tracker2d_widget)

        self.tab_tracker2d.setLayout(layout)

    # Set gui update timer
    def update_gui(self):
        # Only update if new data is available
        if self.daq.data_available.is_set():
            self.graph_panel.update()
            self.tracker2d_widget.update()
            # Clear DAQ event once GUI update ends
            self.daq.data_available.clear()
