# -*- coding: utf-8 -*-
'''
radar.py
Contains Radar class and a RadarTypes class

Author: Jason Merlo
Maintainer: Jason Merlo (merlojas@msu.edu)
last_modified: 7/3/2018
'''
import numpy as np          # Storing data


class RadarTypes:
    '''
    Class containing types pertaining to Radar objects

    Attributes:
        complex32
            32-bit complex data-type to align with the 16-bit samples from
            the nidaqmx - this saves space over the default complex128
    '''
    self.complex32 =
        np.dtype((np.int32, {'real': (np.int16, 0), 'imag': (np.int16, 2)})


class Radar:
    pass
