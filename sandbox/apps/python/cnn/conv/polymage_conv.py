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

    K = Parameter(UInt, "K")
    N = Parameter(UInt, "N")
    C = Parameter(UInt, "C")
    Y = Parameter(UInt, "Y")
    X = Parameter(UInt, "X")
    Fh = Parameter(UInt, "Fh")
    Fw = Parameter(UInt, "Fw")

    k = Variable(UInt, 'k')
    n = Variable(UInt, 'n')
    c = Variable(UInt, 'c')
    x = Variable(UInt, 'x')
    y = Variable(UInt, 'y')
    fh = Variable(UInt, 'fh')
    fw = Variable(UInt, 'fw')

    Ki = Interval(UInt, 0, K-1)
    Ni = Interval(UInt, 0, N-1)
    Ci = Interval(UInt, 0, C-1)
    Yi = Interval(UInt, 0, Y-1-Fh)
    Xi = Interval(UInt, 0, X-1-Fw)
    Fhi = Interval(UInt, 0, Fh-1)
    Fwi = Interval(UInt, 0, Fw-1)
    
    input_mat = Matrix(Double, "input", [X, Y, C, N], [x, y, c, n])
    weights = Matrix(Double, "weights", [Fw, Fh, C, K], [fw, fh, c, k])
    
    output = Reduction(([x, y, k, n],[Xi, Yi, Ki, Ni]), ([n, k, c, y, x, fh, fw],[Ni, Ki, Ci, Yi, Xi, Fhi, Fwi]), Double, "output")
    output.defn = [Reduce(output(x, y, k, n), input_mat(x+fw, y+fh, c, n) * weights(fw, fh, c, k), Op.Sum)]

    return output
