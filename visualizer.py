# -*- coding: utf-8 -*-
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from pyqtgraph.Qt.QtWidgets import QWidget
import numpy as np
import DAQ
import signal
import sys

# === CONSTANTS ===============================================================
DAQ_SAMPLE_SIZE = 4096   # Hardware max = 4096
DAQ_SAMPLE_RATE = 50000  # Hz


class RadarWidget(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        layout = pg.GraphicsLayoutWidget()
        p3 = layout.addPlot()
        # Use automatic downsampling and clipping to reduce the drawing load
        p3.setDownsampling(mode='peak')
        p3.setClipToView(True)
        p3.setRange(xRange=[-100, 0])
        p3.setLimits(xMax=0)

        data3 = np.empty(100)
        ptr3 = 0


def update2():
    global data3, ptr3
    data3[ptr3] = np.random.normal()
    ptr3 += 1
    if ptr3 >= data3.shape[0]:
        tmp = data3
        data3 = np.empty(data3.shape[0] * 2)
        data3[:tmp.shape[0]] = tmp
    curve3.setData(data3[:ptr3])
    curve3.setPos(-ptr3, 0)

# update all plots


def update():
    update2()


# Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    pg.mkQApp()

    win = pg.GraphicsLayoutWidget()
    win.setWindowTitle('Quad-Radar')

    # 2) Allow data to accumulate. In these examples, the array doubles in
    #    length whenever it is full.
    p3 = win.addPlot()
    # Use automatic downsampling and clipping to reduce the drawing load
    p3.setDownsampling(mode='peak')
    p3.setClipToView(True)
    p3.setRange(xRange=[-100, 0])
    p3.setLimits(xMax=0)
    curve3 = p3.plot()

    data3 = np.empty(100)
    ptr3 = 0

    win.show()
    timer = pg.QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(50)

    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
