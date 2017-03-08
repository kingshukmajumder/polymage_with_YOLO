from __init__ import *

import sys
import subprocess
import numpy as np
from fractions import Fraction

sys.path.insert(0, ROOT)

from compiler import *
from constructs import *

def hilbert(pipe_data):

    N = Parameter(UInt, "N")

    pipe_data['N'] = N

    x = Variable(UInt, 'x')

    sig = Wave(Double, "sig", N, x)

    sig_complex = Wave(Complex, "sig_complex", N, x)
    sig_complex.defn = [ sig(x) ]

    f = sig_complex.fft("f")

    h = Wave(Double, "h", N, x)
    cond1 = Condition(x, '==', 0)
    cond2 = Condition(x, '>', 0) & Condition(2*x, '<=', N)
    cond3 = Condition(2*x, '>', N) & Condition(x, '<', N)
    h.defn = [ Case(cond1, 1), Case(cond2, Min(2, Cast(Int, 1 + N - 2*x))), Case(cond3, 0) ]

    fh = Wave(Complex, "fh", N, x)
    fh.defn = [ f(x) * h(x) ]

    scaled_sig_a = fh.ifft("scaled_sig_a", real_input=False)

    sig_a = Wave(Complex, "sig_a", N, x)
    sig_a.defn = [ scaled_sig_a(x) / Cast(Double, N) ]

    return sig_a
