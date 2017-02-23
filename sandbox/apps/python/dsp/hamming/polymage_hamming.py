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

    sig = Wave(Double, "sig", N, x)

    order = Cast(Double, N-1)
    win = Wave(Double, "win", N, x)
    win.defn = [ 0.54 - 0.46*Cos((2*Pi()*x)/order) ]

    windowed_signal = Wave(Double, "win_sig", N, x)
    windowed_signal.defn = [ sig(x) * win(x) ]
    return windowed_signal
