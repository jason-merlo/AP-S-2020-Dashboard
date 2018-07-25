# -*- coding: utf-8 -*-
'''
tracker_widget.py
Contains parametric graph capable of plotting a tracked object's path.

Author: Jason Merlo
Maintainer: Jason Merlo (merlojas@msu.edu)
last_modified: 7/25/2018
'''
import pyqtgraph as pg          # Used for RadarWidget superclass
import numpy as np              # Used for numerical operations
import time


class Tracker2DWidget(pg.GraphicsLayoutWidget):
    def __init__(self, tracker, xRange=[-0.20,0.20], yRange=[-0.20,0.20], trail=0):
        super(Tracker2DWidget, self).__init__()

        # Copy arguments to member variables
        self.tracker = tracker
        self.xRange = xRange
        self.yRange = yRange
        self.trail = trail

        # Add plots to layout
        self.plot = self.addPlot()

        # Set up plot
        self.plot.setRange(xRange=self.xRange, yRange=self.yRange)
        self.pw = self.plot.plot()
        self.plot.setLabel('left', text='Distance-Y', units='m')
        self.plot.setLabel('bottom', text='Distance-X', units='m')
        self.plot.setTitle('Tracker2D')

        self.plot.setAspectLocked(True)

        # Remove extra margins around plot
        self.ci.layout.setContentsMargins(0, 0, 0, 0)

    def update(self):
        # Update fmax graph
        self.tracker.update()
        data = self.tracker.ts_track.data[-self.trail:]
        data = np.array([(p.x, p.y) for p in data])
        self.pw.setData(data)

    def reset(self):
        self.tracker.ts_track.clear()
        self.update()
