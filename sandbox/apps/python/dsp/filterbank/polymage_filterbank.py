from __init__ import *

import sys
import subprocess
import numpy as np
from fractions import Fraction

sys.path.insert(0, ROOT)

from compiler import *
from constructs import *

def filterbank(pipe_data):

    N = Parameter(UInt, "N")
    M = 32
    N_samp = 8

    pipe_data['N'] = N

    # input vector
    r = Wave(Double, "r", N)

    # filter responses
    H = Wave(Double, "H", M)
    F = Wave(Double, "F", M)

    # convolving H
    Vect_H = r.lfilter_fir(H, "Vect_H")

    # downsampling
    Vect_Dn = Vect_H.downsample(N_samp, "Vect_Dn")

    # upsampling
    Vect_Up = Vect_Dn.upsample(N_samp, "Vect_Up", N)

    # convolving F
    y = Vect_Up.lfilter_fir(F, "y")

    # output vector
    return y
