from __init__ import *

import sys
import subprocess
import numpy as np
from fractions import Fraction

sys.path.insert(0, ROOT)

from compiler import *
from constructs import *

def gemver(pipe_data):

    R = Parameter(Int, "R")
    beta = 1.2
    alpha = 1.5

    pipe_data['R'] = R

    i0 = Variable(UInt, 'i0')
    i1 = Variable(UInt, 'i1')

    row = Interval(UInt, 0 , R-1)
    
    A = Matrix(Double, "A", [R, R], [i0, i1])
    u1 = Matrix(Double, "u1", [R], [i0])
    v1 = Matrix(Double, "v1", [R], [i0])
    u2 = Matrix(Double, "u2", [R], [i0])
    v2 = Matrix(Double, "v2", [R], [i0])
    w = Matrix(Double, "w", [R], [i0])
    x = Matrix(Double, "x", [R], [i0])
    y = Matrix(Double, "y", [R], [i0])
    z = Matrix(Double, "z", [R], [i0])

    fn1 = Function(([i0, i1], [row, row]), Double, "fn1")
    fn1.defn = [ A(i0, i1) + u1(i0) * v1(i1) + u2(i0) * v2(i1) ]

    fn2 = Reduction(([i0], [row]), ([i0, i1], [row, row]), Double, "fn2")
    fn2.defn = [ Reduce(fn2(i0), beta * fn1(i1, i0) * y(i1) , Op.Sum) ]
    
    fn3 = Function(([i0], [row]), Double, "fn3")
    fn3.defn = [ fn2(i0) + z(i0) ]

    fn4 = Reduction(([i0], [row]), ([i0, i1], [row, row]), Double, "fn4")
    fn4.defn = [ Reduce(fn4(i0), alpha * fn1(i1, i0) * fn3(i1), Op.Sum) ]

    return [fn2, fn4]
