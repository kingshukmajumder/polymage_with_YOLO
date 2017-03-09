from __init__ import *

import sys
import subprocess
import numpy as np
from fractions import Fraction

sys.path.insert(0, ROOT)

from compiler import *
from constructs import *

def corr(pipe_data):

    M = Parameter(Int, "M")
    N = Parameter(Int, "N")

    pipe_data['M'] = M
    pipe_data['N'] = N

    x = Variable(Int, 'x')
    z = Variable(Int, 'z')

    sig1 = Wave(Double, "sig1", M)
    sig2 = Wave(Double, "sig2", N)
    sig3 = Wave(Complex, "sig3", M)
    sig4 = Wave(Complex, "sig4", N)

    row1 = Interval(Int, 0, M-1)
    row2 = Interval(Int, 0, M+N-2)

    corr = Reduction(([z], [row2]), ([z, x], [row2, row1]), Double, "corr")
    c = Condition(z - x, '<', N) & Condition(z - x, '>=', 0)
    corr.defn = [ Case(c, Reduce(corr(z), sig1(x) * sig2(x + N - 1 - z), Op.Sum)) ]
    corr2 = sig1.correlate(sig2, "corr2")
    corr3 = sig3.correlate(sig4, "corr3")
    return corr, corr2, corr3
