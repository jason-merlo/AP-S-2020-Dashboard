# -*- coding: utf-8 -*-
'''
radar_widget.py
Contains RadarWidget class used to draw the max frequency and FFT graphs

Author: Jason Merlo
Maintainer: Jason Merlo (merlojas@msu.edu)
last_modified: 7/10/2018
'''
import pyqtgraph as pg          # Used for RadarWidget superclass
import numpy as np              # Used for numerical operations
import time                     # Used for FPS calculations


class RadarWidget(pg.GraphicsLayoutWidget):
    def __init__(self, daq, radar, vmax_len=100):
        super(RadarWidget, self).__init__()

        # Copy arguments to member variables
        self.daq = daq
        self.radar = radar
        self.vmax_len = vmax_len
        self.update_period = daq.sample_size / daq.sample_rate

        # Add plots to layout
        self.vmax_plot = self.addPlot()
        self.nextRow()
        self.fft_plot = self.addPlot()

        # Calculate reasonable ranges for FFT peak outputs
        fft_len = self.radar.fft_size
        # fft_xrange = [fft_len / 2 - fft_len / 25, fft_len / 2 + fft_len / 25]
        # fft_yrange = [fft_len / 2 - fft_len / 50, fft_len / 2 + fft_len / 50]
        fft_xrange = [-2e3, 2e3]
        fft_yrange = [-1.5e3, 1.5e3]

        # Set up fmax plot
        self.vmax_plot.setDownsampling(mode='peak')
        self.vmax_plot.setClipToView(True)
        self.vmax_plot.setRange(xRange=[-vmax_len, 0], yRange=[-10, 10])
        self.vmax_plot.setLimits(
            xMax=0, yMax=20, yMin=-20)
        self.vmax_pw = self.vmax_plot.plot()
        self.vmax_plot.setLabel('left', text="Velocity", units="m/s")
        self.vmax_ax_bottom = self.vmax_plot.getAxis('bottom')
        self.vmax_ax_bottom.setScale(self.update_period)
        self.vmax_plot.setLabel('bottom', text="Time", units="s")

        # Set up fft plot
        self.fft_plot.setDownsampling(mode='peak')
        self.fft_plot.setClipToView(True)
        self.fft_plot.setLogMode(x=False, y=True)  # Log Y-axis of FFT views
        self.fft_plot.setRange(disableAutoRange=True,
                               xRange=fft_xrange, yRange=[-5, 6])
        self.fft_plot.setLimits(
            xMin=fft_xrange[0], xMax=fft_xrange[1], yMin=-8, yMax=10)
        self.fft_pw = self.fft_plot.plot()
        self.fft_line = pg.InfiniteLine(angle=90, movable=False)
        self.fft_plot.addItem(self.fft_line)
        self.fft_ax_bottom = self.fft_plot.getAxis('bottom')
        self.fft_ax_bottom.setScale(1 / self.radar.bin_size)
        self.fft_plot.setLabel('bottom', text="Frequency", units="Hz")
        self.fft_plot.setLabel('left', text="Power", units="W")

        # FPS ticker data
        self.lastTime = time.time()
        self.fps = None

    def update_vmax(self):
        # Update fmax graph
        vmax_data = self.radar.ts_vmax_data.data
        vmax_ptr = self.radar.ts_vmax_data.head_ptr
        self.vmax_pw.setData(vmax_data)
        self.vmax_pw.setPos(-vmax_ptr, 0)

        # draw max FFT line
        self.fft_line.setValue(self.radar.fmax)
        self.vmax_plot.setTitle('Max Velocity:\t{:+0.4f} (m/s)'.format(vmax_data[-1]))

    def update_fft(self):
        self.fft_pw.setData(self.radar.cfft_data)
        self.fft_pw.setPos(-self.radar.center_bin, 0)
        self.fft_plot.setTitle('Max Frequency:\t{:+0.4f} (Hz)'.format(self.radar.fmax))

    def update_fps(self):
        now = time.time()
        dt = now - self.lastTime
        self.lastTime = now
        if self.fps is None:
            self.fps = 1.0 / dt
        else:
            s = np.clip(dt * 3., 0, 1)
            self.fps = self.fps * (1 - s) + (1.0 / dt) * s
        # self.vmax_plot.setTitle('%0.2f fps' % self.fps)
        print('%0.2f fps' % self.fps)

    def update(self):
        self.radar.update()
        self.update_fft()
        self.update_vmax()
        self.update_fps()

    def reset(self):
        self.radar.clear()
        # When paused, redraw after reset
        if self.daq.pause:
            self.update()
