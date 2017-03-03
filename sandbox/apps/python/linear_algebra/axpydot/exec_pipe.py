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

    IN_U = img_data['IN_U']  
    IN_V = img_data['IN_V']  
    IN_W = img_data['IN_W']  
    IN_Z = img_data['IN_Z']  
    OUT_R = img_data['OUT_R']
    
    # lib function name
    func_name = 'pipeline_'+app_data['app']
    pipe_func = app_data[func_name]

    # lib function args
    pipe_args = []
    pipe_args += [ctypes.c_int(rows)]
    pipe_args += [ctypes.c_void_p(IN_U.ctypes.data)]
    pipe_args += [ctypes.c_void_p(IN_V.ctypes.data)]
    pipe_args += [ctypes.c_void_p(IN_W.ctypes.data)]
    pipe_args += [ctypes.c_void_p(IN_Z.ctypes.data)]
    pipe_args += [ctypes.c_void_p(OUT_R.ctypes.data)]

    # call lib function
    pipe_func(*pipe_args)
    
    return

def axpydot(app_data):
    it  = 0
    app_args = app_data['app_args']
   
    runs = int(app_args.runs)
    timer = app_args.timer
    if timer == True:
        t1 = time.time()

    while it < runs :
        call_pipe(app_data)
        it += 1

    print('OUTPUT R')
    print(app_data['img_data']['OUT_R'])

    if timer == True:
        t2 = time.time()

        time_taken = float(t2) - float(t1)
        print("")
        print("[exec_pipe] : time taken to execute = ", (time_taken * 1000) / runs, " ms")

    return

