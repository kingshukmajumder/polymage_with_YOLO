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
    # Downsample the lowpass filtered signal by a factor of 5
    Fd = Fs//5
    yds = y.lfilter_fir_and_delay_down(taps, 5, "yds")

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
    yf1 = yds.lfilter_fir_and_delay(taps1, "yf1")

    cutoff_hz1 = 425 # Passband frequency 1 in Hz
    cutoff_hz2 = 505 # Passband frequency 2 in Hz

    # Design the filter
    taps2 = Wave.firwin(ntaps+1, (cutoff_hz1 / nyq_rate, cutoff_hz2 / nyq_rate), "taps2", window=win)

    # Filter the data and compensate for delay
    yf2 = yf1.lfilter_fir_and_delay(taps2, "yf2")

    cutoff_hz1 = 650 # Passband frequency 1 in Hz
    cutoff_hz2 = 750 # Passband frequency 2 in Hz

    # Design the filter
    taps2_5 = Wave.firwin(ntaps+1, (cutoff_hz1 / nyq_rate, cutoff_hz2 / nyq_rate), "taps2_5", window=win)

    # Filter the data and compensate for delay
    yf2_5 = yf2.lfilter_fir_and_delay(taps2_5, "yf2_5")

    cutoff_hz1 = 870 # Passband frequency 1 in Hz
    cutoff_hz2 = 990 # Passband frequency 2 in Hz

    # Design the filter
    taps3 = Wave.firwin(ntaps+1, (cutoff_hz1 / nyq_rate, cutoff_hz2 / nyq_rate), "taps3", window=win)

    # Filter the data and compensate for delay
    yf3 = yf2_5.lfilter_fir_and_delay(taps3, "yf3")

    cutoff_hz1 = 1325 # Passband frequency 1 in Hz
    cutoff_hz2 = 1465 # Passband frequency 2 in Hz

    # Design the filter
    taps3_5 = Wave.firwin(ntaps+1, (cutoff_hz1 / nyq_rate, cutoff_hz2 / nyq_rate), "taps3_5", window=win)

    # Filter the data and compensate for delay
    yf3_5 = yf3.lfilter_fir_and_delay(taps3_5, "yf3_5")

    cutoff_hz1 = 1780 # Passband frequency 1 in Hz
    cutoff_hz2 = 1940 # Passband frequency 2 in Hz

    # Design the filter
    taps4 = Wave.firwin(ntaps+1, (cutoff_hz1 / nyq_rate, cutoff_hz2 / nyq_rate), "taps4", window=win)

    # Filter the data and compensate for delay
    yf4 = yf3_5.lfilter_fir_and_delay(taps4, "yf4", _out_typ=Complex)

    # Upsample the signal to bring it back to the original sample rate
    yf = yf4.interp_fft(5, "yf", _out_typ=Double)

    return yf
