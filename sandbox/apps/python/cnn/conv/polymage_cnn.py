from __init__ import *

import sys
import subprocess
import numpy as np
from fractions import Fraction

sys.path.insert(0, ROOT)

from compiler import *
from constructs import *

def polymage_conv(pipe_data):

    N = Parameter(Int, "N")
    Oc = Parameter(Int, "Oc")
    Ic = Parameter(Int, "Ic")
    Y = Parameter(Int, "Y")
    X = Parameter(Int, "X")
    Kh = Parameter(Int, "Kh")
    Kw = Parameter(Int, "Kw")

    n = Variable(UInt, 'n')
    o = Variable(UInt, 'o')
    i = Variable(UInt, 'i')
    x = Variable(UInt, 'x')
    y = Variable(UInt, 'y')
    kh = Variable(UInt, 'kh')
    kw = Variable(UInt, 'kw')

    Ni = Interval(UInt, 0, N-1)
    Oi = Interval(UInt, 0, Oc-1)
    Ii = Interval(UInt, 0, Ic-1)
    Yi = Interval(UInt, 0, Y-1)
    # Yi = Interval(UInt, 0, Y-3-1)
    # Xi = Interval(UInt, 0, X-3-1)
    Xi = Interval(UInt, 0, X-1)
    Khi = Interval(UInt, 0, Kh-1)
    Kwi = Interval(UInt, 0, Kw-1)
    
    # output = Matrix(Float, "output", [N, Oc, Y, X])
    input_mat = Matrix(Float, "input_mat", [N, Ic, Y, X], [n, i, y, x])
    weights = Matrix(Float, "weights", [Oc, Ic, Kh, Kw], [o, i, kh, kw])

    #cond = Condition(x+kh, '<=', X) & Condition(y+kw, '<=', Y)
    cond = Condition(x, '>=', 0)

    # output = input_mat * weights
    output = Reduction(([n, o, y, x],[Ni, Oi, Yi, Xi]), ([n, o, i, y, x, kh, kw],[Ni, Oi, Ii, Yi, Xi, Khi, Kwi]), Float, "output")
    output.defn = [Case(cond, Reduce(output(n, o, y, x), input_mat(n, i, y+kh, x+kw) * weights(o, i, kh, kw), Op.Sum))]

    return output
