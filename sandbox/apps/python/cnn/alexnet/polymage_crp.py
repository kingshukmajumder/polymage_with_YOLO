from __init__ import *

import sys
import subprocess
import numpy as np
from fractions import Fraction

sys.path.insert(0, ROOT)

from compiler import *
from constructs import *
from cnn_constructs import *

def polymage_crp(pipe_data):

    X1 = Parameter(UInt, "X1")
    Y1 = Parameter(UInt, "Y1")

    K1 = Parameter(UInt, "K1")
    K2 = Parameter(UInt, "K2")
    K3 = Parameter(UInt, "K3")
    K4 = Parameter(UInt, "K4")
    K5 = Parameter(UInt, "K5")

    C1 = Parameter(UInt, "C1")

    Fh1 = Parameter(UInt, "Fh1")
    Fh2 = Parameter(UInt, "Fh2")
    Fh3 = Parameter(UInt, "Fh3")
    Fh4 = Parameter(UInt, "Fh4")
    Fh5 = Parameter(UInt, "Fh5")

    Fw1 = Parameter(UInt, "Fw1")
    Fw2 = Parameter(UInt, "Fw2")
    Fw3 = Parameter(UInt, "Fw3")
    Fw4 = Parameter(UInt, "Fw4")
    Fw5 = Parameter(UInt, "Fw5")

    Fhm1 = Parameter(UInt, "Fhm1")
    Fhm2 = Parameter(UInt, "Fhm2")
    Fhm5 = Parameter(UInt, "Fhm5")

    Fwm1 = Parameter(UInt, "Fwm1")
    Fwm2 = Parameter(UInt, "Fwm2")
    Fwm5 = Parameter(UInt, "Fwm5")

    input_mat1 = Matrix(Double, "input", [X1, Y1, C1])
    weights1 = Matrix(Double, "weights1", [Fw1, Fh1, C1, K1])
    weights2 = Matrix(Double, "weights2", [Fw2, Fh2, K1, K2])
    weights3 = Matrix(Double, "weights3", [Fw3, Fh3, K2, K3])
    weights4 = Matrix(Double, "weights4", [Fw4, Fh4, K3, K4])
    weights5 = Matrix(Double, "weights5", [Fw5, Fh5, K4, K5])

    conv1 = Network.convolution(input_mat1, weights1, "conv1",_stride=4,_pad=0)
    relu1 = Network.ReLU(conv1, "relu1")
    maxpool1 = Network.maxpool(relu1, Fwm1, Fhm1, 2, "maxpool1")

    conv2 = Network.convolution(maxpool1,weights2,"conv2",_stride=1,_pad=2)
    relu2 = Network.ReLU(conv2, "relu2")
    maxpool2 = Network.maxpool(relu2, Fwm2, Fhm2, 2, "maxpool2")

    conv3 = Network.convolution(maxpool2,weights3,"conv3",_stride=1,_pad=1)
    relu3 = Network.ReLU(conv3, "relu3")
    
    conv4 = Network.convolution(relu3,weights4,"conv4",_stride=1,_pad=1)
    relu4 = Network.ReLU(conv4, "relu4")
    
    conv5 = Network.convolution(relu4,weights5,"conv5",_stride=1,_pad=1)
    relu5 = Network.ReLU(conv2, "relu4")
    maxpool5 = Network.maxpool(relu5, Fwm5, Fhm5, 2, "maxpool5")
    
    return maxpool5

