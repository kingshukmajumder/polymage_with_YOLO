from __init__ import *

import sys
import subprocess
import numpy as np
from fractions import Fraction

sys.path.insert(0, ROOT)

from compiler import *
from constructs import *

def axpydot(pipe_data):

    R = Parameter(Int, "R")
 
    alpha = 0.9

    pipe_data['R'] = R

    i0 = Variable(UInt, 'i0')
    i1 = Variable(UInt, 'i1')

    row = Interval(UInt, 0 , R-1)
    scalar_int = Interval(UInt, 0 , 0)
    
    u = Matrix(Double, "u", [R], [i0])
    v = Matrix(Double, "v", [R], [i0])
    w = Matrix(Double, "w", [R], [i0])

    z = Function(([i0], [row]), Double, "z")
    z.defn = [ w(i0) - alpha * v(i0) ]

    r = Reduction(([i1], [scalar_int]), ([i0, i1], [row, scalar_int]), Double, "r")
    r.defn = [ Reduce(r(i1), z(i0) * u(i0), Op.Sum) ]
    
    #fn3.defn = [ Reduce(fn3(i0), A(i0, i1) * fn2(i1) , Op.Sum) ]
    return r
