# === Window / UI ===
import pyqtgraph as pg                  # Graph Elements
from pyqtgraph import QtCore, QtGui     # Qt Elements
# === GUI Elements ===
from GuiPanels import GraphPanel, ControlPanel

class DataWindow(pg.LayoutWidget):
    def __init__(self, daq, fft_size):
        pg.LayoutWidget.__init__(self)

        # Copy member objects
        self.daq = daq

        # Create layout
        self.setWindowTitle('Radar Tracking Visualizer')

        # Create panel objects
        self.graph_panel = GraphPanel(self.daq, fft_size)
        self.control_panel = ControlPanel(self.daq, self.graph_panel)

        # Create splitter widget
        h_split = QtGui.QSplitter(QtCore.Qt.Horizontal)

        # Add panels to splitter widget
        h_split.addWidget(self.control_panel)
        h_split.addWidget(self.graph_panel)

        # Add GUI items to window layout
        # self.addWidget(self.control_panel)
        # self.nextCol()
        # self.addWidget(self.graph_panel)
        self.addWidget(h_split)

    # Set gui update timer
    def update_gui(self):
        # Only update if new data is available
        if self.daq.data_available.is_set():
            self.graph_panel.update()
            # Clear event once GUI update ends
            self.daq.data_available.clear()
