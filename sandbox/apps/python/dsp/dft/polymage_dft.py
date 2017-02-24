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

    row = Interval(UInt, 0, N - 1)
    out_sig = Reduction(([y], [row]), ([y, x], [row, row]), Complex, "out_sig")
    out_sig.defn = [ Reduce(out_sig(y), \
                            sig(x) * Exp(Cast(Complex, -2 * Pi() * 1.0j * y * x / N)), \
                            Op.Sum) ]
    return out_sig
