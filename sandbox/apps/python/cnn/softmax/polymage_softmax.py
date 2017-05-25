from __init__ import *

import sys
import subprocess
import numpy as np
from fractions import Fraction

sys.path.insert(0, ROOT)

from compiler import *
from constructs import *
from cnn_constructs import *

def polymage_softmax(pipe_data):

    N = Parameter(UInt, "N")
    X = Parameter(UInt, "X")

    x = Variable(UInt, 'x')
    n = Variable(UInt, 'n')

    Ni = Interval(UInt, 0, N-1)
    Xi = Interval(UInt, 0, X-1)
    
    input_mat = Matrix(Double, "input_mat", [X, N], [x, n])

    exp_max = Reduction(([n],[Ni]), ([x, n],[Xi, Ni]), Double, "exp_max")
    exp_max.defn = [Reduce(exp_max(n), input_mat(x, n), Op.Max)]

    expo = Matrix(Double, "expo", [X, N], [x, n])
    expo.defn = [Exp(input_mat(x, n) - exp_max(n))]

    normalizer = Reduction(([n],[Ni]), ([x, n],[Xi, Ni]), Double, "normalizer")
    normalizer.defn = [Reduce(normalizer(n), expo(x, n), Op.Sum)]
    
    output = Matrix(Double, "output", [X, N], [x, n])
    output.defn = [expo(x, n) / normalizer(n)]

    return output
