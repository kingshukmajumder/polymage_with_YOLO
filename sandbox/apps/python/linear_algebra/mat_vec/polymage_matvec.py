from __init__ import *

import sys
import subprocess
import numpy as np
from fractions import Fraction

sys.path.insert(0, ROOT)

from compiler import *
from constructs import *

def matvec(pipe_data):

    R = Parameter(Int, "R")
    C = Parameter(Int, "C")
    
    pipe_data['R'] = R
    pipe_data['C'] = C
    
    x = Variable(UInt, 'x')
    y = Variable(UInt, 'y')

    mat1 = Matrix(Double, "mat1", [R, C], [x, y])
    # mat2 = Matrix(Double, "mat2", [R, C], [x, y])
    # mat3 = Matrix(Double, "mat3", [R, C], [x, y])

    v1 = Vector(Double, "v1", C)
    v2 = Vector(Double, "v2", C)
    v3 = Vector(Double, "v3", C)
    # v4 = Vector(Double, "v3", [R, 1], [x, y])

    v4 = mat1 * v1
    v5 = mat1 * v2
    v6 = mat1 * v3 
    # print(v4,v5,v6)
    return [v4,v5,v6]
