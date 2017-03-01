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
    sig_len = app_data['sig_len']
    blength = app_data['blength']
    alength = app_data['alength']

    sig_data = app_data['sig_data']
    IN = sig_data['IN']
    IN1 = sig_data['IN1']
    IN2 = sig_data['IN2']
    OUT = sig_data['OUT']

    # lib function name
    func_name = 'pipeline_'+app_data['app']
    pipe_func = app_data[func_name]

    # lib function args
    pipe_args = []
    pipe_args += [ctypes.c_int(sig_len)]
    pipe_args += [ctypes.c_int(blength)]
    pipe_args += [ctypes.c_int(alength)]
    pipe_args += [ctypes.c_void_p(IN2.ctypes.data)]
    pipe_args += [ctypes.c_void_p(IN1.ctypes.data)]
    pipe_args += [ctypes.c_void_p(IN.ctypes.data)]
    pipe_args += [ctypes.c_void_p(OUT.ctypes.data)]

    # call lib function
    pipe_func(*pipe_args)
    return

def lfilter(app_data):
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

    print('IN')
    print(app_data['sig_data']['IN'])

    print('IN1')
    print(app_data['sig_data']['IN1'])

    print('IN2')
    print(app_data['sig_data']['IN2'])

    if timer == True:
        t2 = time.time()

        time_taken = float(t2) - float(t1)
        print("")
        print("[exec_pipe] : time taken to execute = ", (time_taken * 1000) / runs, " ms")

    return

