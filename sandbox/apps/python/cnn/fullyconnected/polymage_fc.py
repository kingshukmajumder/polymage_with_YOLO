from __init__ import *

import sys
import subprocess
import numpy as np
from fractions import Fraction

sys.path.insert(0, ROOT)

from compiler import *
from constructs import *
from cnn_constructs import *

def polymage_fc(pipe_data):

    N = Parameter(UInt, "N")
    Y = Parameter(UInt, "Y")
    X = Parameter(UInt, "X")

    n = Variable(UInt, 'n')
    x = Variable(UInt, 'x')
    y = Variable(UInt, 'y')

    Ni = Interval(UInt, 0, N-1)
    Yi = Interval(UInt, 0, Y-1)
    Xi = Interval(UInt, 0, X-1)
    
    input_mat = Matrix(Double, "input_mat", [X, N], [x, n])
    weights = Matrix(Double, "weights", [X, Y], [x, y])
    bias = Matrix(Double, "bias", [Y], [y])
   
     
    output = Reduction(([y, n],[Yi, Ni]), ([x, y, n],[Xi, Yi, Ni]), Double, "output")
    output.default = bias(y) 
    output.defn = [Reduce(output(y, n), input_mat(x, n) * weights(x, clamp(y, 0, Y-1)), Op.Sum)]

    return output
