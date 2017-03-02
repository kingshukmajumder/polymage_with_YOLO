from __init__ import *

import sys
import subprocess
import numpy as np
from fractions import Fraction

sys.path.insert(0, ROOT)

from compiler import *
from constructs import *

def upfirdn(pipe_data):

    M = Parameter(Int, "M")
    N = Parameter(Int, "N")
    U = Parameter(Int, "U")
    D = Parameter(Int, "D")

    pipe_data['M'] = M
    pipe_data['N'] = N
    pipe_data['U'] = U
    pipe_data['D'] = D

    h = Wave(Double, "h", M)
    sig_in = Wave(Double, "sig_in", N)

    x = Variable(UInt, 'x')
    y = Variable(Int, 'y')
    z = Variable(Int, 'z')

    sig_up = Wave(Double, "sig_up", N * U, x)
    cond1 = Condition(x % U, '==', 0)
    cond2 = Condition(x % U, '!=', 0)
    sig_up.defn = [ Case(cond1, sig_in(x / U)), \
                    Case(cond2, 0) ]

    suf_interval = Interval(Int, 0, N*U+M-2)
    coeff_interval = Interval(Int, 0, M-1)

    sig_up_fir = Reduction(([z], [suf_interval]), ([z, y], [suf_interval, \
                            coeff_interval]), Double, "sig_up_fir")
    cond3 = Condition(z - y, '>=', 0) & Condition(z - y, '<', N*U)
    sig_up_fir.defn = [ Case(cond3, Reduce(sig_up_fir(z), \
                                           sig_up(z - y) * h(y), \
                                           Op.Sum)) ]

    sig_out = Wave(Double, "sig_out", (N*U+M-1+D-1) / D, x)
    sig_out.defn = [ sig_up_fir(x * D) ]

    return sig_out
