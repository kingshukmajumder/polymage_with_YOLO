from __init__ import *

import sys
import subprocess
import numpy as np
from fractions import Fraction

sys.path.insert(0, ROOT)

from compiler import *
from constructs import *

def window(pipe_data):

    N = Parameter(UInt, "N")
    typ = Parameter(UInt, "typ")

    pipe_data['N'] = N
    pipe_data['typ'] = typ

    x = Variable(UInt, 'x')

    sig = Wave(Double, "sig", N, x)

    c_hamming = Condition(typ, '==', 0)
    c_hanning = Condition(typ, '==', 1)
    c_bartlett = Condition(typ, '==', 2)
    c_blackman = Condition(typ, '==', 3)
    c_nuttall = Condition(typ, '==', 4)
    c_blackman_harris = Condition(typ, '==', 5)
    c_blackman_nuttall = Condition(typ, '==', 6)
    c_flat_top = Condition(typ, '==', 7)
    c_dirichlet = Condition(typ, '==', 8)
    order = Cast(Double, N-1)
    alpha = 0.16
    win = Wave(Double, "win", N, x)
    win.defn = [ Case(c_hamming, 0.54 - 0.46*Cos((2*Pi()*x)/order)),
                 Case(c_hanning, 0.5 - 0.5*Cos((2*Pi()*x)/order)),
                 Case(c_bartlett, 1.0 - Abs(2*x/order - 1)),
                 Case(c_blackman, (1-alpha)/2
                        - 0.50*Cos((2*Pi()*x)/order)
                        + (alpha/2)*Cos((4*Pi()*x)/order)),
                 Case(c_nuttall, 0.355768 - 0.487396*Cos(2*Pi()*x/order)
                        + 0.144232*Cos(4*Pi()*x/order)
                        - 0.012604*Cos(6*Pi()*x/order)),
                 Case(c_blackman_harris, 0.35875
                        - 0.48829*Cos(2*Pi()*x/order)
                        + 0.14128*Cos(4*Pi()*x/order)
                        - 0.01168*Cos(6*Pi()*x/order)),
                Case(c_blackman_nuttall, 0.3635819
                        - 0.4891775*Cos(2*Pi()*x/order)
                        + 0.1365995*Cos(4*Pi()*x/order)
                        - 0.0106411*Cos(6*Pi()*x/order)),
                Case(c_flat_top, 1 - 1.93*Cos(2*Pi()*x/order)
                        + 1.29*Cos(4*Pi()*x/order)
                        - 0.388*Cos(6*Pi()*x/order)
                        + 0.028*Cos(8*Pi()*x/order)),
                Case(c_dirichlet, 1) ]

    windowed_signal = Wave(Double, "win_sig", N, x)
    windowed_signal.defn = [ sig(x) * win(x) ]
    return windowed_signal
