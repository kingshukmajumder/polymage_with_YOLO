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
    # return mul
    
    # Scalar multiplication
    scalar_mul = Matrix(Double, "scalar_mul", [R, C], [x, y])
    scalar_mul.defn = [Case(cond, mul(x,y) * 10)]
    # return scalar_mul

    # Element-wise addition
    add = scalar_mul + mat2
    #return add
    
    # Element-wise subtraction
    sub = Matrix(Double, "sub", [R, C], [x, y])
    sub.defn = [add(x,y) - mat2(x,y)]
    # return sub

    # Element-wise multiplication
    mul = Matrix(Float, "mul", [R, C], [x, y])
    mul.defn = [mat1(x,y) * sub(x,y)]
    #return mul

    # Transpose of a matrix
    transpose = Matrix(Double, "transpose", [R, C], [x, y])
    transpose.defn = [sub(y, x)]
    #return transpose

    # Element-wise division
    div = Matrix(Double, "div", [R, C], [x, y])
    div.defn = [transpose(x,y) / mat2(x,y)]
    return div
    
