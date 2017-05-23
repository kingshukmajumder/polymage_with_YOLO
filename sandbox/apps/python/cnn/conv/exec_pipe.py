import sys
import os
import ctypes
import numpy as np
import time

from printer import print_line

from compiler   import *
from constructs import *
from utils import *

def call_pipe(app_data):
    K = app_data['K']
    C = app_data['C']
    Y = app_data['Y']
    X = app_data['X']
    Fh = app_data['Fh']
    Fw = app_data['Fw']

    img_data = app_data['img_data']
    IN = img_data['IN']
    IN1 = img_data['IN1']
    OUT = img_data['OUT']

    # lib function name
    func_name = 'pipeline_'+app_data['app']
    pipe_func = app_data[func_name]

    # lib function args
    pipe_args = []
    pipe_args += [ctypes.c_int(C)]
    pipe_args += [ctypes.c_int(Fh)]
    pipe_args += [ctypes.c_int(Fw)]
    pipe_args += [ctypes.c_int(K)]
    pipe_args += [ctypes.c_int(X)]
    pipe_args += [ctypes.c_int(Y)]
    pipe_args += [ctypes.c_void_p(IN.ctypes.data)]
    pipe_args += [ctypes.c_void_p(IN1.ctypes.data)]
    pipe_args += [ctypes.c_void_p(OUT.ctypes.data)]

    # call lib function
    pipe_func(*pipe_args)
    
    return

def conv(app_data):
    it  = 0
    app_args = app_data['app_args']
   
    runs = int(app_args.runs)
    timer = app_args.timer
    if timer == True:
        t1 = time.time()

    while it < runs :
        call_pipe(app_data)
        it += 1

    if timer == True:
        t2 = time.time()

        time_taken = float(t2) - float(t1)
        print("")
        print("[exec_pipe] : time taken to execute = ", (time_taken * 1000) / runs, " ms")

    return

