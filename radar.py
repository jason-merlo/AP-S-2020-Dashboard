# -*- coding: utf-8 -*-
'''
radar.py
Contains Radar class and a RadarTypes class

Contains RadarArray class to hold timeseries data for voltage measurements,
FFT slices, and max frequency.

Author: Jason Merlo
Maintainer: Jason Merlo (merlojas@msu.edu)
last_modified: 7/5/2018
'''
import numpy as np          # Storing data
from ts_data import TimeSeries


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
    '''
    Radar object class containing information and useful functions for a single
    radar module.

    It is assumed radars will have both I and Q channels

    Attributes:
        daq
            daq_mgr object
        data
            ndarray of current data <num_channels x num_samples>
            one "frame" of data
        fft_data
            ndarray of fft's
    '''
    def __init__(daq, index, fft_size):
        # copy arguments into member variables
        self.daq=daq
        self.index=index
        self.fft_size=fft_size

        # initialize data arrays
        self.data=np.empty(2, self.daq.num_samples, dtype=RadarTypes.complex32)
        self.fft_data=np.empty(self.fft_size, dtype=RadarTypes.complex32)

    def compute_fft():
        '''
        compute fft and fft magnitude for plotting
        '''
        self.fft_complex=np.fft.fft(self.new_iq_data)
        # Display only magnitude
        fft_mag=np.square(fft_complex.real) + np.square(fft_complex.imag)

        # Adjust fft so DC is at the center
        center=int(fft_mag.shape[0] / 2)
        self.fft_data[0:center]=fft_mag[center - 1:-1]
        self.fft_data[center:-1]=fft_mag[0:center - 1]


class RadarArray:
    '''
    RadarArray holds timeseries data for voltage measurements,
    FFT slices, and max frequency.

    Attributes:
        daq
            daq_mgr object
        array_shape
            tuple containing dimensions of radar array
        fft_size
            size of FFT to compute
        ts_data
            timeseries data containing direct voltage measurements
        ts_fft_data
            timeseries data containing fft slices
        ts_fmax_data
            timeseries data containing max frequency points
    '''
    def __init__(daq, index, fft_size, array_shape):
        # copy arguments into member variables
        self.daq=daq
        self.index=index
        self.fft_size=fft_size

        # initial array size 4096 samples
        length=self.daq.sample_size * 4096
        shape=(self.daq.num_channels, self.daq.sample_size)
        self.ts_data=TimeSeries(length, shape, dtype=RadarTypes.complex32)
        self.ts_fft_data=TimeSeries(
            length, self.daq.num_channels, dtype=complex128)
        self.ts_fmax_data = TimeSeries(length, self.daq.num_channels)

        # create radar object array
        self.radars = [] # [row][col]
        for i in range(array_shape[1]):
            radar_row = []
            for j in range(array_shape[0]):
                index = array_shape[0] * j + i
                radar_row.append(Radar(daq, index, fft_size))
            self.radars.append(radar_row)

    def compute_ffts():
        '''
        Updates all FFTs in radar array
        '''
        for row in self.radars:
            for radar in row:
                radar.compute_fft()
