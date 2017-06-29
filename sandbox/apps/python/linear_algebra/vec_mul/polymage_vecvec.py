from __init__ import *

import sys
import subprocess
import numpy as np
from fractions import Fraction

sys.path.insert(0, ROOT)

from compiler import *
from constructs import *

def vecvec(pipe_data):

    R = Parameter(Int, "R")
    C = Parameter(Int, "C")
    
    pipe_data['R'] = R
    pipe_data['C'] = C
    

    v1 = Vector(Double, "v1", R)
    v2 = Vector(Double, "v2", C)

    val = Vector.transpose(v1) * v2

    return [val]
