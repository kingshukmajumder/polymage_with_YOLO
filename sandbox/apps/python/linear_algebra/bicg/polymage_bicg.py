from __init__ import *

import sys
import subprocess
import numpy as np
from fractions import Fraction

sys.path.insert(0, ROOT)

from compiler import *
from constructs import *

def bicg(pipe_data):

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
    p = Matrix(Double, "p", [C], [i0])
    r = Matrix(Double, "r", [R], [i0])

    fn1 = Reduction(([i0], [col]), ([i0, i1], [row, col]), Double, "fn1")
    fn1.defn = [ Reduce(fn1(i1), r(i0) * A(i0, i1) , Op.Sum) ]

    fn2 = Reduction(([i0], [row]), ([i0, i1], [row, col]), Double, "fn2")
    fn2.defn = [ Reduce(fn2(i0), A(i0, i1) * p(i1) , Op.Sum) ]
    
    return [fn2, fn1]
