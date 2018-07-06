# -*- coding: utf-8 -*-
'''
radar.py
Contains Radar class and a RadarTypes class

Contains RadarArray class to hold timeseries data for voltage measurements,
FFT slices, and max frequency.

Author: Jason Merlo
Maintainer: Jason Merlo (merlojas@msu.edu)
last_modified: 7/6/2018
'''
import numpy as np              # Storing data
from ts_data import TimeSeries  # storing data
import time                     # computing sample time
import scipy.constants as spc   # speed of light


class RadarTypes(object):
    '''
    Class containing types pertaining to Radar objects

    Attributes:
        complex32
            32-bit complex data-type to align with the 16-bit samples from
            the nidaqmx - this saves space over the default complex128
    '''
    complex32 = \
        np.dtype((np.int32, {'real': (np.int16, 2), 'imag': (np.int16, 2)}))


class Radar(object):
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
    '''
    def __init__(self, daq, index, fft_size, f0=24.150e9):
        super(Radar, self).__init__()
        # copy arguments into member variables
        self.daq=daq
        self.index=index
        self.fft_size=fft_size
        self.first_update=True
        self.f0 = f0

        # initial array size 4096 samples
        length=4096
        shape=(2, self.daq.sample_size)

        # initialize data arrays
        self.ts_data=TimeSeries(length, shape, dtype=complex)
        self.ts_fft_data=TimeSeries(length, shape, dtype=float)
        self.ts_fmax_data=TimeSeries(length, (), dtype=float)

        # Generate FFT frequency labels
        self.fft_freqs=[]
        center=np.ceil(self.fft_size / 2)
        bin_size=self.daq.sample_rate / self.daq.sample_size
        for i in range(self.fft_size):
            freq=(i - center) * bin_size
            self.fft_freqs.append(freq)

        # Generate FFT velocity labels
        self.fft_velocities=[]
        for i in self.fft_freqs:
            velocity=self.compute_velocity(i)
            self.fft_velocities.append(velocity)

    def compute_velocity(self, freq):
        '''
        Computes a velocity for the given frequency and the radar f0
        '''
        c=spc.speed_of_light
        return c * self.f0 / (freq + self.f0) - c

    def compute_cfft(self, data):
        '''
        compute fft and fft magnitude for plotting
        '''
        fft_complex=np.fft.fft(data)
        # Display only magnitude
        fft_mag=np.square(fft_complex.real) + np.square(fft_complex.imag)

        # Adjust fft so DC is at the center
        center=int(fft_mag.shape[0] / 2)
        fft_data = np.empty(fft_mag.shape)
        fft_data[0:center]=fft_mag[center - 1:-1]
        fft_data[center:-1]=fft_mag[0:center - 1]

        return fft_data

    def update(self):
        if self.first_update:
            self.init_time=self.daq.time
        sample_time=self.daq.time - self.init_time

        # Append samples, FFT, and max frequency
        slice = 2*self.index
        self.ts_data.append(self.daq.data[slice:slice+2], sample_time)
        cfft = self.compute_cfft(self.ts_data.data[-1])
        self.ts_fft_data.append(cfft, sample_time)
        max_freq_bin=np.argmax(self.ts_fft_data.data)
        self.ts_fmax_data.append(max_freq_bin, sample_time)
        print("max: ", self.ts_fmax_data.data[-1])

    def clear(self):
        self.ts_data.clear()
        self.ts_fft_data.clear()


class RadarArray(object):
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
    def __init__(self, daq, array_shape, fft_size=65536):
        #super(Radar, self).__init__()
        # copy arguments into member variables
        self.daq=daq
        self.fft_size=fft_size
        self.initial_update=True

        # create radar object array
        self.radars=[]  # [row][col]
        for i in range(array_shape[1]):
            radar_row=[]
            for j in range(array_shape[0]):
                index=array_shape[0] * j + i
                radar_row.append(Radar(daq, index, fft_size))
            self.radars.append(radar_row)

    def clear(self):
        for row in self.radars:
            for radar in row:
                radar.clear()

    def update(self):
        for row in self.radars:
            for radar in row:
                radar.update()
