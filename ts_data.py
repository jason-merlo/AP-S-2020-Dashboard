# -*- coding: utf-8 -*-
'''
ts_data.py
Contains TimeSeries class

Author: Jason Merlo
Maintainer: Jason Merlo (merlojas@msu.edu)
last_modified: 7/31/2018
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

    def __init__(self, length, shape=(), dtype=np.float32):
        self.size = length  # Length of initial data buffer (in frames)
        self.frame_shape = shape  # Shape of single data frame
        self.dtype = dtype

        self.head_ptr = 0
        self._data = np.empty(
            (self.size,) + self.frame_shape, dtype=self.dtype)
        self._time = np.empty((self.size,), dtype=float)

    @property
    def data(self):
        return self._data[:self.head_ptr]

    @property
    def time(self):
        return self._time[:self.head_ptr]

    @property
    def shape(self):
        '''
        Returns the shape of a single data frame
        '''
        return self.frame_shape

    @property
    def type(self):
        '''
        Returns the type of data stored
        '''
        return self.dtype

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
            new_shape = ((self._data.shape[0] * 2),) + self._data.shape[1:]
            print('== NEW SIZE --> {:}'.format(new_shape[0]))
            self._data = np.empty(new_shape, dtype=self.dtype)
            self._data[:tmp.shape[0]] = tmp
            # expand time
            tmp = self._time
            self._time = np.empty(self._time.shape[0] * 2, dtype=float)
            self._time[:tmp.shape[0]] = tmp

        # Update the long-term iq_data store buffer
        self._data[self.head_ptr] = data
        self._time[self.head_ptr] = time
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

    def __getitem__(self, i):
        return self.data[i]
