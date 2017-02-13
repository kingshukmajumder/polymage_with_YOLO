from __init__ import *

import sys
import subprocess
import numpy as np
from fractions import Fraction

sys.path.insert(0, ROOT)

from compiler import *
from constructs import *

def corr(pipe_data):

    N = Parameter(UInt, "N")

    pipe_data['N'] = N

    x = Variable(UInt, 'x')
    y = Variable(UInt, 'y')

    sig1 = Matrix(Double, "sig1", [N, 1], [x, y])
    sig2 = Matrix(Double, "sig2", [N, 1], [x, y])

    row, col = Interval(UInt, 0, N-1), Interval(UInt, 0, 0)
    mean1 = Reduction(([y], [col]), ([x, y], [row, col]), Double, "mean1")
    mean1.defn = [Reduce(mean1(y), sig1(x, y) / N, Op.Sum)]

    mean2 = Reduction(([y], [col]), ([x, y], [row, col]), Double, "mean2")
    mean2.defn = [Reduce(mean2(y), sig2(x, y) / N, Op.Sum)]

    cov11 = Reduction(([y], [col]), ([x, y], [row, col]), Double, "cov11")
    cov11.defn = [Reduce(cov11(y), (sig1(x, y) - mean1(y)) * (sig1(x, y) - mean1(y)) / (N - 1), Op.Sum)]

    cov12 = Reduction(([y], [col]), ([x, y], [row, col]), Double, "cov12")
    cov12.defn = [Reduce(cov12(y), (sig1(x, y) - mean1(y)) * (sig2(x, y) - mean2(y)) / (N - 1), Op.Sum)]

    cov22 = Reduction(([y], [col]), ([x, y], [row, col]), Double, "cov22")
    cov22.defn = [Reduce(cov22(y), (sig2(x, y) - mean2(y)) * (sig2(x, y) - mean2(y)) / (N - 1), Op.Sum)]

    corr = Function(([y], [col]), Double, "corr")
    corr.defn = [cov12(y) / Sqrt(cov11(y) * cov22(y))]
    return corr
