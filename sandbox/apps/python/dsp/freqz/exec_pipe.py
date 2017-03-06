import sys
import os
import ctypes
import numpy as np
import time
from scipy import signal
import matplotlib.pyplot as plt

from printer import print_line

from compiler   import *
from constructs import *
from utils import *

def call_pipe(app_data):
    length = app_data['length']

    sig_data = app_data['sig_data']
    IN = sig_data['IN']
    OUT1 = sig_data['OUT1']
    OUT2 = sig_data['OUT2']

    # lib function name
    func_name = 'pipeline_'+app_data['app']
    pipe_func = app_data[func_name]

    # lib function args
    pipe_args = []
    pipe_args += [ctypes.c_uint(length)]
    pipe_args += [ctypes.c_void_p(IN.ctypes.data)]
    pipe_args += [ctypes.c_void_p(OUT1.ctypes.data)]
    pipe_args += [ctypes.c_void_p(OUT2.ctypes.data)]

    # call lib function
    pipe_func(*pipe_args)
    return

def freqz(app_data):
    it  = 0
    app_args = app_data['app_args']
   
    runs = int(app_args.runs)
    timer = app_args.timer
    if timer == True:
        t1 = time.time()

    while it < runs :
        call_pipe(app_data)
        it += 1

    print('OUTPUT: w')
    print(app_data['sig_data']['OUT2'])

    print('OUTPUT: h')
    print(app_data['sig_data']['OUT1'])

    print('IN')
    print(app_data['sig_data']['IN'])

    if timer == True:
        t2 = time.time()

        time_taken = float(t2) - float(t1)
        print("")
        print("[exec_pipe] : time taken to execute = ", (time_taken * 1000) / runs, " ms")

    print()
    print("Plotting frequency response of 2 FIR filters...")
    print("Blue: low pass with cutoff frequency = 0.5 Hz")
    print("Red: band stop with low cutoff frequency = 0.3 Hz; high cutoff frequency = 0.8 Hz")

    w1, h1 = app_data['sig_data']['OUT2'].copy(), app_data['sig_data']['OUT1'].copy()
    app_data['sig_data']['IN'] = signal.firwin(41, [0.3, 0.8])
    call_pipe(app_data)
    w2, h2 = app_data['sig_data']['OUT2'], app_data['sig_data']['OUT1']

    assert len(w1) == len(w2) and all([i == j for i, j in zip(w1, w2)])

    plt.title('Digital filter frequency response')
    plt.plot(w1, 20*np.log10(np.abs(h1)), 'b')
    plt.plot(w2, 20*np.log10(np.abs(h2)), 'r')
    plt.ylabel('Amplitude Response (dB)')
    plt.xlabel('Frequency (rad/sample)')
    plt.grid()
    plt.show()

    return

