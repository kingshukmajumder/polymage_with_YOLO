from __init__ import *

import sys
import subprocess
import numpy as np
from fractions import Fraction

sys.path.insert(0, ROOT)

from compiler import *
from constructs import *
from cnn_constructs import *

def polymage_relu(pipe_data):

    C = Parameter(UInt, "C")
    Y = Parameter(UInt, "Y")
    X = Parameter(UInt, "X")
    norm = Parameter(Double, "norm")

    c = Variable(UInt, 'c')
    x = Variable(UInt, 'x')
    y = Variable(UInt, 'y')

    Ci = Interval(UInt, 0, C-1)
    Yi = Interval(UInt, 0, Y-1)
    Xi = Interval(UInt, 0, X-1)
    
    input_mat = Matrix(Double, "input", [X, Y, C], [x, y, c])
    
    output = Function(([x, y, c],[Xi, Yi, Ci]), Double, "output")
    output.defn = [Max(norm, input_mat(x, y, c))]

    return output
