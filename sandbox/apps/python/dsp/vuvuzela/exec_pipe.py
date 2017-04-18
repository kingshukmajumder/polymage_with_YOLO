import sys
import os
import ctypes
import numpy as np
import scipy.io.wavfile as spiowav
import scipy.signal as signal
import time
import matplotlib.pyplot as plt

from printer import print_line

from compiler   import *
from constructs import *
from utils import *

def call_pipe(app_data):
    length = app_data['length']
    freq = app_data['freq']

    sig_data = app_data['sig_data']
    IN = sig_data['IN']
    OUT = sig_data['OUT']

    # lib function name
    func_name = 'pipeline_'+app_data['app']
    pipe_func = app_data[func_name]

    # lib function args
    pipe_args = []
    pipe_args += [ctypes.c_double(freq)]
    pipe_args += [ctypes.c_uint(length)]
    pipe_args += [ctypes.c_void_p(IN.ctypes.data)]
    pipe_args += [ctypes.c_void_p(OUT.ctypes.data)]

    # call lib function
    pipe_func(*pipe_args)
    return

def vuvu(app_data):
    it  = 0
    app_args = app_data['app_args']
    length = app_data['length']
    freq = app_data['freq']

    sig_data = app_data['sig_data']
    IN = sig_data['IN']
    OUT = sig_data['OUT']

    # lib function name
    func_name = 'pipeline_'+app_data['app']
    pipe_func = app_data[func_name]

    # lib function args
    pipe_args = []
    pipe_args += [ctypes.c_double(freq)]
    pipe_args += [ctypes.c_uint(length)]
    pipe_args += [ctypes.c_void_p(IN.ctypes.data)]
    pipe_args += [ctypes.c_void_p(OUT.ctypes.data)]
   
    runs = int(app_args.runs)
    timer = app_args.timer
    if timer == True:
        t1 = time.time()

    while it < runs :
        pipe_func(*pipe_args)
        it += 1

    if timer == True:
        t2 = time.time()

        time_taken = float(t2) - float(t1)
        print("")
        print("number of runs = ", runs)
        print("[exec_pipe] : time taken to execute = ", (time_taken * 1000) / runs, " ms")

    print('OUTPUT')
    print(app_data['sig_data']['OUT'])

    print('IN')
    print(app_data['sig_data']['IN'])

    Fs = app_data['freq']
    y = app_data['sig_data']['IN']
    yf = np.trim_zeros(app_data['sig_data']['OUT'])
    print("length of final signal is: " + str(len(yf)))
    F, P = signal.welch(y, fs=Fs, window=np.array(np.ones(8192)), nperseg=8192, scaling='spectrum')
    Ff, Pf = signal.welch(yf, fs=Fs, window=np.array(np.ones(8192)), nperseg=8192, scaling='spectrum')
    plt.semilogx(F, 10*np.log10(P), 'b', label='Original signal')
    plt.semilogx(Ff, 10*np.log10(Pf), 'g', label='Final filtered signal')
    plt.xlabel('Frequency in Hz')
    plt.ylabel('Power Spectrum (dB)')
    plt.ylim((-10, 60))
    plt.legend()
    plt.show()
    spiowav.write('vuvuzela_filtered.wav', int(Fs), yf.astype(np.int16))

    return

