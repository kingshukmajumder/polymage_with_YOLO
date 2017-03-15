from __init__ import *

import sys
import subprocess
import numpy as np
from fractions import Fraction

sys.path.insert(0, ROOT)

from compiler import *
from constructs import *

def interp_fft(pipe_data):

    N = Parameter(UInt, "N")

    pipe_data['N'] = N

    sig = Wave(Double, "sig", N)

    sig_up = sig.interp_fft(10, "sig_up")

    return sig_up
