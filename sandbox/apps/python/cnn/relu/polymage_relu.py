from __init__ import *

import sys
import subprocess
import numpy as np
from fractions import Fraction

sys.path.insert(0, ROOT)

from compiler import *
from constructs import *
from cnn_constructs import *

def polymage_relu(pipe_data):

    # Channel width
    C = Parameter(UInt, "C")
    # Input / Output dimensions
    Y = Parameter(UInt, "Y")
    X = Parameter(UInt, "X")

    c = Variable(UInt, 'c')
    x = Variable(UInt, 'x')
    y = Variable(UInt, 'y')

    Ci = Interval(UInt, 0, C-1)
    Yi = Interval(UInt, 0, Y-1)
    Xi = Interval(UInt, 0, X-1)
    
    # Input image
    input_mat = Matrix(Float, "input", [X, Y, C], [x, y, c])
    # Rectified Linear Unit
    output = Matrix(Float, "output", [X, Y, C], [x, y, c])
    
    output.defn = [Max(0.0, input_mat(x, y, c))]

    return output
