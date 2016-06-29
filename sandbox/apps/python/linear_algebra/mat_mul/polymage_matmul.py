from __init__ import *

import sys
import subprocess
import numpy as np
from fractions import Fraction

sys.path.insert(0, ROOT)

from compiler import *
from constructs import *

def matmul(pipe_data):

    R1 = Parameter(Int, "R1")
    C1 = Parameter(Int, "C1")
    R2 = Parameter(Int, "R2")
    C2 = Parameter(Int, "C2")

    pipe_data['R1'] = R1
    pipe_data['C1'] = C1
    pipe_data['R2'] = R2
    pipe_data['C2'] = C2

    x = Variable(UInt, 'x')
    y = Variable(UInt, 'y')
    z = Variable(UInt, 'z')
    
    mat1 = Matrix(Float, "mat1", [R1, C1], [x,y])
    mat2 = Matrix(Float, "mat2", [R2, C2], [x,y])

    #mul = Matrix.multiply(mat1,mat2)
    mul = mat1 * mat2
    #mul2 = mul * mat2
    return mul
