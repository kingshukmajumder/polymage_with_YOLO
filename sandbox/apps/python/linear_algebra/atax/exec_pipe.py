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
    cols = app_data['cols']

    img_data = app_data['img_data']

    IN_X = img_data['IN_X']
    OUT_Y = img_data['OUT_Y']
    IN_A =  img_data['IN_A']

    # lib function name
    func_name = 'pipeline_'+app_data['app']
    pipe_func = app_data[func_name]

    # lib function args
    pipe_args = []
    pipe_args += [ctypes.c_int(cols)]
    pipe_args += [ctypes.c_int(rows)]
    pipe_args += [ctypes.c_void_p(IN_A.ctypes.data)]
    pipe_args += [ctypes.c_void_p(IN_X.ctypes.data)]
    pipe_args += [ctypes.c_void_p(OUT_Y.ctypes.data)]

    # call lib function
    pipe_func(*pipe_args)
    
    return

def atax(app_data):
    it  = 0
    app_args = app_data['app_args']
   
    runs = int(app_args.runs)
    timer = app_args.timer
    if timer == True:
        t1 = time.time()

    while it < runs :
        call_pipe(app_data)
        it += 1

    print('OUTPUT Y')
    print(app_data['img_data']['OUT_Y'])

    if timer == True:
        t2 = time.time()

        time_taken = float(t2) - float(t1)
        print("")
        print("[exec_pipe] : time taken to execute = ", (time_taken * 1000) / runs, " ms")

    return

