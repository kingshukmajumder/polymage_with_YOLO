from __init__ import *

import sys
import subprocess
import numpy as np
from fractions import Fraction

sys.path.insert(0, ROOT)

from compiler import *
from constructs import *

def convolve(pipe_data):

    M = Parameter(Int, "M")
    N = Parameter(Int, "N")

    pipe_data['M'] = M
    pipe_data['N'] = N

    x = Variable(Int, 'x')
    z = Variable(Int, 'z')

    sig1 = Wave(Double, "sig1", M)
    sig2 = Wave(Double, "sig2", N)

    row1 = Interval(Int, 0, M-1)
    row2 = Interval(Int, 0, M+N-2)

    convolution = Reduction(([z], [row2]), ([z, x], [row2, row1]), Double, "convolution")
    c = Condition(z - x, '<', N) & Condition(z - x, '>=', 0)
    convolution.defn = [ Case(c, Reduce(convolution(z), sig1(x) * sig2(z - x), Op.Sum)) ]
    return convolution
