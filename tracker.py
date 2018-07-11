# -*- coding: utf-8 -*-
'''
tracker2d.py

Author: Jason Merlo
Maintainer: Jason Merlo (merlojas@msu.edu)
last_modified: 7/10/2018
'''
import numpy as np              # Storing data
from ts_data import TimeSeries  # storing data


class Tracker2D(object):
    def __init__(self):
        super(Tracker2D, self).__init__()
        # copy arguments into member variables
        init_length = 4096
        shape = (2,)
        self.ts_track = TimeSeries(init_length, shape, dtype=np.float32)

    def update(self):
        data = np.random.randn(2) * 0.05
        self.ts_track.append(data, 0)

    def clear(self):
        pass
