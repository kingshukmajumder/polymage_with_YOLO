from __init__ import *

import sys
import subprocess
import numpy as np
from fractions import Fraction

sys.path.insert(0, ROOT)

from compiler import *
from constructs import *

def vuvu(pipe_data):

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

    cutoff_hz = 4000 # Passband frequency in Hz

    # Design the filter
    taps = Wave.firwin(ntaps, cutoff_hz / nyq_rate, "taps", window=('kaiser', beta))

    # Filter the data and compensate for delay
    filtered_x = y.lfilter_fir(taps, "filtered_sig")

    filtered_xw = Wave(Double, "filtered_sigw", y.length, x)
    filtered_xw.defn = [ filtered_x(x) ]
    ylp = filtered_xw.subset(ntaps - 1, N - 1, "ylp")

    # Downsample the lowpass filtered signal by a factor of 5
    Fd = Fs//5
    yds = ylp.downsample(5, "yds")

    nyq_rate = Fd / 2.0
    ripple_db = 48.0 # Stopband attenuation in dB
    ntaps = 7238
    beta = Wave.kaiser_beta(ripple_db)

    cutoff_hz1 = 215 # Passband frequency 1 in Hz
    cutoff_hz2 = 255 # Passband frequency 2 in Hz

    # Design the filter
    taps1 = Wave.firwin(ntaps+1, (cutoff_hz1 / nyq_rate, cutoff_hz2 / nyq_rate), "taps1", window=('kaiser', beta))

    # Filter the data and compensate for delay
    filtered_x1 = yds.lfilter_fir(taps1, "filtered_sig1")

    M = yds.length
    yf1 = Wave(Double, "yf1", M - ntaps, x)
    yf1.defn = [ filtered_x1(x + ntaps) ]

    cutoff_hz1 = 445 # Passband frequency 1 in Hz
    cutoff_hz2 = 485 # Passband frequency 2 in Hz

    # Design the filter
    taps2 = Wave.firwin(ntaps+1, (cutoff_hz1 / nyq_rate, cutoff_hz2 / nyq_rate), "taps2", window=('kaiser', beta))

    # Filter the data and compensate for delay
    filtered_x2 = yf1.lfilter_fir(taps2, "filtered_sig2")

    M = yf1.length
    yf2 = Wave(Double, "yf2", M - ntaps, x)
    yf2.defn = [ filtered_x2(x + ntaps) ]

    cutoff_hz1 = 910 # Passband frequency 1 in Hz
    cutoff_hz2 = 950 # Passband frequency 2 in Hz

    # Design the filter
    taps3 = Wave.firwin(ntaps+1, (cutoff_hz1 / nyq_rate, cutoff_hz2 / nyq_rate), "taps3", window=('kaiser', beta))

    # Filter the data and compensate for delay
    filtered_x3 = yf2.lfilter_fir(taps3, "filtered_sig3")

    M = yf2.length
    yf3 = Wave(Double, "yf3", M - ntaps, x)
    yf3.defn = [ filtered_x3(x + ntaps) ]

    cutoff_hz1 = 1840 # Passband frequency 1 in Hz
    cutoff_hz2 = 1880 # Passband frequency 2 in Hz

    # Design the filter
    taps4 = Wave.firwin(ntaps+1, (cutoff_hz1 / nyq_rate, cutoff_hz2 / nyq_rate), "taps4", window=('kaiser', beta))

    # Filter the data and compensate for delay
    filtered_x4 = yf3.lfilter_fir(taps4, "filtered_sig4")

    M = yf3.length
    yf4 = Wave(Double, "yf4", M - ntaps, x)
    yf4.defn = [ filtered_x4(x + ntaps) ]

    # Upsample the signal to bring it back to the original sample rate
    yf = yf4.interp_fft(5, "yf")

    return yf
