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
    
    #mat1 = Matrix(Float, "mat1", [R1, C1], [x,y])
    #mat2 = Matrix(Float, "mat2", [R2, C2], [x,y])

    #mul = Matrix.multiply(mat1,mat2)
    #mul = mat1 * mat2
    #mul2 = mul * mat2


    # FIXME: add the following changes at the matrix multiply
    # operator overloading function, and remove them from here.

    mat1 = Image(Float, "A", [R1, C1])
    mat2 = Image(Float, "B", [R2, C2])

    dom1x = Interval(UInt, 0, R1-1)
    dom1y = Interval(UInt, 0, C1-1)
    dom2x = Interval(UInt, 0, R2-1)
    dom2y = Interval(UInt, 0, C2-1)

    # NOTE: This is the constraint given to isl, as a promise, that
    # the parameters of the dimension in which matrices are reduced
    # are equal. The bounds check pass will fail if we don't supply
    # this information.
    cond = Condition(C1, "==", R2)

    mat_mul = Reduction(
        ([x, y], [dom1x, dom2y]),
        ([x, z, y], [dom1x, dom2x, dom2y]),
        Float, "prod")
    mat_mul.defn = [ Case(cond, Reduce(mat_mul(x, y), mat1(x, z) * mat2(z, y), Op.Sum)) ]

    return mat_mul
