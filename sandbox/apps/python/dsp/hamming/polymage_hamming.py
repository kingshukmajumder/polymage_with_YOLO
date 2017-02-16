from __init__ import *

import sys
import subprocess
import numpy as np
from fractions import Fraction

sys.path.insert(0, ROOT)

from compiler import *
from constructs import *

def hamming(pipe_data):

    N = Parameter(UInt, "N")

    pipe_data['N'] = N

    x = Variable(UInt, 'x')
    y = Variable(UInt, 'y')

    sig = Matrix(Double, "sig", [N, 1], [x, y])

    row, col = Interval(UInt, 0, N-1), Interval(UInt, 0, 0)

    order = Cast(Double, N-1)
    win = Function(([x, y], [row, col]), Double, "win")
    win.defn = [ 0.54 - 0.46*Cos((2*Pi()*x)/order) ]

    windowed_signal = Function(([x, y], [row, col]), Double, "win_sig")
    windowed_signal.defn = [ sig(x, y) * win(x, y) ]
    return windowed_signal
