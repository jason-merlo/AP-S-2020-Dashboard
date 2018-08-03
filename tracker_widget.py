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
from geometry import Point, Circle


class Tracker2DWidget(pg.GraphicsLayoutWidget):
    def __init__(self, tracker, xRange=[-0.10,0.10], yRange=[-0.10,0.10], trail=1):
        super(Tracker2DWidget, self).__init__()

        # Copy arguments to member variables
        self.tracker = tracker
        self.xRange = xRange
        self.yRange = yRange
        self.trail = trail

        # Add plots to layout
        self.plot = self.addPlot()

        # Add radar location markers
        self.radar_loc_plot = pg.ScatterPlotItem(size=10, pen=pg.mkPen(None), brush=pg.mkBrush(255, 255, 0, 255))

        for radar in self.tracker.array:
            loc = (radar.loc.x, radar.loc.y)
            self.radar_loc_plot.addPoints(pos=[loc])

        self.plot.addItem(self.radar_loc_plot)

        # Add radar detection radius circles
        self.radar_rad_plots = []
        for i in range(len(self.tracker.array)):
            curve = pg.PlotCurveItem()

            # Add initial radii
            radar = self.tracker.array[i]
            self.draw_circle(curve, Circle(radar.loc, radar.r))

            # Add to list to keep track
            self.radar_rad_plots.append(curve)

            # Add to plot
            self.plot.addItem(curve)

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
        data = self.tracker.ts_track.data[-self.trail:]
        data = np.array([(p.x, p.y) for p in data])
        self.pw.setData(data, pen=pg.mkPen({'color': "FFF", 'width': 2}))
        # Update tracker radii
        for i, pt in enumerate(self.radar_rad_plots):
            radar = self.tracker.array[i]
            vel = radar.vmax/10 #radar.ts_r[-1] #radar.vmax/10
            if vel < 0:
                self.draw_circle(pt, Circle(radar.loc, -vel), color="FFAAAA16")
            else:
                self.draw_circle(pt, Circle(radar.loc, vel))

    def reset(self):
        self.tracker.reset()
        self.update()

    def draw_circle(self, curve, cir, num_pts=50, color="AAFFFF16"):
        '''
        adds a Circle, c, to the plot
        '''
        x_list = []
        y_list = []
        two_pi = 2 * np.pi
        for i in range(num_pts):
            ang = two_pi * (i/num_pts)
            x = (np.cos(ang) * cir.r/2) + cir.c.x
            y = (np.sin(ang) * cir.r/2) + cir.c.y
            x_list.append(x)
            y_list.append(y)
        # append first point to end to 'close' circle
        x_list.append(x_list[0])
        y_list.append(y_list[0])

        x = np.array(x_list)
        y = np.array(y_list)

        pixel_size = self.ppm()
        curve.setData(x, y, pen=pg.mkPen({'color': color, 'width': cir.r*pixel_size}))

    def ppm(self):
        '''
        pixels per meter
        '''
        pixels = self.frameGeometry().width() - 50
        meters = self.plot.vb.viewRange()[0][1] - self.plot.vb.viewRange()[0][0]
        return pixels / meters
