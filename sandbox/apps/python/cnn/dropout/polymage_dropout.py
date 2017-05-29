from __init__ import *

import sys
import subprocess
import numpy as np
from fractions import Fraction
import random

sys.path.insert(0, ROOT)

from compiler import *
from constructs import *
from cnn_constructs import *

def polymage_dropout(pipe_data):

    # Input Channels
    C = Parameter(UInt, "C")
    # Image size
    Y = Parameter(UInt, "Y")
    X = Parameter(UInt, "X")

    c = Variable(UInt, 'c')
    x = Variable(UInt, 'x')
    y = Variable(UInt, 'y')

    Ci = Interval(UInt, 0, C-1)
    Yi = Interval(UInt, 0, Y-1)
    Xi = Interval(UInt, 0, X-1)

    thresh = 0.15
    scale = 1.0/(1.0 - thresh) 
    
    input_mat = Matrix(Float, "input", [X, Y, C], [x, y, c])
    mask = Matrix(Float, "mask", [X, Y, C], [x, y, c])
    output = Matrix(Float, "output", [X, Y, C], [x, y, c])

    # Dropout operation
    mask.defn = [Select(Condition(random.random(), ">", thresh), scale, 0.0)]
    output.defn = [mask(x, y, c) * input_mat(x, y, c)]

    return output
