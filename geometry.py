# -*- coding: utf-8 -*-
'''
geometry.py

Author: Jason Merlo
Maintainer: Jason Merlo (merlojas@msu.edu)
last_modified: 7/20/2018
'''
import numpy as np


class Point(object):
    def __init__(self, *args):
        self.p = args

    @property
    def p(self):
        return (self.x, self.y)

    @p.setter
    def p(self, *args):
        # Defult to origin if zero arguments provided
        self.x = 0
        self.y = 0
        self.z = 0
        alen = len(args)

        # if argument is tuple
        if alen == 1:
            try:
                self.x = args[0][0]
                self.y = args[0][1]
                # if tuple is 3D
                if len(args[0]) == 3:
                    self.z = args[0][2]
            except TypeError:
                raise TypeError('Point expects tuple, got', type(args[0]))
            #except all as e:
            #    raise(e)
        # if argument is 2D
        elif alen == 2:
            self.x = args[0]
            self.y = args[1]
        # if argument is 3D
        elif alen == 3:
            self.x = args[0]
            self.y = args[1]
            self.z = args[2]
        elif alen != 0:
            raise TypeError('Point expects at most three arguments, got', alen)

    def distance(self, a=None):
        '''
        Find distance between self and another Point
        '''
        # If no arguments provided, compare to origin
        if a is None:
            a = Point(0, 0)
        dx = self.x - a.x
        dy = self.y - a.y
        dz = self.z - a.z
        return np.sqrt(dx**2 + dy**2 + dz**2)

    def normalize(self):
        '''
        will convert Point into a vector of length 1
        '''
        len = self.length
        self.x /= len
        self.y /= len
        self.z /= len

    @property
    def length(self):
        '''
        Returns the distance of the point from the origin
        '''
        return np.sqrt(self.x**2 + self.y**2 + self.z**2)

    def __add__(self, a):
        self.x += a
        self.y += a
        self.z += a

    def __sub__(self, a):
        if isinstance(a, Point):
            print("POINT TYPE DETECTED....")
            self.x -= a.x
            self.y -= a.y
            self.z -= a.z
        else:
            self.x -= a
            self.y -= a
            self.z -= a

    def __mul__(self, a):
        self.x *= a
        self.y *= a
        self.z *= a

    def __div__(self, a):
        self.x /= a
        self.y /= a
        self.z /= a


class Circle(object):
    def __init__(self, *args):
        '''
        Circle class, holds Point and radius, also finds intersections

        Args:
            tuple
                (Point(), r)
            (or)
            Point()
                Point object containing center of circle
            r
                Number indicating radius of circle
        '''
        self.circle = args

    @property
    def circle(self):
        return (self.c, self.r)

    @circle.setter
    def circle(self, *args):
        # Default to unit circle if zero arguments provided
        self.c = Point(0, 0)
        self.r = 1

        alen = len(args)

        print("args: ", args)
        if alen == 1:
            self.c =args[0][0]
            self.r = args[0][1]
        elif alen == 2:
            self.c = args[0]
            self.r = args[1]
        elif alen == 3:
            self.c = Point(args[0], args[1])
            self.r = args[2]
        elif alen != 0:
            raise TypeError('Point expects at most three arguments, got', alen)

    def intersections(self, c):
        '''
        Finds the intersections of two circles, or the mid-point between
        their circumferences

        Based on the algorithm found at:
        http://paulbourke.net/geometry/circlesphere/

        Args:
            c
                the circle to calculate intersections with

        Returns:
            list of one or two Points
        '''
        # distance between centers
        dist = self.c.distance(c.c)

        # One circle is contained within the other
        if dist < np.absolute(self.r - c.r):
            if self.r > c.r:
                c1 = self.circle
                c2 = c.circle
            else:
                c1 = c.circle
                c2 = self.circle
            # get unit vector towards smaller circle within larger circle
            dir = c2.c - c1.c
            dir.normalize()
            # ditance between circumferences
            dc = c1.r - c2.r - dist
            mp_dist = dist + c2.r + dist / 2  # NOTE Changed mp_dist to dist

            result = [dir * mp_dist]
        # Circles intersect
        if dist < self.r + c.r:
            # distance to midpoint within both circumferences
            mp_dist = (self.r**2 - c.r**2 + 2 * dist) / 2 * dist
            # distance to intersection from midpoint
            height = np.sqrt(self.r**2 - mp_dist**2)
            # Point object between both circumferences
            # midpoint = self.c + mp_dist * (c.c - self.c) / 2
            # intersections
            P1 = Point()
            P2 = Point()
            P1.x = c.x + height * (c.c.y - self.c.y) / dist
            P1.y = c.y - height * (c.c.x - self.c.x) / dist
            P2.x = c.x - height * (c.c.y - self.c.y) / dist
            P2.y = c.y + height * (c.c.x - self.c.x) / dist
            result = [P1, P2]
        # circles do not intersect, and are not inside one another
        else:
            # Calculate unit vector in direction of second circle
            dir = c.c - self.c
            dir.normalize()
            dc = (dist - self.r - c.r) / 2
            mp_dist = dist - c.r - dc
            result = [dir * mp_dist]

        return result


class Triangle(object):
    def __init__(self, *args):
        self.points = args

    @property
    def points(self):
        return (self.p)

    @points.setter
    def points(self, *args):
        alen = len(args)
        if alen == 1:
            self.p = [args[0][0], args[0][1], args[0][2]]
        elif alen == 3:
            self.p = [args[0], args[1], args[2]]
        else:
            raise TypeError('Point expects at most three arguments, got', alen)

    @property
    def centroid(self):
        centroid = Point()
        for point in self.points:
            centroid.x += point.x
            centroid.y += point.y
        return centroid / 3

    @property
    def area(self):
        # shoelace formula
        p = self.points
        a = np.array([[p[0].x, p[1].x, p[2].x],
                     [p[0].y, p[1].y, p[2].y],
                     [1, 1, 1]])
        area = 0.5 * abs(np.linalg.det(a))
        return area
