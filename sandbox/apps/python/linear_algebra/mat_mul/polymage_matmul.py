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

    pipe_data['R'] = R
    pipe_data['C'] = C

    x = Variable(UInt, 'x')
    y = Variable(UInt, 'y')
    
    mat1 = Matrix(Float, "mat1", [R, C], [x, y])
    mat2 = Matrix(Float, "mat2", [C, R], [x, y])

    #mul = Matrix.multiply(mat1,mat2)
    mul = mat1 * mat2
    mul2 = mul * mat2
    return mul2
