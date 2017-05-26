from __init__ import *

import sys
import subprocess
import numpy as np
from fractions import Fraction

sys.path.insert(0, ROOT)

from compiler import *
from constructs import *
from cnn_constructs import *

def polymage_flatten(pipe_data):

    C = Parameter(UInt, "C")
    Y = Parameter(UInt, "Y")
    X = Parameter(UInt, "X")
    N = Parameter(UInt, "N")
    out = Parameter(UInt, "out")

    c = Variable(UInt, 'c')
    x = Variable(UInt, 'x')
    y = Variable(UInt, 'y')
    n = Variable(UInt, 'n')
    o = Variable(UInt, 'o')

    input_mat = Matrix(Float, "input_mat", [X, Y, C, N], [x, y, c, n])
    # Creating a temporary function. Otherwise parameter 'C' is not passed correctly.
    tmp = Matrix(Float, "tmp", [X, Y, C, N], [x, y, c, n])
    output = Matrix(Float, "output", [out, N], [o, n])

    tmp.defn = [input_mat(x, y, c, n)]
    output.defn = [tmp(o % X, (o / X) % Y, o / (X * Y), n)]

    return output
