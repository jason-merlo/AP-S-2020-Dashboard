# -*- coding: utf-8 -*-
'''
radar.py
Contains Radar class and a RadarTypes class

Contains RadarArray class to hold timeseries data for voltage measurements,
FFT slices, and max frequency.

Author: Jason Merlo
Maintainer: Jason Merlo (merlojas@msu.edu)
last_modified: 7/25/2018
'''
import numpy as np              # Storing data
from ts_data import TimeSeries  # storing data
import scipy.constants as spc   # speed of light
from geometry import Point      # radar location

# DEBUG:
import sys


class RadarTypes(object):
    '''
    Class containing types pertaining to Radar objects

    Attributes:
        complex32
            32-bit complex data-type to align with the 16-bit samples from
            the nidaqmx - this saves space over the default complex128
    '''
    complex32 = np.dtype([('real', np.int16), ('imag', np.int16)])


class Radar(object):
    '''
    Radar object class containing information and useful functions for a single
    radar module.

    It is assumed radars will have both I and Q channels

    Attributes:
        daq
            daq_mgr object
        ts_data
        ts_drho
        cfft_data
        loc
            Point containing relative location
    '''

    def __init__(self, daq, index, fft_size, f0=24.150e9, loc=Point()):
        super(Radar, self).__init__()
        # copy arguments into attributes
        self.daq = daq
        self.index = index
        self.fft_size = fft_size
        self.first_update = True
        self.f0 = f0
        self.loc = loc

        # Initialize attributes
        self.bin_size = self.daq.sample_rate / self.fft_size
        self.center_bin = np.ceil(self.fft_size / 2)
        self.fmax = 0
        self.vmax = 0

        self.rho_vec = Point()
        self.phi = 0
        self.theta = 0
        self.r = 0  # 2D projection of rho onto azimuth plane

        # initial array size 4096 samples
        length = 4096
        data_shape = (2, self.daq.sample_size)

        # initialize data arrays
        self.ts_data = TimeSeries(length, data_shape, dtype=np.complex64)
        self.cfft_data = np.empty(fft_size, dtype=np.float32)

        # Initialize kinematics timeseries
        self.ts_drho = TimeSeries(length)
        self.ts_r = TimeSeries(length)
        self.ts_v = TimeSeries(length)
        self.ts_a = TimeSeries(length)

        # Generate FFT frequency labels
        self.fft_freqs = []
        for i in range(self.fft_size):
            self.fft_freqs.append(self.bin_to_freq(i))

        # Generate FFT velocity labels
        self.fft_velocities = []
        for i in self.fft_freqs:
            velocity = self.freq_to_vel(i)
            self.fft_velocities.append(velocity)

    def freq_to_vel(self, freq):
        '''
        Computes a velocity for the given frequency and the radar f0
        '''
        c = spc.speed_of_light
        return -(c * self.f0 / (freq + self.f0) - c)

    def bin_to_freq(self, bin):
        return (bin - self.center_bin) * self.bin_size

    def compute_cfft(self, data):
        '''
        compute fft and fft magnitude for plotting
        '''
        # Create complex data from input
        complex_data = data[0] + data[1] * 1j
        padded_data = np.zeros(self.fft_size, dtype=np.complex64)
        padded_data[:complex_data.size] = complex_data
        fft_complex = np.fft.fft(padded_data)
        # Display only magnitude
        fft_mag = np.linalg.norm([fft_complex.real, fft_complex.imag], axis=0)

        # Adjust fft so DC is at the center
        center = int(fft_mag.shape[0] / 2)
        fft_data = np.empty(fft_mag.shape)
        fft_data[:center] = fft_mag[center:]
        fft_data[center:] = fft_mag[:center]

        return fft_data

    def update(self):
        # Get sample time from DAQ
        if self.first_update:
            self.init_time = self.daq.time
            self.first_update = False
        sample_time = self.daq.time - self.init_time

        # Get data from DAQ
        slice = 2 * self.index
        self.ts_data.append(self.daq.data[slice:slice + 2], sample_time)

        # Calculate complex FFT (may be zero-padded if fft-size > sample_size)
        self.cfft_data = self.compute_cfft(self.ts_data.data[-1])

        vmax_bin = np.argmax(self.cfft_data).astype(np.int32)
        self.fmax = self.bin_to_freq(vmax_bin)
        self.vmax = self.freq_to_vel(self.fmax)
        self.ts_drho.append(self.vmax, sample_time)

    def clear(self):
        self.ts_data.clear()
        self.ts_drho.clear()


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
    '''

    def __init__(self, daq, array_shape, locations=None,
                 indices=None, fft_size=65536):
        '''
        Initializes radar array

        Args:
            daq
                daq_mgr object for acquisition parameters
            array_shape
                tuple containing array shape in x and y
            locations
                tuple of shape "array_shape" containing 2D Points
                describing the x and y location of each radar in m relative
                to an arbitrary origin
            array_indices [TODO]
                tuple of shape "array_shape" containing the DAQ indeces of the
                radars at the locations specified in the tuple
            fft_size
                zero-padded FFT size to be computed
        '''
        # copy arguments into member variables
        self.daq = daq
        self.fft_size = fft_size
        self.array_shape = array_shape
        self.locations = locations
        self.indices = indices
        self.initial_update = True

        # create radar object array
        self.radars = []  # [row][col]
        for i in range(array_shape[1]):
            radar_row = []
            for j in range(array_shape[0]):
                if self.locations:
                    loc = self.locations[i][j]
                else:
                    loc = None
                if self.indices:
                    index = self.indices[i][j]
                else:
                    index = array_shape[0] * j + i
                radar_row.append(Radar(daq, index, fft_size, loc=loc))
            self.radars.append(radar_row)

    def clear(self):
        for row in self.radars:
            for radar in row:
                radar.clear()

    def update(self):
        # Unused function - update is taken care of by widget
        for row in self.radars:
            for radar in row:
                radar.update()
