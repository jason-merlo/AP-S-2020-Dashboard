# -*- coding: utf-8 -*-
'''
radar_widget.py
Contains GUI panel classes for radar tracker dashboard

Author: Jason Merlo
Maintainer: Jason Merlo (merlojas@msu.edu)
last_modified: 7/10/2018
'''
# === Window / UI ===
import pyqtgraph as pg                  # Graph Elements
from pyqtgraph import QtCore, QtGui     # Qt Elements
from custom_ui import QHLine             # Horizontal dividers
# === GUI Panels ===
from radar_widget import RadarWidget


class GraphPanel(pg.LayoutWidget):
    def __init__(self, daq, radar_array):
        pg.LayoutWidget.__init__(self)

        # Copy member objects
        self.daq = daq
        self.radar_array = radar_array

        # Instantiate RadarWidget objects and widgets add to GraphPanel
        self.rw_array = []  # [row, col]
        for i,row in enumerate(self.radar_array.radars):
            rw_row = []
            for j,radar in enumerate(row):
                w = RadarWidget(self.daq, radar, vmax_len=100)
                rw_row.append(w)
                self.addWidget(rw_row[-1])
            self.rw_array.append(rw_row)
            self.nextRow()

        # Remove extra margins around plot widgets
        self.layout.setContentsMargins(0, 0, 0, 0)

    def update(self):
        for row in self.rw_array:
            for rw in row:
                rw.update()

    def reset(self):
        for row in self.rw_array:
            for rw in row:
                rw.reset()


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
        self.layout.addItem(QtGui.QSpacerItem(
            20, 30))
        self.nextRow()

        self.add_database_buttons()
        self.nextRow()
        self.layout.addItem(QtGui.QSpacerItem(
            20, 30))

        self.nextRow()
        self.add_dataset_buttons()
        self.nextRow()
        self.add_dataset_list()

        # Remove extra margins around button widgets
        self.layout.setContentsMargins(0, 0, 0, 0)

    def add_control_buttons(self):
        # Add label
        self.control_label = QtGui.QLabel('DAQ Controls')

        # Add buttons
        self.pause_button = QtGui.QPushButton('Start/Stop')
        self.pause_button.clicked.connect(self.pause_button_handler)
        self.reset_button = QtGui.QPushButton('Clear Data')
        self.reset_button.clicked.connect(self.reset_button_handler)

        # Add widgets to layout
        self.addWidget(self.control_label)
        self.nextRow()
        self.addWidget(QHLine())
        self.nextRow()
        self.addWidget(self.pause_button)
        self.nextRow()
        self.addWidget(self.reset_button)

        # Align widgets to top instead of center
        self.layout.setAlignment(self.pause_button, QtCore.Qt.AlignTop)
        self.layout.setAlignment(self.reset_button, QtCore.Qt.AlignTop)

    def add_database_buttons(self):
        # Add label
        self.database_label = QtGui.QLabel('Database Control')

        self.load_database_button = QtGui.QPushButton('Load Database...')
        self.load_database_button.clicked.connect(
            self.load_database_button_handler)
        self.save_database_as_button = QtGui.QPushButton('Save Database as...')
        self.save_database_as_button.clicked.connect(
            self.save_database_as_button_handler)

        # Add widgets to layout
        self.addWidget(self.database_label)
        self.nextRow()
        self.addWidget(QHLine())
        self.nextRow()

        self.addWidget(self.load_database_button)
        self.nextRow()
        self.addWidget(self.save_database_as_button)

    def add_dataset_buttons(self):
        # Add label
        self.dataset_label = QtGui.QLabel('Dataset Control')

        # Add buttons
        self.save_dataset_button = QtGui.QPushButton('Save Dataset')
        self.save_dataset_button.clicked.connect(
            self.save_dataset_button_handler)
        self.delete_dataset_button = QtGui.QPushButton('Delete Selected Dataset')
        self.delete_dataset_button.clicked.connect(
            self.delete_dataset_button_handler)

        # Add widgets to layout
        self.addWidget(self.dataset_label)
        self.nextRow()
        self.addWidget(QHLine())
        self.nextRow()

        self.addWidget(self.save_dataset_button)
        self.nextRow()
        self.addWidget(self.delete_dataset_button)

    def add_dataset_list(self):
        self.dataset_list = QtGui.QListWidget()
        # self.dataset_list.addItem("Item 1");
        # self.dataset_list.addItem("Item 2");
        # self.dataset_list.addItem("Item 3");
        # self.dataset_list.addItem("Item 4");
        self.dataset_list.itemClicked.connect(self.load_database_button_handler)

        # Add widget to main window
        self.addWidget(self.dataset_list)

    def load_database_button_handler(self):
        print("load database...")

    def save_dataset_button_handler(self):
        print("save dataset")

    def save_database_as_button_handler(self):
        print("save database as...")

    def delete_dataset_button_handler(self):
        print("delete dataset...")

    def pause_button_handler(self):
        if self.daq.pause:
            self.daq.pause = False
            print("DAQ running.")
        else:
            self.daq.pause = True
            print("DAQ paused.")

    def reset_button_handler(self):
        self.graph_panel.reset()
