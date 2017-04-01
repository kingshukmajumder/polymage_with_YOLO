from __init__ import *

import sys
import subprocess
import numpy as np
from fractions import Fraction

sys.path.insert(0, ROOT)

from compiler import *
from constructs import *

def unwanted_spectral(pipe_data):

    N = Parameter(UInt, "N")
    Fs = Parameter(Double, "F") # Sample rate

    pipe_data['N'] = N
    pipe_data['F'] = Fs

    x = Variable(UInt, 'x')

    y = Wave(Double, "sig", N)

    nyq_rate = Fs / 2.0
    ripple_db = 95.0 # Stopband attenuation in dB
    ntaps = 670
    beta = Wave.kaiser_beta(ripple_db)

    cutoff_hz = 1000 # Passband frequency in Hz

    # Design the filter
    taps1 = Wave.firwin(ntaps, cutoff_hz / nyq_rate, "taps1", window=('kaiser', beta))

    # Filter the data and compensate for delay
    filtered_x = y.lfilter_fir(taps1, "filtered_sig")

    filtered_xw = Wave(Double, "filtered_sigw", y.length, x)
    filtered_xw.defn = [ filtered_x(x) ]
    ylp = filtered_xw.subset(ntaps - 1, N - 1, "ylp")

    # Downsample the lowpass filtered signal by a factor of 10
    Fd = Fs//10
    yds = ylp.downsample(10, "yds")

    nyq_rate = Fd / 2.0
    ripple_db = 60.0 # Stopband attenuation in dB
    ntaps = 3998
    beta = Wave.kaiser_beta(ripple_db)

    cutoff_hz1 = 55 # Passband frequency 1 in Hz
    cutoff_hz2 = 65 # Passband frequency 2 in Hz

    # Design the filter
    taps2 = Wave.firwin(ntaps+1, (cutoff_hz1 / nyq_rate, cutoff_hz2 / nyq_rate), "taps2", window=('kaiser', beta))

    # Filter the data and compensate for delay
    filtered_x1 = yds.lfilter_fir(taps2, "filtered_down_sig")

    M = yds.length
    ybs = Wave(Double, "ybs", M - ntaps, x)
    ybs.defn = [ filtered_x1(x + ntaps) ]

    # Upsample the signal to bring it back to the original sample rate
    yf = ybs.interp_fft(10, "yf")

    return yf
