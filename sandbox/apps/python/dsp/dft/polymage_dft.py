from __init__ import *

import sys
import subprocess
import numpy as np
from fractions import Fraction

sys.path.insert(0, ROOT)

from compiler import *
from constructs import *

def dft(pipe_data):

    N = Parameter(UInt, "N")

    pipe_data['N'] = N

    x = Variable(UInt, 'x')
    y = Variable(UInt, 'y')

    sig = Wave(Double, "sig", N, x)

    row = Interval(UInt, 0, N // 2)
    row_full = Interval(UInt, 0, N-1)
    sig_fft = Reduction(([y], [row]), ([y, x], [row, row_full]), Complex, "sig_fft")
    sig_fft.defn = [ Reduce(sig_fft(y), \
                            sig(x) * Exp(Cast(Complex, -2 * Pi() * 1.0j * y * x / N)), \
                            Op.Sum) ]

    cond1 = Condition(2*x, '<=', N)
    cond2 = Condition(2*x, '>', N)

    sig_fft_ifft = Reduction(([y], [row_full]), ([y, x], [row_full, row_full]), Double, "sig_fft_ifft")
    sig_fft_ifft.defn = [ Case(cond1, Reduce(sig_fft_ifft(y), \
                                 Real((Conj(sig_fft(x)) * Exp(Cast(Complex, -2 * Pi() * 1.0j * y * x / N)))), \
                                 Op.Sum)), \
                          Case(cond2, Reduce(sig_fft_ifft(y), \
                                 Real(((sig_fft(N - x)) * Exp(Cast(Complex, -2 * Pi() * 1.0j * y * x / N)))), \
                                 Op.Sum)) ]

    return sig_fft_ifft
