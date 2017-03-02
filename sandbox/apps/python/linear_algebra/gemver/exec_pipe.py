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
    rows1 = app_data['rows1']
    cols1 = app_data['cols1']
    #rows2 = app_data['rows2']
    #cols2 = app_data['cols2']

    img_data = app_data['img_data']
    IN = img_data['IN']
    IN1 = img_data['IN1']
    IN2 = img_data['IN2']
    OUT = img_data['OUT']
    OUT1 = img_data['OUT1']

    # lib function name
    func_name = 'pipeline_'+app_data['app']
    pipe_func = app_data[func_name]

    # lib function args
    pipe_args = []
    pipe_args += [ctypes.c_int(cols1)]
    #pipe_args += [ctypes.c_int(cols2)]
    pipe_args += [ctypes.c_int(rows1)]
    #pipe_args += [ctypes.c_int(rows2)]
    pipe_args += [ctypes.c_void_p(IN.ctypes.data)]
    pipe_args += [ctypes.c_void_p(IN1.ctypes.data)]
    pipe_args += [ctypes.c_void_p(IN2.ctypes.data)]
    pipe_args += [ctypes.c_void_p(OUT.ctypes.data)]
    pipe_args += [ctypes.c_void_p(OUT1.ctypes.data)]

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

    print('OUTPUT1')
    print(app_data['img_data']['OUT'])
    print('OUTPUT2')
    print(app_data['img_data']['OUT1'])

    if timer == True:
        t2 = time.time()

        time_taken = float(t2) - float(t1)
        print("")
        print("[exec_pipe] : time taken to execute = ", (time_taken * 1000) / runs, " ms")

    return

