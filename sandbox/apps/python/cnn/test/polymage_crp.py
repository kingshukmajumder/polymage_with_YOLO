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
    # K5 = Parameter(UInt, "K5")
    # K6 = Parameter(UInt, "K6")
    # K7 = Parameter(UInt, "K7")
    # K8 = Parameter(UInt, "K8")
    # K9 = Parameter(UInt, "K9")
    # K10 = Parameter(UInt, "K10")
    # K11 = Parameter(UInt, "K11")
    # K12 = Parameter(UInt, "K12")
    # K13 = Parameter(UInt, "K13")

    C1 = Parameter(UInt, "C1")

    Fh1 = Parameter(UInt, "Fh1")
    Fh2 = Parameter(UInt, "Fh2")
    Fh3 = Parameter(UInt, "Fh3")
    Fh4 = Parameter(UInt, "Fh4")
    # Fh5 = Parameter(UInt, "Fh5")
    # Fh6 = Parameter(UInt, "Fh6")
    # Fh7 = Parameter(UInt, "Fh7")
    # Fh8 = Parameter(UInt, "Fh8")
    # Fh9 = Parameter(UInt, "Fh9")
    # Fh10 = Parameter(UInt, "Fh10")
    # Fh11 = Parameter(UInt, "Fh11")
    # Fh12 = Parameter(UInt, "Fh12")
    # Fh13 = Parameter(UInt, "Fh13")

    Fw1 = Parameter(UInt, "Fw1")
    Fw2 = Parameter(UInt, "Fw2")
    Fw3 = Parameter(UInt, "Fw3")
    Fw4 = Parameter(UInt, "Fw4")
    # Fw5 = Parameter(UInt, "Fw5")
    # Fw6 = Parameter(UInt, "Fw6")
    # Fw7 = Parameter(UInt, "Fw7")
    # Fw8 = Parameter(UInt, "Fw8")
    # Fw9 = Parameter(UInt, "Fw9")
    # Fw10 = Parameter(UInt, "Fw10")
    # Fw11 = Parameter(UInt, "Fw11")
    # Fw12 = Parameter(UInt, "Fw12")
    # Fw13 = Parameter(UInt, "Fw13")


    Fhm1 = Parameter(UInt, "Fhm1")
    Fhm2 = Parameter(UInt, "Fhm2")
    # Fhm3 = Parameter(UInt, "Fhm3")
    # Fhm4 = Parameter(UInt, "Fhm4")
    # Fhm5 = Parameter(UInt, "Fhm5")

    Fwm1 = Parameter(UInt, "Fwm1")
    Fwm2 = Parameter(UInt, "Fwm2")
    # Fwm3 = Parameter(UInt, "Fwm3")
    # Fwm4 = Parameter(UInt, "Fwm4")
    # Fwm5 = Parameter(UInt, "Fwm5")

    input_mat1 = Matrix(Double, "input", [X1, Y1, C1])
    weights1 = Matrix(Double, "weights1", [Fw1, Fh1, C1, K1])
    weights2 = Matrix(Double, "weights2", [Fw2, Fh2, K1, K2])
    weights3 = Matrix(Double, "weights3", [Fw3, Fh3, K2, K3])
    weights4 = Matrix(Double, "weights4", [Fw4, Fh4, K3, K4])
    # weights5 = Matrix(Double, "weights5", [Fw5, Fh5, K4, K5])
    # weights6 = Matrix(Double, "weights6", [Fw6, Fh6, K5, K6])
    # weights7 = Matrix(Double, "weights7", [Fw7, Fh7, K6, K7])
    # weights8 = Matrix(Double, "weights8", [Fw8, Fh8, K7, K8])
    # weights9 = Matrix(Double, "weights9", [Fw9, Fh9, K8, K9])
    # weights10 = Matrix(Double, "weights10", [Fw10, Fh10, K9, K10])
    # weights11 = Matrix(Double, "weights11", [Fw11, Fh11, K10, K11])
    # weights12 = Matrix(Double, "weights12", [Fw12, Fh12, K11, K12])
    # weights13 = Matrix(Double, "weights13", [Fw13, Fh13, K12, K13])


    conv1 = Network.convolution(input_mat1, weights1, "conv1",_stride=1,_pad=1)
    relu1 = Network.ReLU(conv1, "relu1")
    conv2 = Network.convolution(relu1, weights2, "conv2",_stride=1,_pad=1)
    relu2 = Network.ReLU(conv2, "relu2")
    maxpool1 = Network.maxpool(relu2, Fwm1, Fhm1, 2, "maxpool1")

    conv3 = Network.convolution(maxpool1, weights3, "conv3",_stride=1,_pad=1)
    relu3 = Network.ReLU(conv3, "relu3")
    conv4 = Network.convolution(relu3, weights4, "conv4",_stride=1,_pad=1)
    relu4 = Network.ReLU(conv4, "relu4")
    maxpool2 = Network.maxpool(relu4, Fwm2, Fhm2, 2, "maxpool2")

    # conv5 = Network.convolution(maxpool2, weights5, "conv5",_stride=1,_pad=1)
    # relu5 = Network.ReLU(conv5, "relu5")
    # conv6 = Network.convolution(relu5, weights6, "conv6",_stride=1,_pad=1)
    # relu6 = Network.ReLU(conv6, "relu6")
    # conv7 = Network.convolution(relu6, weights7, "conv7",_stride=1,_pad=1)
    # relu7 = Network.ReLU(conv7, "relu7")
    # maxpool3 = Network.maxpool(relu7, Fwm3, Fhm3, 2, "maxpool3")
    
    # conv8 = Network.convolution(maxpool3, weights8, "conv8",_stride=1,_pad=1)
    # relu8 = Network.ReLU(conv8, "relu8")
    # conv9 = Network.convolution(relu8, weights9, "conv9",_stride=1,_pad=1)
    # relu9 = Network.ReLU(conv9, "relu9")
    # conv10 = Network.convolution(relu9, weights10, "conv10",_stride=1,_pad=1)
    # relu10 = Network.ReLU(conv10, "relu10")
    # maxpool4 = Network.maxpool(relu10, Fwm4, Fhm4, 2, "maxpool4")

    # conv11 = Network.convolution(maxpool4, weights11, "conv11",_stride=1,_pad=1)
    # relu11 = Network.ReLU(conv11, "relu11")
    # conv12 = Network.convolution(relu11, weights12, "conv12",_stride=1,_pad=1)
    # relu12 = Network.ReLU(conv12, "relu12")
    # conv13 = Network.convolution(relu12, weights13, "conv13",_stride=1,_pad=1)
    # relu13 = Network.ReLU(conv13, "relu13")
    # maxpool5 = Network.maxpool(relu13, Fwm5, Fhm5, 2, "maxpool5")

    return maxpool2

