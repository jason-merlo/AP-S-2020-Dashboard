# -*- coding: utf-8 -*-
'''
geometry.py

Author: Jason Merlo
Maintainer: Jason Merlo (merlojas@msu.edu)
last_modified: 7/12/2018
'''
class Point(object):
    def __init__(self, *args):
        self.l = args

    @property
    def l(self):
        return (self.x, self.y)

    @l.setter
    def l(self, *args):
        # Defult to origin if zero arguments provided
        self.x, self.y, self.z = 0

        # if argument is tuple
        if alen == 1:
            if type(args[0]) != type(touple()):
                raise TypeError('Point expects tuple, got', type(args[0]))
            self.x = args[0][0]
            self.y = args[0][1]
            # if tuple is 3D
            if len(args[0]) == 3:
                self.z = args[0][2]
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

    def distance(self, a):
        '''
        Find distance between self and another Point
        '''
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
        self.circle = args

    @property
    def circle(self):
        return (self.c, self.r)

    @circle.setter
    def circle(self, *args):
        # Default to unit circle if zero arguments provided
        self.c = Point()
        self.r = 1

        alen = len(args)
        if alen == 1:
            self.c = Point(args[0][0], args[0][1])
            self.r = args[0][2]
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
            mp_dist = dist + c2.r + mp_dist / 2

            result = [dir * mp_dist]
        # Circles intersect
        if dist < self.r + c.r:
            # distance to midpoint within both circumferences
            mp_dist = (self.r**2 - c.r**2 + 2* dist) / 2 * dist
            # distance to intersection from midpoint
            height = np.sqrt(self.r**2 - mp_dist**2)
            # Point object between both circumferences
            midpoint = self.c + mp_dist * (c.c - self.c) / 2
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
            self.p = (args[0][0], args[0][1], args[0][2])
        elif alen == 3:
            self.p = Point(args[0], args[1])
            self.r = args[2]
        else:
            raise TypeError('Point expects at most three arguments, got', alen)

    @property
    def centroid(self):
        centroid = Point()
        for point in self.points:
            centroid.x += point.x
            centroid.y += point.y
        return centroid / 3
