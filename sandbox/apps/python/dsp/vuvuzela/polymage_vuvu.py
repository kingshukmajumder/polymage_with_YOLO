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
    ylpr = y.lfilter_fir_and_delay(taps, "ylpr")
    ylp = Wave(Double, "ylp", N - ntaps + 1, x)
    ylp.defn = [ ylpr(x) ]

    # Downsample the lowpass filtered signal by a factor of 5
    Fd = Fs//5
    yds = ylp.downsample(5, "yds")

    nyq_rate = Fd / 2.0
    ripple_db = 48.0 # Stopband attenuation in dB
    ntaps = 7238
    beta = Wave.kaiser_beta(ripple_db)

    win = Wave.get_window(('kaiser', beta), ntaps+1, "taps_window")

    cutoff_hz1 = 215 # Passband frequency 1 in Hz
    cutoff_hz2 = 255 # Passband frequency 2 in Hz

    # Design the filter
    taps1 = Wave.firwin(ntaps+1, (cutoff_hz1 / nyq_rate, cutoff_hz2 / nyq_rate), "taps1", window=win)

    # Filter the data and compensate for delay
    yf1r = yds.lfilter_fir_and_delay(taps1, "yf1r")
    M = yds.length
    yf1 = Wave(Double, "yf1", M - ntaps, x)
    yf1.defn = [ yf1r(x) ]

    cutoff_hz1 = 445 # Passband frequency 1 in Hz
    cutoff_hz2 = 485 # Passband frequency 2 in Hz

    # Design the filter
    taps2 = Wave.firwin(ntaps+1, (cutoff_hz1 / nyq_rate, cutoff_hz2 / nyq_rate), "taps2", window=win)

    # Filter the data and compensate for delay
    yf2r = yf1.lfilter_fir_and_delay(taps2, "yf2r")
    M = yf1.length
    yf2 = Wave(Double, "yf2", M - ntaps, x)
    yf2.defn = [ yf2r(x) ]

    cutoff_hz1 = 910 # Passband frequency 1 in Hz
    cutoff_hz2 = 950 # Passband frequency 2 in Hz

    # Design the filter
    taps3 = Wave.firwin(ntaps+1, (cutoff_hz1 / nyq_rate, cutoff_hz2 / nyq_rate), "taps3", window=win)

    # Filter the data and compensate for delay
    yf3r = yf2.lfilter_fir_and_delay(taps3, "yf3r")
    M = yf2.length
    yf3 = Wave(Double, "yf3", M - ntaps, x)
    yf3.defn = [ yf3r(x) ]

    cutoff_hz1 = 1840 # Passband frequency 1 in Hz
    cutoff_hz2 = 1880 # Passband frequency 2 in Hz

    # Design the filter
    taps4 = Wave.firwin(ntaps+1, (cutoff_hz1 / nyq_rate, cutoff_hz2 / nyq_rate), "taps4", window=win)

    # Filter the data and compensate for delay
    yf4r = yf3.lfilter_fir_and_delay(taps4, "yf4r")
    M = yf3.length
    yf4 = Wave(Double, "yf4", M - ntaps, x)
    yf4.defn = [ yf4r(x) ]

    # Upsample the signal to bring it back to the original sample rate
    yf = yf4.interp_fft(5, "yf")

    return yf
