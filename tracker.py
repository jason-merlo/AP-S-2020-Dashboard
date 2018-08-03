# -*- coding: utf-8 -*-
'''
tracker.py

Author: Jason Merlo
Maintainer: Jason Merlo (merlojas@msu.edu)
last_modified: 7/31/2018
'''
import numpy as np                            # Storing data
from ts_data import TimeSeries                # storing data
from geometry import Point, Circle, Triangle  # storing geometric information
import itertools                              # 'triangulating' radar radii
import math
import sys


class Tracker2D(object):
    def __init__(self, daq, radar_array, start_loc=Point(0.0, 0.0, 0.1794)):
        '''
        Args:
        radar_array
            Array of radar objects, tuple matching physical layout
        start_loc
            Point indicating the initial location of the object to track
        '''
        super(Tracker2D, self).__init__()
        # copy arguments into attributes
        self.daq = daq
        self.array = radar_array
        self.loc = start_loc

        init_length = 4096
        self.ts_track = TimeSeries(init_length, dtype=Point)

    def rho_to_r(self, rho, phi):
        '''
           r
        ______
        |    /
        |   /
        |  / rho
        |_/
        |/phi

        '''
        return rho * np.sin(phi)

    def update_relative_positions(self, radar):
        '''
        Updates rho, phi, theta, and 2D projection, r, of tracked object
        relative to each radar object/module

        NOTE: Math varified
        '''
        radar.rho_vec = self.loc - radar.loc
        radar.r = Point(radar.rho_vec.x, radar.rho_vec.y).length

        radar.theta = np.arctan2(radar.rho_vec.y, radar.rho_vec.x)
        print(radar.rho_vec)
        assert(radar.rho_vec.z > 0), 'Implausibility: rho_vec.z <= 0'
        radar.phi = np.arctan(radar.r / radar.rho_vec.z)

        # print('rho:{:+7.3}, phi:{:+7.3}, theta:{:+7.3}, r:{:+7.3}'.format(
            # radar.rho_vec.length, radar.phi, radar.theta, radar.r))

    def update_radius(self, radar, t):
        '''
        Calculates new radii for each radar in the array based on the
        differential position update of the doppler radar.

        Args:
            radar
                Radar object to update
            t
                Time of update
        '''

        # Append new 2D data
        if len(radar.ts_v) > 0:
            radial_vel = self.rho_to_r(radar.vmax, radar.phi) * 0.5 + radar.ts_v[-1] * 0.5
        else:
            radial_vel = self.rho_to_r(radar.vmax, radar.phi)
        radar.ts_v.append(radial_vel, t)

        # Need a time delta (two samples) before position can be updated
        if len(radar.ts_a) > 0:
            dt = radar.ts_data.time[-1] - radar.ts_data.time[-2]
            r = radar.r  # radar.ts_r.data[-1]
            v = radar.ts_v.data[-1]
            a = radar.ts_a.data[-1]

            # Calculate radius and acceleration
            ap = (v - radar.ts_v.data[-2]) / dt
            rp = r + v * dt + 0.5 * a * dt**2
            radar.ts_a.append(ap, t)
            radar.ts_r.append(rp, t)
            print(
                'new values: r: {:+7.3f}, v: {:+7.3f}, a: {:+7.3f}, dt: {:+7.3f}'
                .format(rp, v, ap, dt))
        else:
            # Append initial values
            radar.ts_r.append(radar.r, t)
            radar.ts_a.append(0, t)

    def update(self):
        '''
        Updates position of track based on differential position updates
        of each element in the array.
        '''
        # Loop through all new data that has arrived in the buffer
        buffer = self.daq.buffer
        for i in range(len(buffer)):

            print('Tracker update ran.')

            # Get new radar data
            data = buffer.pop()
            self.array.update(data)

            # Check to see if this is the first loop
            # Cannot update without time delta (two loops)
            if len(self.array.radars[0][0].ts_r) > 0:
                intersections = []
                # flatten radars list for combinations
                flat_array = itertools.chain(*self.array.radars)

                # find intersections between radar circles
                for radar_pair in itertools.combinations(flat_array, 2):
                    # Get most recent radius data
                    r1 = radar_pair[0].ts_r.data[-1]
                    r2 = radar_pair[1].ts_r.data[-1]

                    # Get radar locations
                    p1 = radar_pair[0].loc
                    p2 = radar_pair[1].loc

                    # Create circle objects from radar information
                    c1 = Circle(p1, r1)
                    c2 = Circle(p2, r2)
                    # print(c1)
                    # print(c2)

                    # Calculate all intersections, or nearest approximate intersection
                    intersect = c1.intersections(c2)  #TODO check for zero bias
                    # print(intersect)
                    # print('='*50)
                    intersections.append(intersect)

                # Find triangle with lowest area
                potentials = itertools.product(*intersections)
                lowest_area = -1
                best_triangle = Triangle()
                for p in potentials:
                    t = Triangle(*p)
                    area = t.area  # TODO Cehck for zero bias
                    if (area < lowest_area or lowest_area == -1):
                        lowest_area = area
                        best_triangle = t

                # Set centroid of best triangle to new location
                self.loc.x = best_triangle.centroid.x  # TODO check for zero bias
                self.loc.y = best_triangle.centroid.y

                if not math.isnan(self.loc.x):
                    # print('Current location:', self.loc)
                    pass
                else:
                    print('Nan encountered, exiting...')
                    self.array.daq.close()
                    sys.exit(0)

            # Append new location to track
            p = Point(*self.loc.p)

            sample_time = self.array.radars[0][0].ts_data.time[-1]
            self.ts_track.append(p, sample_time)

            for i, radar in enumerate(itertools.chain(*self.array.radars)):
                # print("=== RADAR {:} ===".format(i))
                self.update_relative_positions(radar)
                self.update_radius(radar, sample_time)

    def reset(self):
        self.ts_track.clear()
        self.array.reset()
        self.loc = Point(0.0, 0.0, 0.1794)
