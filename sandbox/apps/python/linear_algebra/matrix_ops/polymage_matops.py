from __init__ import *

import sys
import subprocess
import numpy as np
from fractions import Fraction

sys.path.insert(0, ROOT)

from compiler import *
from constructs import *

def mat_ops(pipe_data):

    R = Parameter(UInt, "R")
    C = Parameter(UInt, "C")

    pipe_data['R'] = R
    pipe_data['C'] = C

    x = Variable(UInt, 'x')
    y = Variable(UInt, 'y')

    row = Interval(UInt, 0, R-1)
    col = Interval(UInt, 0, C-1)

    mat1 = Matrix(Double, "mat1", [R, C], [x, y])
    mat2 = Matrix(Double, "mat2", [R, C], [x, y])

    cond = Condition(R, "==", C)

    # Multiplication
    mul = mat1 * mat2
    
    # Scalar multiplication
    scalar_mul = Matrix.scalar_mul(mul, 10)

    # Element-wise addition
    add = scalar_mul + mat2
    
    # Element-wise subtraction
    sub = add - mat2

    # Element-wise multiplication
    elem_mul = Matrix.elementwise_mul(mat1, sub)

    # Transpose of a matrix
    transpose = Matrix.transpose(elem_mul)

    # Element-wise division
    div = Matrix.elementwise_div(transpose, mat2)
    return div
    
