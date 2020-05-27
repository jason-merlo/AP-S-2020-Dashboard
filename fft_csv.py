# Loads in DAQami CSV and plots FFT

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import EngFormatter
import sys

channel = [1, 3, 5, 7, 0, 2, 4, 6]

def read_csv(fname, skip_lines=7, skip_cols=2, sample_rate_idx=(5,0), sample_count_idx=(3,0), channel_count_idx=(2,0)):
    fp = open(fname)

    for line_num, line in enumerate(fp):
        if line_num == channel_count_idx[0]:
            num_channels = int(line.split(':')[-1].strip('"\n'))
            print('num_channels:', num_channels)
        elif line_num == sample_count_idx[0]:
            num_samples = int(line.split(':')[-1].strip('"\n'))
            print('num_samples:', num_samples)
            samples = np.empty((num_samples, num_channels))
        elif line_num == sample_rate_idx[0]:
            sample_rate = int(line.split(':')[-1].strip('"\n'))
            print('sample_rate:', sample_rate)
        elif line_num < skip_lines:
            continue
        else:
            val_list = line.replace('"', '').split(',')[skip_cols:]
            vals = np.array(val_list, dtype=float)
            samples[line_num - skip_lines,:] = vals

    return samples, sample_rate

def process_fft(data, sample_rate=50000, chunk_size=5000, fft_size=2**17):

    num_chunks = data.shape[0] // chunk_size
    print('num_chunks', num_chunks)
    bin_size = sample_rate / fft_size
    print('bin_size:', bin_size)

    formatter1 = EngFormatter(places=1, sep="\N{THIN SPACE}")  # U+2009

    ax = plt.subplot(111)

    for idx in range(num_chunks):
        start = idx * chunk_size
        end = (idx+1) * chunk_size
        data_slice = data[start:end, 0] + data[start:end, 1] * 1.0j

        fft_complex = np.fft.fft(data_slice, fft_size)
        fft_freq = np.fft.fftfreq(fft_size, d=1/sample_rate)
        fft_mag = np.linalg.norm([fft_complex.real, fft_complex.imag], axis=0)

        ax.clear()
        ax.plot(fft_freq, fft_mag)
        ax.set_yscale('log')
        ax.xaxis.set_major_formatter(formatter1)
        ax.set_xlabel('Frequency (Hz)')
        # ax.set_xlim([-100, 100])
        ax.set_ylim([0.1, 500])

        plt.pause(0.25)

    plt.show()

def main():
    data, sample_rate = read_csv(sys.argv[1])
    process_fft(data[:, channel[0:2]], sample_rate)

if __name__ == "__main__":
    main()
