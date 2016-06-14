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
    
    mat1 = Matrix(Float, "mat1", [R,C])
    mat2 = Matrix(Float, "mat2", [R,C])

    mul = Matrix.multiply(mat1,mat2)
    return mul   
