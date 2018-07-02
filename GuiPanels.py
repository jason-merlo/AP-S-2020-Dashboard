# === Window / UI ===
import pyqtgraph as pg                  # Graph Elements
from pyqtgraph import QtCore, QtGui     # Qt Elements
from CustomUi import QHLine             # Horizontal dividers
# === GUI Panels ===
from RadarWidget import RadarWidget

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
        # self.nextRow()
        # Add spacer item to shift all buttons to top of screen
        # self.verticalSpacer = QtGui.QSpacerItem(
        #     0, 0, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        # self.layout.addItem(self.verticalSpacer)

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

        # Align widgets to top instead of center
        # self.layout.setAlignment(self.load_database_button, QtCore.Qt.AlignTop)
        # self.layout.setAlignment(self.save_dataset_button, QtCore.Qt.AlignTop)
        # self.layout.setAlignment(
        #     self.save_database_as_button, QtCore.Qt.AlignTop)

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
