# -*- coding: utf-8 -*-
'''
tracker.py

Author: Jason Merlo
Maintainer: Jason Merlo (merlojas@msu.edu)
last_modified: 7/12/2018
'''
import numpy as np                      # Storing data
from ts_data import TimeSeries          # storing data
from geometry import Point, Circle      # storing geometric information


class Tracker2D(object):
    def __init__(self, radar_array, r0_array):
        super(Tracker2D, self).__init__()
        # copy arguments into attributes
        self.array = radar_array

        # Initialize attributes
        # TODO initialize arrays of x, v, a, etc.

        init_length = 4096
        shape = (2,)
        self.ts_track = TimeSeries(init_length, shape, dtype=np.float32)

    def update_radius(self, index):
        radar = radar_array.radars[index]
        if len(radar.ts_data) > 1:
            dt = radar.ts_data.time[-1] - radar.ts_data.time[-2]
            radar.r += radar.v * dt + 0.5 * radar.a * dt**2
            radar.dr = radar.ts_vmax_data[-1]

    def rho_to_r(self, rho):
        pass

    def update(self):
        sample_time = self.radar_array.radars[0].ts_data.time[-1]
        data = np.random.randn(2) * 0.05
        self.ts_track.append(data, sample_time)

    def clear(self):
        pass
