# -*- coding: utf-8 -*-
"""
daq_mgr.py
Author: Jason Merlo

Dependencies: nidaqmx, random, threading, time
"""
try:
    import nidaqmx              # Used for NI-DAQ hardware
    from nidaqmx import stream_readers
except ImportError:
    print('Warning: nidaqmx module not imported')
import threading                # Used for creating thread and sync events
import time                     # Used for tracking update fps
from time import sleep          # Used for sleeping sampling thread
import numpy as np


class DAQ:
    def __init__(self, daq_type="nidaq",
                 sample_rate=44100, sample_size=4096,
                 # NI-DAQ specific
                 dev_string="Dev1/ai0:7", fake_data=False,
                 sample_mode=nidaqmx.constants.AcquisitionType.FINITE):
        """
        Creates sampling task on DAQ and opens I & Q channels for the four
        radars

        arguments:
        dev_string -- device and ports to initialize (default: "Dev1/ai0:7")
        sample_rate -- frequency in Hz to sample at (default: 44100)
        sample_mode -- finite or continuous acquisition (default: finite)
        sample_size -- size of chunk to read (default/max: 4095)
        """

        # Copy member data
        # General arguments
        self.sample_rate = sample_rate
        self.sample_size = sample_size
        self.daq_type = daq_type
        self.fake_data = fake_data
        self.pause = False  # Start running by default

        # Create sevent for controlling draw events only when there is new data
        self.data_available = threading.Event()

        # Device specific arguments
        if daq_type == "nidaq":
            self.sample_mode = sample_mode
            self.dev_string = dev_string
            # Get number of channels to sample
            if self.dev_string[-2] == ':':
                self.num_channels = int(
                    self.dev_string[-1]) - int(self.dev_string[-3]) + 1
            else:
                self.num_channels = int(self.dev_string[-1]) + 1

            # Create new sampling task
            if not fake_data:
                try:
                    # Try to create sampling task
                    self.task = nidaqmx.Task()

                    self.task.ai_channels.add_ai_voltage_chan(dev_string)

                    self.task.timing.cfg_samp_clk_timing(
                        sample_rate, sample_mode=sample_mode,
                        samps_per_chan=sample_size)
                    self.in_stream = \
                        stream_readers.AnalogMultiChannelReader(
                            self.task.in_stream)
                except nidaqmx._lib.DaqNotFoundError:
                    # On failure (ex. on mac/linux) generate random data for
                    # development purposes
                    # TODO: switch to PyDAQmx for mac/linux
                    # TODO: is there any reason to keep nidaqmx for windows?
                    # TODO: try performance comparison
                    self.fake_data = True
                    print("Warning: Using fake data as 'nidaqmx' is not "
                          "supported on this platform.")

        elif daq_type == "pyaudio":
            pass  # TODO insert pyaudio support here

        # Create data member to store samples
        self.data = np.empty((self.num_channels, self.sample_size),)

        # Spawn sampling thread
        self.running = True
        self.t_sampling = threading.Thread(target=self.sample_loop)
        self.t_sampling.start()

        self.last_time = 0

    def sample_loop(self):
        """
        Calls get_samples forever
        """
        while self.running:
            if self.pause:
                time.sleep(0.1)  # sleep 100 ms
            else:
                self.get_samples()
        print("Sampling thread stopped.")

    def start_sampling(self):
        self.thread = threading.Thread(target=self.get_samples)
        self.thread.start()

    def get_samples(self):
        """
        Reads device sample buffers returning the specified sample size

        arguments:
        task -- nidaqmx task object, returned from open_task_channels()
        """
        # print("DAQ updated...")

        if self.fake_data:
            sleep_time = self.sample_size / self.sample_rate
            self.data = np.random.randn(
                self.num_channels, self.sample_size) * 0.001 + \
                np.random.randn(1) * 0.001 + 0.01
                self.time = time.time_ns()
            sleep(sleep_time)
        else:
            try:
                self.in_stream.read_many_sample(
                    self.data,
                    number_of_samples_per_channel=nidaqmx.constants.READ_ALL_AVAILABLE,
                    timeout=1.0)
                self.time = time.time_ns()
            except nidaqmx.errors.DaqError:
                print("DAQ exception caught: Sampling too fast.")
        # Set the update event to True once data is read in
        self.data_available.set()

    def close(self):
        print("Stopping sampling thread...")
        if self.daq_type == "nidaq" and self.fake_data is False:
            self.task.close()  # Close nidaq gracefully
        self.running = False
        self.thread.join()
