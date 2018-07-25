# -*- coding: utf-8 -*-
'''
tracker.py

Author: Jason Merlo
Maintainer: Jason Merlo (merlojas@msu.edu)
last_modified: 7/25/2018
'''
import numpy as np                            # Storing data
from ts_data import TimeSeries                # storing data
from geometry import Point, Circle, Triangle  # storing geometric information
import itertools                              # 'triangulating' radar radii


class Tracker2D(object):
    def __init__(self, radar_array, start_loc=Point(0, 0, 0.14)):
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
        self.ts_track = TimeSeries(init_length, dtype=Point)

    def rho_to_r(self, rho, phi):
        return rho * np.sin(phi)

    def update_relative_positions(self, radar):
        '''
        Updates rho, phi, theta, and 2D projection, r, of tracked object
        relative to each radar object/module
        '''
        radar.rho_vec = self.loc - radar.loc
        print('rho_vec: ', radar.rho_vec)
        radar.r = Point(radar.rho_vec.x, radar.rho_vec.y).length

        radar.theta = np.arctan2(radar.rho_vec.y, radar.rho_vec.x)
        radar.phi = np.arctan(radar.rho_vec.z / radar.r)

        print('rho:{:+7.3}, phi:{:+7.3}, theta:{:+7.3}, r:{:+7.3}'.format(radar.rho_vec.length, radar.phi, radar.theta, radar.r))

    # TODO needs to use current loc for radii update
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
        radar.ts_r.append(radar.r, t)
        radial_vel = self.rho_to_r(radar.vmax, radar.phi)
        print('radial_vel: ', radial_vel)
        radar.ts_v.append(radial_vel, t)

        # Need a time delta (two samples) before position can be updated
        if len(radar.ts_data) > 1:
            dt = t - radar.ts_data.time[-2]
            r = radar.r  # radar.ts_r.data[-1]
            v = radar.ts_v.data[-1]
            a = radar.ts_a.data[-1]

            # Calculate radius and acceleration
            ap = (v - radar.ts_v.data[-2]) / dt
            rp = r + v * dt + 0.5 * a * dt**2
            radar.ts_a.append(ap, t)
            radar.ts_r.append(rp, t)
            print(
                'rp: {:+7.3f}, v: {:+7.3f}, ap: {:+7.3f}, dt: {:+7.3f}'\
                .format(rp, v, ap, dt))
        else:
            # Measure distance from origin to initial point on 2D plane
            p = self.loc
            p.z = 0
            r = p.distance()

            radar.ts_r.append(r, t)
            radar.ts_a.append(0, t)

    def update(self):
        '''
        Updates position of track based on differential position updates
        of each element in the array.
        '''
        sample_time = self.array.radars[0][0].ts_data.time[-1]

        for radar in itertools.chain(*self.array.radars):
            self.update_relative_positions(radar)
            self.update_radius(radar, sample_time)

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

            # Calculate all intersections, or nearest approximate intersection
            intersect = c1.intersections(c2)
            intersections.append(intersect)

        # Find triangle with lowest area
        potentials = itertools.product(*intersections)
        lowest_area = -1
        best_triangle = Triangle()
        for p in potentials:
            t = Triangle(*p)
            area = t.area
            if (area < lowest_area or lowest_area == -1):
                lowest_area = area
                best_triangle = t

        # Set centroid of best triangle to new location
        self.loc = best_triangle.centroid

        print('Current location:', self.loc)

        # Append new location to track
        self.ts_track.append(self.loc, sample_time)


    def clear(self):
        pass
