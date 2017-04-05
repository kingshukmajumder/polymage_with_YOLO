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
    u1 = Vector(Double, "u1", R)
    v1 = Vector(Double, "v1", R)
    u2 = Vector(Double, "u2", R)
    v2 = Vector(Double, "v2", R)
    y = Vector(Double, "y", R)
    z = Vector(Double, "z", R)

    fn1 = A + u1 * Vector.transpose(v1) + u2 * Vector.transpose(v2)
    x = (Matrix.scalar_mul(Matrix.transpose(fn1), beta) * y ) + z
    w = Matrix.scalar_mul(fn1, alpha) * x

    return [w, x]
