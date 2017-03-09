from __init__ import *

import sys
import subprocess
import numpy as np
from fractions import Fraction

sys.path.insert(0, ROOT)

from compiler import *
from constructs import *

def fftconvolve(pipe_data):

    M = Parameter(Int, "M")
    N = Parameter(Int, "N")

    pipe_data['M'] = M
    pipe_data['N'] = N

    x = Variable(UInt, 'x')

    sig1 = Wave(Double, "sig1", M)
    sig2 = Wave(Double, "sig2", N)
    sig3 = Wave(Complex, "sig3", M)
    sig4 = Wave(Complex, "sig4", N)

    sig1_zero_pad = Wave(Double, "sig1_zero_pad", M+N-1, x)
    cond1 = Condition(x, '<', M)
    cond2 = Condition(x, '>=', M)
    sig1_zero_pad.defn = [ Case(cond1, sig1(x)), \
                           Case(cond2, 0) ]

    sig2_zero_pad = Wave(Double, "sig2_zero_pad", M+N-1, x)
    cond3 = Condition(x, '<', N)
    cond4 = Condition(x, '>=', N)
    sig2_zero_pad.defn = [ Case(cond3, sig2(x)), \
                           Case(cond4, 0) ]

    f1 = sig1_zero_pad.fft("f1")
    f2 = sig2_zero_pad.fft("f2")
    f1_f2_mult = Wave(Complex, "f1_f2_mult", (M+N-1) // 2 + 1, x)
    f1_f2_mult.defn = [ f1(x) * f2(x) ]

    scaled_convolution = f1_f2_mult.ifft("scaled_convolution", M+N-1)

    convolution = Wave(Double, "convolution", M + N - 1, x)
    convolution.defn = [ scaled_convolution(x) / (M + N - 1) ]

    convolution2 = sig1.fftconvolve(sig2, "convolution2")
    convolution3 = sig3.fftconvolve(sig4, "convolution3")

    return convolution, convolution2, convolution3
