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
    N = app_data['N']
    Oc = app_data['Oc']
    Ic = app_data['Ic']
    Y = app_data['Y']
    X = app_data['X']
    Kh = app_data['Kh']
    Kw = app_data['Kw']

    img_data = app_data['img_data']
    IN = img_data['IN']
    IN1 = img_data['IN1']
    OUT = img_data['OUT']

    # lib function name
    func_name = 'pipeline_'+app_data['app']
    pipe_func = app_data[func_name]

    # lib function args
    pipe_args = []
    pipe_args += [ctypes.c_int(N)]
    pipe_args += [ctypes.c_int(Oc)]
    pipe_args += [ctypes.c_int(Ic)]
    pipe_args += [ctypes.c_int(Y)]
    pipe_args += [ctypes.c_int(X)]
    pipe_args += [ctypes.c_int(Kh)]
    pipe_args += [ctypes.c_int(Kw)]
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

    print('OUTPUT')
    print(app_data['img_data']['OUT'])

    if timer == True:
        t2 = time.time()

        time_taken = float(t2) - float(t1)
        print("")
        print("[exec_pipe] : time taken to execute = ", (time_taken * 1000) / runs, " ms")

    return

