from __init__ import *

import sys
import subprocess
import numpy as np
from fractions import Fraction
import random

sys.path.insert(0, ROOT)

from compiler import *
from constructs import *
from cnn_constructs import *

def polymage_lrn(pipe_data):

    # Input Channels
    C = Parameter(UInt, "C")
    # Image size
    Y = Parameter(UInt, "Y")
    X = Parameter(UInt, "X")
    # Filter size
    N = Parameter(UInt, "N")
    # Paramters for LRN
    alpha = Parameter(Float, "alpha")
    beta = Parameter(Float, "beta")
    k = Parameter(UInt, "k")

    c = Variable(UInt, 'c')
    x = Variable(UInt, 'x')
    y = Variable(UInt, 'y')

    n = Variable(Int, 'n')

    Ci = Interval(UInt, 0, C-1)
    Yi = Interval(UInt, 0, Y-1)
    Xi = Interval(UInt, 0, X-1)
    Ni = Interval(Int, (1-N)/2, (N-1)/2)

    
    input_mat = Matrix(Float, "input", [X, Y, C], [x, y, c])
    output = Matrix(Float, "output", [X, Y, C], [x, y, c])

    # sum of sqaures
    squares = Reduction(([x, y, c],[Xi, Yi, Ci]), ([x, y, c, n],[Xi, Yi, Ci, Ni]), Double, "squares")
    lower = Min(c+n/2, N-1)
    clamp = Max(lower, Cast(UInt, 0))
    squares.defn = [Reduce(squares(x, y, c), input_mat(x, y, clamp) * input_mat(x, y, clamp), Op.Sum)]

    output.defn = [input_mat(x,y,c) / Pow(((squares(x,y,c) * alpha) + k),beta)]

    return output
