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
    y = Variable(Int, 'y')
    z = Variable(Int, 'z')

    sig1 = Matrix(Double, "sig1", [M, 1])
    sig2 = Matrix(Double, "sig2", [N, 1])

    row1, col1 = Interval(Int, 0, M-1), Interval(Int, 0, 0)
    row2, col2 = Interval(Int, 0, M+N-2), Interval(Int, 0, 0)

    convolution = Reduction(([z, y], [row2, col2]), ([z, x, y], [row2, row1, col1]), Double, "convolution")
    c = Condition(z - x, '<', N) & Condition(z - x, '>=', 0)
    convolution.defn = [ Case(c, Reduce(convolution(z, y), sig1(x, y) * sig2(z - x, y), Op.Sum)) ]
    return convolution
