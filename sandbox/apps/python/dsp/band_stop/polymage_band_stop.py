from __init__ import *

import sys
import subprocess
import numpy as np
from fractions import Fraction

sys.path.insert(0, ROOT)

from compiler import *
from constructs import *

def band_stop(pipe_data):

    N = Parameter(UInt, "N")
    LC = Parameter(Double, "LC")
    HC = Parameter(Double, "HC")
    F = Parameter(Double, "F")

    pipe_data['N'] = N
    pipe_data['LC'] = LC
    pipe_data['HC'] = HC
    pipe_data['F'] = F

    x = Variable(UInt, 'x')

    sig = Wave(Double, "sig", N, x)
    hs = sig.fft("hs")

    fsran = Interval(UInt, 0, N / 2)
    fs = Function(([x], [fsran]), Double, "fs")
    fs.defn = [ Cast(Double, x) / N ]

    hs_bs = Wave(Complex, "hs_bs", N / 2 + 1, x)
    cond1 = Condition(LC, '<', fs(x)) & Condition(fs(x), '<', HC) 
    cond2 = Condition(LC, '>=', fs(x)) | Condition(fs(x), '>=', HC)
    hs_bs.defn = [ Case(cond1, hs(x) * F), \
                   Case(cond2, hs(x)) ]
    scaled_sig = hs_bs.ifft("scaled_sig", N)

    out_sig = Wave(Double, "out_sig", N, x)
    out_sig.defn = [ scaled_sig(x) / N ]

    out_sig2 = sig.band_stop(LC, HC, "out_sig2", F)

    return out_sig, out_sig2
