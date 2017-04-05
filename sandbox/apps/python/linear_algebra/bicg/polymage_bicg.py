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

    pipe_data['R'] = R
    pipe_data['C'] = C

    i0 = Variable(UInt, 'i0')
    i1 = Variable(UInt, 'i1')

    row = Interval(UInt, 0 , R-1)
    col = Interval(UInt, 0 , C-1)
    
    A = Matrix(Double, "A", [R, C], [i0, i1])
    p = Vector(Double, "p", C)
    r = Vector(Double, "r", R)

    r_transpose = Vector.transpose(r)

    s = r_transpose * A
    q = A * p

    return [q, s]
