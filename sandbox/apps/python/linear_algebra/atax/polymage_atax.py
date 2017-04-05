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
    i2 = Variable(UInt, 'i2')

    row = Interval(UInt, 0 , R-1)
    col = Interval(UInt, 0 , C-1)
    scalar = Interval(UInt, 0 , 0)
    
    A = Matrix(Double, "A", [R, C])
    x = Vector(Double, "x", C)

    A_transpose = Vector.transpose(A)

    y = A_transpose * (A * x)
    
    return y
