# -*- coding: utf-8 -*-
"""
daq_mgr.py
Author: Jason Merlo
"""
import threading                # Used for creating thread and sync events
import time                     # Used for tracking update fps
from time import sleep          # Used for sleeping sampling thread
import numpy as np


class DataManager(object):
    def __init__(self):
        self.source_index = 0
        self.source_list = []
        self.source = None

    def add_source(self):
        self.source_list.append()

    def set_source_index(self, index):
        if index < len(self.source_list) and index >=0:
            self.source_index = index
        else:
            raise IndexError('Source index out of bounds:', index)

    def set_source(self, source):
        if source not in source_list:
            self.add_source(source)
        self.source = source
        self.source_index = len(source_list) - 1

    def get_source(self):
        return self.source

    def get_source_index(self):
        return self.source_index

    def reset(self):
        self.source.reset()

    def pause(self):
        self.source.pause()

    def run(self):
        self.source.run()

    def close(self):
        for source in self.source_list:
            source.close()
