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
        '''
        Calculates radii for each radar in the array.

        Args:
            radar
                Radar object to update
            t
                Time of update
        '''
        # Append current velocity reading
        radar.ts_v.append(radar.vmax, t)

        # Need a time delta (two samples) before position can be updated
        if len(radar.ts_data) > 1:
            dt = t - radar.ts_data.time[-2]
            r = radar.ts_r.data[-1]
            v = radar.ts_v.data[-1]
            a = radar.ts_a.data[-1]

            # Calculate radius and acceleration
            radar.ts_a.append(v - radar.ts_v.data[-2], t)
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

        for radar in itertools.chain(*self.array.radars):
            self.update_radius(radar, sample_time)

        intersections = []
        # flatten radars list for combinations
        flat_array = itertools.chain(*self.array.radars)
        # find intersections between radar circles
        for radar_pair in itertools.combinations(flat_array, 2):
            r1 = radar_pair[0].ts_r.data[-1]
            r2 = radar_pair[1].ts_r.data[-1]
            p1 = radar_pair[0].loc
            p2 = radar_pair[1].loc
            c1 = Circle(p1, r1)
            c2 = Circle(p2, r2)

            intersect = c1.intersections(c2)
            intersections.append(intersect)

        # Find triangle with lowest area
        potentials = itertools.product(*intersections)
        lowest_area = -1
        best_triangle = Triangle()
        for p in potentials:
            t = Triangle(*p)
            area = t.area
            if (area < lowest_area and lowest_area != -1):
                lowest_area = area
                best_triangle = t

        # Set centroid of best triangle to new location
        self.loc = best_triangle.centroid

        # Append new location to track
        self.ts_track.append(self.loc, sample_time)

    def clear(self):
        pass
