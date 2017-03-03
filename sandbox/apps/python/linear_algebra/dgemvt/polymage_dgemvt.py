from __init__ import *

import sys
import subprocess
import numpy as np
from fractions import Fraction

sys.path.insert(0, ROOT)

from compiler import *
from constructs import *

def dgemvt(pipe_data):

    R = Parameter(Int, "R")
    beta = 0.89
    alpha = 0.9

    pipe_data['R'] = R

    i0 = Variable(UInt, 'i0')
    i1 = Variable(UInt, 'i1')

    row = Interval(UInt, 0 , R-1)
    
    A = Matrix(Double, "A", [R, R], [i0, i1])
    w = Matrix(Double, "w", [R], [i0])
    x = Matrix(Double, "x", [R], [i0])
    y = Matrix(Double, "y", [R], [i0])
    z = Matrix(Double, "z", [R], [i0])

    fn1 = Reduction(([i0], [row]), ([i0, i1], [row, row]), Double, "fn1")
    fn1.defn = [ Reduce(fn1(i0), A(i1, i0) * y(i1) , Op.Sum) ]

    fn2 = Function(([i0], [row]), Double, "fn2")
    fn2.defn = [ beta * fn1(i0) + z(i0) ]

    fn3 = Reduction(([i0], [row]), ([i0, i1], [row, row]), Double, "fn3")
    fn3.defn = [ Reduce(fn3(i0), A(i0, i1) * fn2(i1) , Op.Sum) ]
    
    fn4 = Function(([i0], [row]), Double, "fn4")
    fn4.defn = [ alpha * fn3(i0) ]

    return [fn2, fn4]
