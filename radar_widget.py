# -*- coding: utf-8 -*-
'''
radar_widget.py
Contains RadarWidget class used to draw the max frequency and FFT graphs

Author: Jason Merlo
Maintainer: Jason Merlo (merlojas@msu.edu)
last_modified: 7/6/2018
'''
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
        self.fft_plot.setLimits(xMin=0, xMax=fft_len, yMin=-1e8, yMax=1e8)
        self.fft_pw = self.fft_plot.plot()
        self.fft_line = pg.InfiniteLine(angle=90, movable=False)
        self.fft_plot.addItem(self.fft_line)

        # FPS ticker data
        self.lastTime = time.time()
        self.fps = None


    def update_fmax(self):
        # Update fmax graph
        fmax_data = self.radar.ts_fmax_data.data
        self.fmax_pw.setData(fmax_data)
        self.fmax_pw.setPos(-self.fmax_len, 0)

        # update max FFT line with result of argmax
        self.fft_line.setValue(fmax_data[-1])

    def update_fft(self):
        self.fft_pw.setData(self.radar.ts_fft_data.data[-1])

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
        self.radar.update()
        self.update_fft()
        self.update_fmax()
        self.update_fps()

    def reset(self):
        self.radar.clear()
        # When paused, redraw after reset
        if self.daq.pause:
            self.update()
