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
    length = app_data['length']

    sig_data = app_data['sig_data']
    r = sig_data['r']
    H = sig_data['H']
    F = sig_data['F']
    OUT = sig_data['OUT']

    # lib function name
    func_name = 'pipeline_'+app_data['app']
    pipe_func = app_data[func_name]

    # lib function args
    pipe_args = []
    pipe_args += [ctypes.c_uint(length)]
    pipe_args += [ctypes.c_void_p(F.ctypes.data)]
    pipe_args += [ctypes.c_void_p(H.ctypes.data)]
    pipe_args += [ctypes.c_void_p(r.ctypes.data)]
    pipe_args += [ctypes.c_void_p(OUT.ctypes.data)]

    # call lib function
    pipe_func(*pipe_args)
    return

def filterbank(app_data):
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

    print('r')
    print(app_data['sig_data']['r'])

    print('H')
    print(app_data['sig_data']['H'])

    print('F')
    print(app_data['sig_data']['F'])

    if timer == True:
        t2 = time.time()

        time_taken = float(t2) - float(t1)
        print("")
        print("[exec_pipe] : time taken to execute = ", (time_taken * 1000) / runs, " ms")

    f = open('output', 'w')
    z = '\n'.join([str(x) for x in app_data['sig_data']['OUT'].astype(np.int64)])
    f.write(z + '\n')
    f.close()

    return

