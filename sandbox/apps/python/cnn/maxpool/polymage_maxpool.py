from __init__ import *

import sys
import subprocess
import numpy as np
from fractions import Fraction

sys.path.insert(0, ROOT)

from compiler import *
from constructs import *
from cnn_constructs import *

def polymage_maxpool(pipe_data):

    # Channels
    K = Parameter(Int, "K")
    # Input dimensions
    Y = Parameter(Int, "Y")
    X = Parameter(Int, "X")
    # Pool size kernel
    Fh = Parameter(Int, "Fh")
    Fw = Parameter(Int, "Fw")

    # Input Matrix
    input_mat = DataLayer(Double, "input_mat", [X, Y, K])

    # Maxpool operation (Fh x Fw)
    maxpool = Network.maxpool(input_mat, Fh, Fw, 2, "maxpool")
    return maxpool

    #k = Variable(Int, 'k')
    #x = Variable(Int, 'x')
    #y = Variable(Int, 'y')
    #fh = Variable(Int, 'fh')
    #fw = Variable(Int, 'fw')

    #Ki = Interval(Int, 0, K-1)
    #Fhi = Interval(Int, 0, Fh-1)
    #Fwi = Interval(Int, 0, Fw-1)

    #Xi = Interval(Int, 0, (X-Fw)/2)
    #Yi = Interval(Int, 0, (Y-Fh)/2)

    #output = Reduction(([x, y, k],[Xi, Yi, Ki]), ([k, y, x, fh, fw],[Ki, Yi, Xi, Fhi, Fwi]), Double, "output")
    #output.defn = [Reduce(output(x, y, k), input_mat(2*x+fw, 2*y+fh, k), Op.Max)]
    #return output
