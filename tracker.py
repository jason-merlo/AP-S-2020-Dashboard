# -*- coding: utf-8 -*-
'''
tracker.py

Author: Jason Merlo
Maintainer: Jason Merlo (merlojas@msu.edu)
last_modified: 7/11/2018
'''
import numpy as np                      # Storing data
from ts_data import TimeSeries          # storing data
from geometry import Point, Circle      # storing geometric information


class Tracker2D(object):
    def __init__(self, radar_array):
        super(Tracker2D, self).__init__()
        # copy arguments into member variables
        self.array = radar_array

        init_length = 4096
        shape = (2,)
        self.ts_track = TimeSeries(init_length, shape, dtype=np.float32)

    def update_radius(self, index):
        pass

    def get_intersections(self, c1, c2):
        pass

    def update(self):
        data = np.random.randn(2) * 0.05
        self.ts_track.append(data, 0)

    def clear(self):
        pass
