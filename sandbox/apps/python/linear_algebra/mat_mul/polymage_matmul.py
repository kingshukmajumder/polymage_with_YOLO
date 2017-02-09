from __init__ import *

import sys
import subprocess
import numpy as np
from fractions import Fraction

sys.path.insert(0, ROOT)

from compiler import *
from constructs import *

def matmul(pipe_data):

    R = Parameter(Int, "R")
    C = Parameter(Int, "C")
    #R2 = Parameter(Int, "R2")
    #C2 = Parameter(Int, "C2")

    pipe_data['R'] = R
    pipe_data['C'] = C
    # pipe_data['R2'] = R2
    #pipe_data['C2'] = C2

    x = Variable(UInt, 'x')
    y = Variable(UInt, 'y')
    #z = Variable(UInt, 'z')
    
    mat1 = Matrix(Double, "mat1", [R, C], [x, y])
    mat2 = Matrix(Double, "mat2", [R, C], [x, y])
    mat3 = Matrix(Double, "mat3", [R, C], [x, y])

    mul = mat1 * mat2
    #return mul
    mul1 = mat1 * mat3
    #return mul1

    row = Interval(UInt, 0, R-1)
    col = Interval(UInt, 0, C-1)
    res = Function(([x, y], [row, col]), Double, "res")
    res.defn = [ mul1(x, y) + mul(x, y) ]

    #TODO: Need to add the constructs for directly doing this operation
    #mul2 = mul1 +  mul

    return res
