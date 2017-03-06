from __init__ import *

import sys
import subprocess
import numpy as np
from fractions import Fraction

sys.path.insert(0, ROOT)

from compiler import *
from constructs import *

def mvt(pipe_data):

    R = Parameter(Int, "R")

    pipe_data['R'] = R
    
    mat1 = Matrix(Double, "mat1", [R, R])
    vec1 = Matrix(Double, "vec1", [R, 1])
    vec2 = Matrix(Double, "vec2", [R, 1])

    mul = mat1 * vec1
    mul1 = mat1 * vec2

    return [mul1,mul]
