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

    mat1 = Matrix(Float, "mat1", [R, C], [x, y])
    #mat2 = Matrix(Float, "mat3", [R, C], [x, y])
    '''
    # Scalar multiplication
    scalar_mul = Matrix(Float, "scalar_mul", [R, C], [x, y])
    scalar_mul.defn = [mat1(x,y) * 10]
    # return scalar_mul

    # Element-wise addition
    add = Matrix(Float, "add", [R, C], [x, y])
    add.defn = [scalar_mul(x,y) + mat2(x,y)]
    # return add

    # Element-wise subtraction
    sub = Matrix(Float, "sub", [R, C], [x, y])
    sub.defn = [add(x,y) - mat2(x,y)]
    # return sub

    # Element-wise multiplication
    mul = Matrix(Float, "mul", [R, C], [x, y])
    mul.defn = [mat1(x,y) * sub(x,y)]
    # return mul

    # Transpose of a matrix
    transpose = Matrix(Float, "transpose", [R, C], [x, y])
    transpose.defn = [mul(y, x)]
    # return transpose

    # Element-wise division
    div = Matrix(Float, "div", [R, C], [x, y])
    div.defn = [transpose(x,y) / mat2(x,y)]
    #return div

    # Determinant of a matrix
    det = Matrix.det(div)
    # return det
    '''
    # Inverse of a matrix
    inv = Matrix.inverse(mat1)
    return inv

    #Iy = Function(([x, y], [row, col]), Float, "Iy")
    #Iy.defn = [Sin(mat1(x,y))]
    #return Iy


    #new = div * mat1
    #return new

    #cond = Condition(x, '>=', 0) & Condition(x, '<=', R-1) & \
    #       Condition(y, '<=', C-1) & Condition(y, '>=', 0)

    # A pipeline with completely aimless random sequence of computations
    # to test the math functions support

    # sin(image1)

    #cos = Function(([x, y], [row, col]), Float, "_cos")
    #cos.defn = [ Cos(mat1(x, y)) ]


    #sin = Function(([x, y], [row, col]), Float, "_sin")
    #sin.defn = [ Case(cond, Cos(mat1(x, y))) ]

    #return cos

