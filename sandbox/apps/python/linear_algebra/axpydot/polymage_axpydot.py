from __init__ import *

import sys
import subprocess
import numpy as np
from fractions import Fraction

sys.path.insert(0, ROOT)

from compiler import *
from constructs import *

def axpydot(pipe_data):

    R = Parameter(Int, "R")
 
    alpha = 0.9

    pipe_data['R'] = R

    row = Interval(UInt, 0 , R-1)
    scalar_int = Interval(UInt, 0 , 0)
    
    u = Vector(Double, "u", R)
    v = Vector(Double, "v", R)
    w = Vector(Double, "w", R)

    z = w - Vector.scalar_mul(v, alpha)
    r = Vector.transpose(z) * u

    return r
