from __init__ import *

import sys
import subprocess
import numpy as np
from fractions import Fraction

sys.path.insert(0, ROOT)

from compiler import *
from constructs import *

def low_pass(pipe_data):

    N = Parameter(UInt, "N")
    C = Parameter(Double, "C")
    F = Parameter(Double, "F")

    pipe_data['N'] = N
    pipe_data['C'] = C
    pipe_data['F'] = F

    x = Variable(UInt, 'x')

    sig = Wave(Double, "sig", N, x)
    hs = sig.fft("hs")

    fs = Wave.fftfreq(N, "fs")

    hs_lp = Wave(Complex, "hs_lp", N / 2 + 1, x)
    cond1 = Condition(fs(x), '>', C)
    cond2 = Condition(fs(x), '<=', C)
    hs_lp.defn = [ Case(cond1, hs(x) * F), \
                   Case(cond2, hs(x)) ]
    scaled_sig = hs_lp.ifft("scaled_sig", N)

    out_sig = Wave(Double, "out_sig", N, x)
    out_sig.defn = [ scaled_sig(x) / N ]

    out_sig2 = Wave.fftfreq(N, "out_sig2", real_input=False)

    return out_sig, out_sig2
