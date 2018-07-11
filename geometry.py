# -*- coding: utf-8 -*-
'''
geometry.py

Author: Jason Merlo
Maintainer: Jason Merlo (merlojas@msu.edu)
last_modified: 7/11/2018
'''
class Point(object):
    def __init__(self, *args):
        self.l = args

    @property
    def l(self):
        return (self.x, self.y)

    @l.setter
    def l(self, *args):
        self.x, self.y, self.z = None

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
        else:
            raise TypeError('Point expects at most three arguments, got', alen)


class Circle(object):
    def __init__(self, *args):
        self.c = args

    @property
    def c(self):
        return (self.c, self.r)

    @c.setter
    def c(self, *args):
        alen = len(args)
        if alen == 1:
            self.p = Point(args[0][0], args[0][1])
            self.r = args[0][2]
        elif alen == 2:
            self.p = args[0]
            self.r = args[1]
        elif alen == 3:
            self.p = Point(args[0], args[1])
            self.r = args[2]
        else:
            raise TypeError('Point expects at most three arguments, got', alen)
