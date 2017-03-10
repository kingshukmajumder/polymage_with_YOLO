from __init__ import *

import sys
import subprocess
import numpy as np
from fractions import Fraction

sys.path.insert(0, ROOT)

from compiler import *
from constructs import *

def freqz(pipe_data):

    N = Parameter(UInt, "N")

    pipe_data['N'] = N

    x = Variable(UInt, 'x')
    y = Variable(Int, 'y')
    z = Variable(Int, 'z')

    b = Wave(Double, "b", N)

    w = Wave(Double, "w", 512, x)
    w.defn = [ Pi() / 512 * x ]

    freq_int = Interval(Int, 0, 511)
    coeff_int = Interval(Int, 0, N-1)

    h = Reduction(([z], [freq_int]), ([z, y], [freq_int, coeff_int]), \
                    Complex, "h")
    h.defn = [ Reduce(h(z), \
                      b(y) * Exp(Cast(Complex, -1.0j * w(z) * y)), \
                      Op.Sum) ]

    w2, h2 = b.freqz(("w2", "h2"))
    return w, h, w2, h2
