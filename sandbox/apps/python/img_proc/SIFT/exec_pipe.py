#this is exec_pipe for sift

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
    total_pad = app_data['total_pad']

    img_data = app_data['img_data']
    IN1 = img_data['IN1']
    OUT = img_data['OUT']

    # lib function name
    func_name = 'pipeline_'+app_data['app']
    pipe_func = app_data[func_name]

    # lib function args
    pipe_args = []
    pipe_args += [ctypes.c_int(cols+total_pad)]
    pipe_args += [ctypes.c_int(rows+total_pad)]
    pipe_args += [ctypes.c_void_p(IN1.ctypes.data)]
    pipe_args += [ctypes.c_void_p(OUT.ctypes.data)]

    # call lib function
    pipe_func(*pipe_args)
    
    return

def sift(app_data):

    app_args = app_data['app_args']
    timer = app_args.timer

    app = app_data['app']
    lib = app_data[app+'.so']
    pool_alloc = app_data['pool_alloc']

    if pool_alloc:
        lib.pool_init()

    if timer == True:
        t1 = time.time()

    call_pipe(app_data)

    if timer == True:
        t2 = time.time()

        time_taken = float(t2) - float(t1)
        print("")
        print("[exec_pipe] : time taken to execute = ", (time_taken * 1000) / runs, " ms")

    if pool_alloc:
        lib.pool_destroy()

    return

