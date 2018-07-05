# -*- coding: utf-8 -*-
'''
ts_data.py
Contains TimeSeries class

Author: Jason Merlo
Maintainer: Jason Merlo (merlojas@msu.edu)
last_modified: 7/3/2018
'''
import numpy as np          # Storing data


class TimeSeries:
    '''Time series data class

    This module contains the TimeSeries data class which stores timeseries
    data in a convenient manner.

    Attributes:
        data
            numpy array of data frames
        time
            numpy array of timestamps data were taken
        head_ptr
            pointer to head index of time and data arrays
        complex32
            numpy type for complex 32-bit data
    '''

    __init__(self, length, shape, dtype=float):
        self.size = length  # Length of initial data buffer (in frames)
        self.frame_shape = shape  # Shape of single data frame

        self.data = np.empty(length, frame_shape, dtype=self.complex32)

    append(self, data, time):
        '''
        Adds 'data' to the time-series data, doubles array size when full

        Args:
            data
                Data to be stored
            time
                Time at which the data was collected
        '''
        # Update the long-term iq_data store buffer
        self.head_ptr += self.shape[0]

        # Double array size
        if self.head_ptr >= self.data.shape[0]:
            tmp = self.data
            self.data = np.empty(self.data.shape[0] * 2, dtype=self.complex32)
            self.data[:tmp.shape[0]] = tmp

        # Insert data into array
        left_ptr = self.head_ptr - self.shape[0]
        self.data[left_ptr:self.iq_data_ptr] = data[:self.size[0]]

    clear(self):
        '''
        Removes data from array, but does not reduce its size
        '''
        self.head_ptr = 0
        self.data = np.zeros(self.data.size())
