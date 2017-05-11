from __init__ import *

import sys
import subprocess
import numpy as np
from fractions import Fraction

sys.path.insert(0, ROOT)

from compiler import *
from constructs import *

def fm(pipe_data):

    N = Parameter(UInt, "N")
    SAMPLING_RATE = 250000000
    CUTOFF_FREQUENCY = 108000000
    NUM_TAPS = 64
    MAX_AMPLITUDE = 27000.0
    BANDWIDTH = 10000
    DECIMATION = 4

    pipe_data['N'] = N

    x = Variable(UInt, 'x')

    # input buffer
    fb1 = Wave(Double, "fb1", (DECIMATION + 1) * N + NUM_TAPS)

    # low pass filter
    lpf = Wave.firwin(NUM_TAPS, 2 * CUTOFF_FREQUENCY / SAMPLING_RATE, "lpf", div_by_sum=False)

    # filtered buffer
    fb2 = fb1.lfilter_fir_and_delay_down(lpf, DECIMATION + 1, "fb2")

    # output buffer
    fb3 = Wave(Double, "fb3", N, x)
    fb3.defn = [ ATan(fb2(x) * fb2(x + 1)) * MAX_AMPLITUDE * SAMPLING_RATE / (BANDWIDTH * Pi()) ]
    return fb3
