# -*- coding: utf-8 -*-
'''
tracker.py

Author: Jason Merlo
Maintainer: Jason Merlo (merlojas@msu.edu)
last_modified: 7/23/2018
'''
import numpy as np                      # Storing data
from ts_data import TimeSeries          # storing data
from geometry import Point, Circle      # storing geometric information
import itertools                        # 'triangulating' radar radii


class Tracker2D(object):
    def __init__(self, radar_array, start_loc=Point(0, 0, 0.2)):
        '''
        Args:
        radar_array
            Array of radar objects, tuple matching physical layout
        start_loc
            Point indicating the initial location of the object to track
        '''
        super(Tracker2D, self).__init__()
        # copy arguments into attributes
        self.array = radar_array
        self.loc = start_loc

        init_length = 4096
        shape = (2,)
        self.ts_track = TimeSeries(init_length, shape, dtype=np.float32)

    def update_radius(self, radar, t):
        # Append current velocity reading
        radar.ts_v.append(radar.ts_vmax, t)

        # Need a time delta (two samples) before position can be updated
        if len(radar.ts_data) > 1:
            dt = t - radar.ts_data.time[-2]
            r = radar.ts_r[-1]
            v = radar.ts_v[-1]
            a = radar.ts_a[-1]

            # Calculate radius and acceleration
            radar.ts_a.append(v - radar.ts_v[-2], t)
            radar.ts_r.append(r + v * dt + 0.5 * a * dt**2, t)
        else:
            # Measure distance from origin to initial point on 2D plane
            p = self.loc
            p.z = 0
            r = p.distance()

            radar.ts_r.append(r, t)
            radar.ts_a.append(0, t)

    def rho_to_r(self, rho, phi):
        return rho * np.sin(phi)

    def update(self):
        sample_time = self.array.radars[0][0].ts_data.time[-1]

        for radar in self.array:
            self.update_radius(radar)

        intersections = []
        # flatten radars list for combinations
        flat_array = itertools.chain(*self.array)
        # find intersections between radar circles
        for radar_pair in itertools.combinations(flat_array):
            r1 = radar_pair[0].ts_r[-1]
            r2 = radar_pair[1].ts_r[-1]
            p1 = radar_pair[0].loc
            p2 = radar_pair[1].loc
            c1 = Circle(p1, r1)
            c2 = Circle(p2, r2)

            intersections = c1.intersections(c2)
            self.intersections.append(intersections)

        # Find closest points in intersections
        # potential list contains (centroid, mse)
        potential_list = []
        for intersect_points in intersections:
            potential = self.argmin_mse(intersect_points, intersections)
            potential_list.append(potential)

        # grab potential centroid with lowest associated mse
        sorted_potentials = sorted(potential_list, key=lambda x: x[1])
        self.loc = sorted_potentials[0][0]

        # Append new location to track
        self.ts_track.append(self.loc, sample_time)

    def argmin_mse(self, a, b):
        '''
        returns a list of tuples containing (centroid, mse)
        '''
        for p1 in a:                     # point 1
            for p_list in b:             # list of other points
                if p_list != b:
                    for p2 in p_list:    # point 2
                        pass

    def clear(self):
        pass
