"""
daq.py
Author: Jason Merlo

Dependencies: nidaqmx, random, threading, time
"""
try:
    import nidaqmx              # Used for NI-DAQ hardware
except ImportError:
    print('Warning: nidaqmx module not imported')
from threading import Thread    # Used for threading sampling function
from time import sleep          # Used for sleeping sampling thread
import numpy as np


class DAQ:
    def __init__(self, daq_type="nidaq",
                 sample_rate=44100, sample_size=4096,
                 # NI-DAQ specific
                 dev_string="Dev1/ai0:7",
                 sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS):
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
            try:
                # Try to create sampling task
                self.task = nidaqmx.Task()
                # List attached devices for debug and convenience
                print("NI-DAQ Devices:" + self.task.devices)

                self.task.ai_channels.add_ai_voltage_chan(dev_string)

                self.task.timing.cfg_samp_clk_timing(
                    sample_rate, sample_mode=sample_mode,
                    samps_per_chan=sample_size)

                self.fake_data = False

            except nidaqmx._lib.DaqNotFoundError:
                # On failure (ex. on mac/linux) generate random data for
                # development purposes
                # TODO: switch to PyDAQmx for mac/linux
                # TODO: is there any reason to keep nidaqmx for windows?
                # TODO: try performance comparison
                self.fake_data = True
                print("Warning: Using fake data as 'nidaqmx' is not supported "
                      "on this platform.")

        elif daq_type == "pyaudio":
            pass  # TODO insert pyaudio support here

        # Create data member to store samples
        self.data = np.empty((self.num_channels, self.sample_size),)

        # Spawn sampling thread
        self.running = True
        self.t_sampling = Thread(target=self.sample_loop)
        self.t_sampling.start()

    def sample_loop(self):
        """
        Calls get_samples forever
        """
        sleep_time = self.sample_size / self.sample_rate
        while self.running:
            self.get_samples()
            print("daq updated...")
            print("daq.running: ", self.running)
            sleep(sleep_time)
        print("Sampling thread stopped.")

    def get_samples(self):
        """
        Reads device sample buffers returning the specified sample size

        arguments:
        task -- nidaqmx task object, returned from open_task_channels()
        """
        if self.fake_data:
            self.data = np.random.randn(self.num_channels, self.sample_size)
        else:
            self.data = self.task.read(
                number_of_samples_per_channel=self.sample_size)

    def close(self, signal, frame):
        if self.daq_type == "nidaq" and self.fake_data is False:
            self.task.close()  # Close nidaq gracefully
        print("Stopping sampling thread...")
        self.running = False
