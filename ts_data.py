# -*- coding: utf-8 -*-
'''
ts_data.py
Contains TimeSeries class

Author: Jason Merlo
Maintainer: Jason Merlo (merlojas@msu.edu)
last_modified: 7/10/2018
'''
import numpy as np              # Storing data


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
    '''

    def __init__(self, length, shape, dtype=float):
        self.size = length  # Length of initial data buffer (in frames)
        self.frame_shape = shape  # Shape of single data frame
        self.dtype = dtype

        self.head_ptr = 0
        self._data = np.empty(
            (self.size,) + self.frame_shape, dtype=self.dtype)
        self.time = np.empty((self.size,) + self.frame_shape, dtype=float)

    @property
    def data(self):
        return self._data[:self.head_ptr]

    def append(self, data, time):
        '''
        Adds 'data' to the time-series data, doubles array size when full

        Args:
            data
                Data to be stored
            time
                Time at which the data was collected
        '''

        # Double array size
        if self.head_ptr >= self._data.shape[0] - 1:
            print('=========== DATASET DOUBLED ===========')
            # expand data
            tmp = self._data
            self._data = np.empty(self._data.shape[0] * 2, dtype=self.dtype)
            self._data[:tmp.shape[0]] = tmp
            # expand time
            tmp = self.time
            self.time = np.empty(self.time.shape[0] * 2, dtype=float)
            self.time[:tmp.shape[0]] = tmp

        # Update the long-term iq_data store buffer
        self._data[self.head_ptr] = data
        self.time[self.head_ptr] = time
        self.head_ptr += 1

    def clear(self):
        '''
        Removes data from array, but does not reduce its size
        '''
        self.head_ptr = 0
        self._data = np.empty((self._data.shape[0],)
                              + self.frame_shape, dtype=self.dtype)

    def __len__(self):
        return self.head_ptr
