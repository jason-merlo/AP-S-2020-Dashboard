# -*- coding: utf-8 -*-
'''
radar.py
Contains Radar class and a RadarTypes class

Author: Jason Merlo
Maintainer: Jason Merlo (merlojas@msu.edu)
last_modified: 7/5/2018
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
    '''
    Radar object class containing information and useful functions for a single
    radar module.

    Attributes:
        daq
            daq_mgr object
        current_data
            ndarray of current data <num_channels x num_samples>
            one "frame" of data
        current_fft_data
            ndarray of fft's
    '''

    def __init__(daq, index, fft_size):
        # copy arguments into member variables
        self.daq = daq
        self.index = index
        self.fft_size = fft_size

        # initialize data arrays
        self.current_data = np.empty(2, self.daq.num_samples)
        self.current_fft = np.empty(self.fft_size)

    def compute_fft():
        fmax_left_ptr = self.iq_data_ptr - self.fft_size
        if fmax_left_ptr < 0:
            fmax_left_ptr = 0
        fft_complex = np.fft.fft(self.new_iq_data)
        # show only positive data
        # fft_complex = fft_complex[int(fft_complex.size / 2):-1]
        fft_mag = np.square(fft_complex.real) + \
            np.square(fft_complex.imag)

        # Adjust fft so it is biased at the center
        center = int(fft_mag.shape[0] / 2)
        self.fft_data[0:center] = fft_mag[center - 1:-1]
        self.fft_data[center:-1] = fft_mag[0:center - 1]
