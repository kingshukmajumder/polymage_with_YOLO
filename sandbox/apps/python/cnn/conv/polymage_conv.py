from __init__ import *

import sys
import subprocess
import numpy as np
from fractions import Fraction

sys.path.insert(0, ROOT)

from compiler import *
from constructs import *
from cnn_constructs import *

def polymage_conv(pipe_data):

    # Ouput Channel
    K = Parameter(UInt, "K")
    # Batch Size
    # Input channel
    C = Parameter(UInt, "C")
    # Height of image
    Y = Parameter(UInt, "Y")
    # Width of image
    X = Parameter(UInt, "X")
    # Kernel Height
    Fh = Parameter(UInt, "Fh")
    # kernel width
    Fw = Parameter(UInt, "Fw")
    P = 1

    k = Variable(UInt, 'k')
    c = Variable(UInt, 'c')
    x = Variable(UInt, 'x')
    y = Variable(UInt, 'y')
    fh = Variable(UInt, 'fh')
    fw = Variable(UInt, 'fw')

    # Input images (Contains N images of dimension X * Y * C)
    input_mat = DataLayer(Double, "input", [X, Y, C], [x, y, c])
    # Kernels (Contains K kernels of size Fw * Fh * C)
    weights = Matrix(Double, "weights", [Fw, Fh, C, K], [fw, fh, c, k])
    bias = Matrix(Double, "bias", [K])

    # Convolution Operation
    conv = Network.convolution(input_mat, weights, bias, P)
    return conv

    #Xp = X+(2*P)
    #Yp = Y+(2*P)
    #Ki = Interval(UInt, 0, K-1)
    #Ci = Interval(UInt, 0, C-1)
    #Yi = Interval(UInt, 0, Yp-Fh)
    #Xi = Interval(UInt, 0, Xp-Fw)
    #Fhi = Interval(UInt, 0, Fh-1)
    #Fwi = Interval(UInt, 0, Fw-1)

    #cond_true = Condition(x, '>=', 1) & \
    #            Condition(x, '<=', Xp-2) & \
    #            Condition(y, '>=', 1) & \
    #            Condition(y, '<=', Yp-2)

    #input_pad = Matrix(Double, "input_pad", [Xp, Yp, C], [x, y, c])
    #expr = input_mat(x-1,y-1,c)
    #input_pad.defn = [Case(cond_true, expr)]

    #output = Reduction(([x, y, k],[Xi, Yi, Ki]), ([k, c, y, x, fh, fw],[Ki, Ci, Yi, Xi, Fhi, Fwi]), Double, "output")
    #output.defn = [Reduce(output(x, y, k), input_pad(x+fw, y+fh, c) * weights(fw, fh, c, k), Op.Sum)]
    #output.default = bias(k)

    #return output
