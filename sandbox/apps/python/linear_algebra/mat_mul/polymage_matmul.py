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
    
    mat1 = Matrix(Double, "mat1", [R, C], [x, y])
    mat2 = Matrix(Double, "mat2", [R, C], [x, y])
    mat3 = Matrix(Double, "mat3", [R, C], [x, y])

    mul = mat1 * mat2
    mul1 = mat1 * mat3

    return [mul1,mul]
