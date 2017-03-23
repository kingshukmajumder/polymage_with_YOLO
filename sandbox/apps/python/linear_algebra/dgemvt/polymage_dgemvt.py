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
    y = Vector(Double, "y", R)
    z = Vector(Double, "z", R)

    A_transpose = Matrix.transpose(A)

    x = Vector.scalar_mul(A_transpose * y, beta) + z
    w = Vector.scalar_mul(A * x, alpha)

    return [w, x]
