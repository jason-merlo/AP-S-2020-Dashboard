# -*- coding: utf-8 -*-
import pyqtgraph as pg
import numpy as np
import time


class RadarWidget(pg.GraphicsLayoutWidget):
    def __init__(self, fmax_len, fft_pts, daq, index):
        super(RadarWidget, self).__init__()

        # Copy arguments to member variables
        self.fmax_len = fmax_len
        self.fft_pts = fft_pts
        self.daq = daq
        self.index = index
        self.update_period = daq.sample_size / daq.sample_rate

        # Add plots to layout
        self.fmax_plot = self.addPlot()
        self.nextRow()
        self.fft_plot = self.addPlot()

        # Use automatic downsampling and clipping to reduce the drawing load
        # Set up fmax plot
        self.fmax_plot.setDownsampling(mode='peak')
        self.fmax_plot.setClipToView(True)
        self.fmax_plot.setRange(xRange=[-100, 0])
        self.fmax_plot.setLimits(xMax=0)
        self.fmax_pw = self.fmax_plot.plot()
        # Set up fft plot
        self.fft_plot.setDownsampling(mode='peak')
        self.fft_plot.setClipToView(True)
        self.fft_plot.setRange(xRange=[0, fft_pts])
        self.fft_plot.setLimits(xMin=0, xMax=fft_pts)
        self.fft_pw = self.fft_plot.plot()

        # Set data and pointers for graphs
        self.fft_data = np.empty(fft_pts)
        self.fmax_data = np.empty(fmax_len)
        self.fmax_ptr = 0

        # Initialize data buffer
        initial_buffer_size = daq.sample_size * 16
        self.iq_data = np.empty(initial_buffer_size, dtype=complex)
        self.iq_data_ptr = 0

        # FPS ticker data
        self.lastTime = time.time()
        self.fps = None

    def update_data(self):
        self.iq_data_ptr += self.daq.sample_size

        if self.iq_data_ptr >= self.iq_data.shape[0]:
            tmp = self.iq_data
            self.iq_data = np.empty(self.iq_data.shape[0] * 2, dtype=complex)
            self.iq_data[:tmp.shape[0]] = tmp

        if self.daq.data.shape == \
                (self.daq.num_channels, self.daq.sample_size):
            fmax_left_ptr = self.iq_data_ptr - self.daq.sample_size
            index = (self.index * 2)

            self.iq_data[fmax_left_ptr:self.iq_data_ptr] \
                = self.daq.data[index] + (self.daq.data[index + 1] * 1j)

    def update_fmax(self):
        self.fmax_ptr += 1

        if self.fmax_ptr >= self.fmax_data.shape[0]:
            tmp = self.fmax_data
            self.fmax_data = np.empty(self.fmax_data.shape[0] * 2)
            self.fmax_data[:tmp.shape[0]] = tmp

        self.fmax_data[self.fmax_ptr] = np.argmax(self.fft_data)
        self.fmax_pw.setData(self.fmax_data[:self.fmax_ptr])
        self.fmax_pw.setPos(-self.fmax_ptr, 0)

        pass

    def update_fft(self):
        fmax_left_ptr = self.iq_data_ptr - self.fft_pts
        if fmax_left_ptr < 0:
            fmax_left_ptr = 0
        fft_complex = np.fft.fft(self.iq_data[fmax_left_ptr:self.iq_data_ptr])
        # show only positive data
        # fft_complex = fft_complex[int(fft_complex.size / 2):-1]
        self.fft_data = np.square(fft_complex.real) + \
            np.square(fft_complex.imag)
        self.fft_pw.setData(self.fft_data)

    def update_fps(self):
        now = time.time()
        dt = now - self.lastTime
        self.lastTime = now
        if self.fps is None:
            self.fps = 1.0 / dt
        else:
            s = np.clip(dt * 3., 0, 1)
            self.fps = self.fps * (1 - s) + (1.0 / dt) * s
        self.fmax_plot.setTitle('%0.2f fps' % self.fps)

    def update(self):
        self.update_data()
        self.update_fft()
        self.update_fmax()
        self.update_fps()
        print("graphing updated...")
