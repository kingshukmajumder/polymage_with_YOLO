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
    fir_len = app_data['fir_len']
    sig_len = app_data['sig_len']

    sig_data = app_data['sig_data']
    IN = sig_data['IN']
    IN1 = sig_data['IN1']
    OUT = sig_data['OUT']
    OUT1 = sig_data['OUT1']

    # lib function name
    func_name = 'pipeline_'+app_data['app']
    pipe_func = app_data[func_name]

    # lib function args
    pipe_args = []
    pipe_args += [ctypes.c_int(fir_len)]
    pipe_args += [ctypes.c_int(sig_len)]
    pipe_args += [ctypes.c_void_p(IN1.ctypes.data)]
    pipe_args += [ctypes.c_void_p(IN.ctypes.data)]
    pipe_args += [ctypes.c_void_p(OUT.ctypes.data)]
    pipe_args += [ctypes.c_void_p(OUT1.ctypes.data)]

    # call lib function
    pipe_func(*pipe_args)
    return

def upfirdn(app_data):
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
    print(app_data['sig_data']['OUT'])

    print('OUTPUT using instance method')
    print(app_data['sig_data']['OUT1'])

    print('IN')
    print(app_data['sig_data']['IN'])

    print('IN1')
    print(app_data['sig_data']['IN1'])

    if timer == True:
        t2 = time.time()

        time_taken = float(t2) - float(t1)
        print("")
        print("[exec_pipe] : time taken to execute = ", (time_taken * 1000) / runs, " ms")

    return

