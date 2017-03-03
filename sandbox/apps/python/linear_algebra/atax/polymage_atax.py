from __init__ import *

import sys
import subprocess
import numpy as np
from fractions import Fraction

sys.path.insert(0, ROOT)

from compiler import *
from constructs import *

def atax(pipe_data):

    R = Parameter(Int, "R")
    C = Parameter(Int, "C")
    beta = 0.89
    alpha = 0.9

    pipe_data['R'] = R
    pipe_data['C'] = C

    i0 = Variable(UInt, 'i0')
    i1 = Variable(UInt, 'i1')

    row = Interval(UInt, 0 , R-1)
    col = Interval(UInt, 0 , C-1)
    
    A = Matrix(Double, "A", [R, C], [i0, i1])
    x = Matrix(Double, "x", [C], [i1])

    fn1 = Reduction(([i0], [row]), ([i0, i1], [row, col]), Double, "fn1")
    fn1.defn = [ Reduce(fn1(i0), A(i1, i0) * x(i1) , Op.Sum) ]

    y = Reduction(([i1], [col]), ([i0, i1], [row, col]), Double, "y")
    y.defn = [ Reduce(y(i1), A(i0, i1) * fn1(i0) , Op.Sum) ]
    
    return y
