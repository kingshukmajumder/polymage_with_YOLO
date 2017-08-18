from __init__ import *

import sys
import subprocess
import numpy as np
from fractions import Fraction

sys.path.insert(0, ROOT)

from compiler import *
from constructs import *
from cnn_constructs import *

def polymage_crp(pipe_data):

    # Output Channel
    K = Parameter(UInt, "K")
    # Input Channel
    C = Parameter(UInt, "C")
    # Height
    Y = Parameter(UInt, "Y")
    # Width
    X = Parameter(UInt, "X")
    # Kernel Height
    Fh = Parameter(UInt, "Fh")
    # Kernel Width
    Fw = Parameter(UInt, "Fw")

    k = Variable(UInt, 'k')
    c = Variable(UInt, 'c')
    x = Variable(UInt, 'x')
    y = Variable(UInt, 'y')
    fh = Variable(UInt, 'fh')
    fw = Variable(UInt, 'fw')

    
    # Input Images
    input_mat = Matrix(Double, "input", [X, Y, C], [x, y, c])
    # Convolution Kernels
    weights = Matrix(Double, "weights", [Fw, Fh, C, K], [fw, fh, c, k])

    # Convolution
    conv = Network.convolution(input_mat, weights)

    # Rectified Linear Unit
    relu = Network.ReLU(conv)

    # Maxpool (Fh x Fw)
    maxpool = Network.maxpool(relu, Fh, Fw, 2)
    return maxpool

    #Ki = Interval(UInt, 0, K-1)
    #Ni = Interval(UInt, 0, N-1)
    #Ci = Interval(UInt, 0, C-1)
    #Yi = Interval(UInt, 0, Y-1-Fh)
    #Xi = Interval(UInt, 0, X-1-Fw)
    #Fhi = Interval(UInt, 0, Fh-1)
    #Fwi = Interval(UInt, 0, Fw-1)
    #Yii = Interval(UInt, 0, Y-1-Fh-Fh)
    #Xii = Interval(UInt, 0, X-1-Fw-Fw)

    #conv = Reduction(([x, y, k, n], [Xi, Yi, Ki, Ni]), ([n, k, c, y, x, fh, fw], [Ni, Ki, Ci, Yi, Xi, Fhi, Fwi]), Double, "conv")
    #conv.defn = [Reduce(conv(x, y, k, n), input_mat(x+fw, y+fh, c, n) * weights(fw, fh, c, k), Op.Sum)]

    #relu = Function(([x, y, k, n], [Xi, Yi, Ki, Ni]), Double, "relu")
    #relu.defn = [Max(Cast(Double, 0.0), conv(x, y, k, n))]

    #pool = Reduction(([x, y, k, n],[Xii, Yii, Ki, Ni]), ([n, k, y, x, fh, fw],[Ni, Ki, Yii, Xii, Fhi, Fwi]), Double, "pool")
    #pool.defn = [Reduce(pool(x, y, k, n), relu(x+fw, y+fh, k, n), Op.Max)]
    #return pool
