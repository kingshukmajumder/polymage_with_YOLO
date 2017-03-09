from __init__ import *

import sys
import subprocess
import numpy as np
from fractions import Fraction

sys.path.insert(0, ROOT)

from compiler import *
from constructs import *

def lfilter(pipe_data):

    L = Parameter(Int, 'L')
    M = Parameter(Int, "M")
    N = Parameter(Int, "N")

    pipe_data['L'] = L
    pipe_data['M'] = M
    pipe_data['N'] = N

    sig_in = Wave(Double, "sig_in", L)
    b = Wave(Double, "b", M)
    a = Wave(Double, "a", N)

    x = Variable(UInt, "x")
    y = Variable(Int, "y")
    z = Variable(Int, "z")

    b_norm = Wave(Double, "b_norm", M, x)
    b_norm.defn = [ Case(Condition(N, '>', 0), b(x) / a(0)) ]

    a_norm = Wave(Double, "a_norm", N, x)
    a_norm.defn = [ a(x) / a(0) ]

    sig_interval = Interval(Int, 0, L-1)
    coeff_interval = Interval(Int, 0, M+N-1)

    sig_out = Reduction(([z], [sig_interval]), ([z, y], [sig_interval, \
                        coeff_interval]), Double, "sig_out")
    cond1 = Condition(z - y, '>=', 0) & Condition(y, '<', M)
    cond2 = Condition(y, '>', 0) & Condition(z - y, '>=', 0) & Condition(y, '<', N)
    sig_out.defn = [ Case(cond1, Reduce(sig_out(z), \
                                        sig_in(z - y) * b_norm(y), \
                                        Op.Sum)), \
                    Case(cond2, Reduce(sig_out(z), \
                                       sig_out(z - y) * -a_norm(y), \
                                       Op.Sum)) ]
    sig_out2 = sig_in.lfilter(b, a, "sig_out2")

    return sig_out, sig_out2
