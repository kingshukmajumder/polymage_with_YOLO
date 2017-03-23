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
    Fs = Parameter(Double, "F")

    pipe_data['N'] = N
    pipe_data['F'] = Fs

    x = Variable(UInt, 'x')

    y = Wave(Double, "sig", N)

    nyq_rate = Fs / 2.0
    ripple_db = 95.0
    ntaps = 670
    beta = Wave.kaiser_beta(ripple_db)

    cutoff_hz = 1000
    taps1 = Wave.firwin(ntaps, cutoff_hz / nyq_rate, "taps1", window=('kaiser', beta))
    a = Wave(Double, "a", 1)
    a.defn = [ 1.0 ]
    filtered_x = y.lfilter_fir(taps1, "filtered_sig")

    ylp = Wave(Double, "ylp", N - ntaps + 1, x)
    ylp.defn = [ filtered_x(x + ntaps - 1) ]

    Fd = Fs//10
    yds = ylp.upfirdn(a, "yds", down=10)

    nyq_rate = Fd / 2.0
    ripple_db = 60.0
    ntaps = 3998
    beta = Wave.kaiser_beta(ripple_db)

    cutoff_hz1 = 55
    cutoff_hz2 = 65
    taps2 = Wave.firwin(ntaps+1, (cutoff_hz1 / nyq_rate, cutoff_hz2 / nyq_rate), "taps2", window=('kaiser', beta))
    filtered_x1 = yds.lfilter_fir(taps2, "filtered_down_sig")

    M = yds.length
    ybs = Wave(Double, "ybs", M - ntaps, x)
    ybs.defn = [ filtered_x1(x + ntaps) ]

    yf = ybs.interp_fft(10, "yf")

    return yf
