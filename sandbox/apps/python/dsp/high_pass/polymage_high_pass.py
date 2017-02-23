from __init__ import *

import sys
import subprocess
import numpy as np
from fractions import Fraction

sys.path.insert(0, ROOT)

from compiler import *
from constructs import *

def high_pass(pipe_data):

    N = Parameter(UInt, "N")
    C = Parameter(Double, "C")
    F = Parameter(Double, "F")

    pipe_data['N'] = N
    pipe_data['C'] = C
    pipe_data['F'] = F

    x = Variable(UInt, 'x')

    sig = Wave(Double, "sig", N, x)
    hs = sig.fft("hs")

    fsran = Interval(UInt, 0, N / 2)
    fs = Function(([x], [fsran]), Double, "fs")
    fs.defn = [ Cast(Double, x) / N ]

    hs_hp = Wave(Complex, "hs_hp", N / 2 + 1, x)
    cond1 = Condition(fs(x), '<', C)
    cond2 = Condition(fs(x), '>=', C)
    hs_hp.defn = [ Case(cond1, hs(x) * F), \
                   Case(cond2, hs(x)) ]
    scaled_sig = hs_hp.ifft("scaled_sig", N)

    out_sig = Wave(Double, "out_sig", N, x)
    out_sig.defn = [ scaled_sig(x) / N ]

    return out_sig
