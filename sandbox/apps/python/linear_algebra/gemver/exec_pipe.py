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
    rows = app_data['rows']

    img_data = app_data['img_data']

    IN_U1 = img_data['IN_U1']
    IN_U2 = img_data['IN_U2']
    IN_V1 = img_data['IN_V1']
    IN_V2 = img_data['IN_V2']
    IN_Y = img_data['IN_Y']
    IN_Z = img_data['IN_Z']
    OUT_X = img_data['OUT_X']
    OUT_W = img_data['OUT_W']
    IN_A =  img_data['IN_A']

    # lib function name
    func_name = 'pipeline_'+app_data['app']
    pipe_func = app_data[func_name]

    # lib function args
    pipe_args = []
    pipe_args += [ctypes.c_int(rows)]
    pipe_args += [ctypes.c_void_p(IN_A.ctypes.data)]
    pipe_args += [ctypes.c_void_p(IN_U1.ctypes.data)]
    pipe_args += [ctypes.c_void_p(IN_U2.ctypes.data)]
    pipe_args += [ctypes.c_void_p(IN_V1.ctypes.data)]
    pipe_args += [ctypes.c_void_p(IN_V2.ctypes.data)]
    pipe_args += [ctypes.c_void_p(IN_Y.ctypes.data)]
    pipe_args += [ctypes.c_void_p(IN_Z.ctypes.data)]
    pipe_args += [ctypes.c_void_p(OUT_X.ctypes.data)]
    pipe_args += [ctypes.c_void_p(OUT_W.ctypes.data)]

    # call lib function
    pipe_func(*pipe_args)
    
    return

def gemver(app_data):
    it  = 0
    app_args = app_data['app_args']
   
    runs = int(app_args.runs)
    timer = app_args.timer
    if timer == True:
        t1 = time.time()

    while it < runs :
        call_pipe(app_data)
        it += 1

    print('OUTPUT X')
    print(app_data['img_data']['OUT_X'])
    print('OUTPUT W')
    print(app_data['img_data']['OUT_W'])

    if timer == True:
        t2 = time.time()

        time_taken = float(t2) - float(t1)
        print("")
        print("[exec_pipe] : time taken to execute = ", (time_taken * 1000) / runs, " ms")

    return

