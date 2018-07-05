# -*- coding: utf-8 -*-
import pyqtgraph as pg          # Used for RadarWidget superclass
import numpy as np              # Used for numerical operations TODO move to new class
import time                     # Used for FPS calculations


class RadarWidget(pg.GraphicsLayoutWidget):
    def __init__(self, daq, radar, fmax_len=100):
        super(RadarWidget, self).__init__()

        # Copy arguments to member variables
        self.daq = daq
        self.radar = radar
        self.fmax_len = fmax_len
        self.index = index * 2
        self.update_period = daq.sample_size / daq.sample_rate

        # Add plots to layout
        self.fmax_plot = self.addPlot()
        self.nextRow()
        self.fft_plot = self.addPlot()

        # Calculate reasonable ranges for FFT peak outputs
        fft_len = self.radar.fft_size
        fft_xrange = [fft_len / 2 - fft_len / 25, fft_len / 2 + fft_len / 25]
        fft_yrange = [fft_len / 2 - fft_len / 50, fft_len / 2 + fft_len / 50]

        # Set up fmax plot
        self.fmax_plot.setDownsampling(mode='peak')
        self.fmax_plot.setClipToView(True)
        self.fmax_plot.setRange(xRange=[-fmax_len, 0], yRange=fft_yrange)
        self.fmax_plot.setLimits(xMax=0)
        self.fmax_pw = self.fmax_plot.plot()

        # Set up fft plot
        self.fft_plot.setDownsampling(mode='peak')
        self.fft_plot.setClipToView(True)
        self.fft_plot.setLogMode(x=False, y=True)  # Log Y-axis of FFT views
        self.fft_plot.setRange(disableAutoRange=True,
                               xRange=fft_xrange, yRange=[-6, 8])
        self.fft_plot.setLimits(xMin=0, xMax=fft_size, yMin=-1e8, yMax=1e8)
        self.fft_pw = self.fft_plot.plot()
        self.fft_line = pg.InfiniteLine(angle=90, movable=False)
        self.fft_plot.addItem(self.fft_line)

        # FPS ticker data
        self.lastTime = time.time()
        self.fps = None


    def update_fmax(self):
        max_freq_bin = np.argmax(self.radar.ts_fft_data)
        self.fmax_data[self.fmax_ptr] = max_freq_bin
        self.fmax_pw.setData(self.fmax_data[:self.fmax_ptr])
        self.fmax_pw.setPos(-self.fmax_ptr, 0)

        # update FFT line with result of argmax
        self.fft_line.setValue(max_freq_bin)

    def clear_fmax(self):
        self.fmax_data = np.full((self.fmax_len,), self.fft_size / 2)
        self.fmax_ptr = 0

    def update_fft(self):
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

        self.fft_pw.setData(self.fft_data)

    def clear_fft(self):
        self.fft_data = np.zeros(self.fft_size)
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
        self.update_fps()
        self.update_data()
        self.update_fft()
        self.update_fmax()

    def reset(self):
        self.clear_data()
        self.clear_fft()
        self.clear_fmax()
        # When paused, redraw after reset
        if self.daq.pause:
            self.update()
