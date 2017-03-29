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

    sig_data = app_data['sig_data']
    IN = sig_data['IN']
    OUT = sig_data['OUT']
    OUT0 = sig_data['OUT0']
    OUT1 = sig_data['OUT1']
    OUT2 = sig_data['OUT2']
    OUT3 = sig_data['OUT3']

    # lib function name
    func_name = 'pipeline_'+app_data['app']
    pipe_func = app_data[func_name]

    # lib function args
    pipe_args = []
    pipe_args += [ctypes.c_uint(length)]
    pipe_args += [ctypes.c_void_p(IN.ctypes.data)]
    pipe_args += [ctypes.c_void_p(OUT0.ctypes.data)]
    pipe_args += [ctypes.c_void_p(OUT1.ctypes.data)]
    pipe_args += [ctypes.c_void_p(OUT2.ctypes.data)]
    pipe_args += [ctypes.c_void_p(OUT3.ctypes.data)]
    pipe_args += [ctypes.c_void_p(OUT.ctypes.data)]

    # call lib function
    pipe_func(*pipe_args)
    return

def sub_band(app_data):
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

    if timer == True:
        t2 = time.time()

        time_taken = float(t2) - float(t1)
        print("")
        print("[exec_pipe] : time taken to execute = ", (time_taken * 1000) / runs, " ms")

    fs = app_data['freq']
    y = app_data['sig_data']['IN']
    lnx = len(y)
    freq = np.pi * np.ones(lnx)
    freq[:lnx-1] = np.arange(-np.pi, np.pi, 2*np.pi/(lnx-1))
    X=np.fft.fftshift(np.fft.fft(y,lnx))
    b0 = app_data['sig_data']['OUT0']
    b1 = app_data['sig_data']['OUT1']
    b2 = app_data['sig_data']['OUT2']
    b3 = app_data['sig_data']['OUT3']
    plt.figure(3)
    plt.title('Four bands in freq domain')
    plt.subplot(411)
    plt.plot(freq/np.pi,abs(np.fft.fftshift(np.fft.fft(b0,lnx))))
    plt.ylabel('|B0|')
    plt.axis([0, np.pi/np.pi, min(abs(np.fft.fft(b0))), max(abs(np.fft.fft(b0)))])
    plt.subplot(412)
    plt.plot(freq/np.pi,abs(np.fft.fftshift(np.fft.fft(b1,lnx))))
    plt.ylabel('|B1|')
    plt.axis([0, np.pi/np.pi, min(abs(np.fft.fft(b0))), max(abs(np.fft.fft(b1)))])
    plt.subplot(413)
    plt.plot(freq/np.pi,abs(np.fft.fftshift(np.fft.fft(b2,lnx))))
    plt.ylabel('|B2|')
    plt.axis([0, np.pi/np.pi, min(abs(np.fft.fft(b2))), max(abs(np.fft.fft(b2)))])
    plt.subplot(414)
    plt.plot(freq/np.pi,abs(np.fft.fftshift(np.fft.fft(b3,lnx))))
    plt.ylabel('|B3|')
    plt.axis([0, np.pi/np.pi, min(abs(np.fft.fft(b3))), max(abs(np.fft.fft(b3)))])
    plt.show()
    fs1 = int(fs // 4)
    spiowav.write('band0.wav', fs1, b0.astype(np.int16))
    spiowav.write('band1.wav', fs1, b1.astype(np.int16))
    spiowav.write('band2.wav', fs1, b2.astype(np.int16))
    spiowav.write('band3.wav', fs1, b3.astype(np.int16))
    ys = app_data['sig_data']['OUT']
    plt.figure(5)
    plt.subplot(211)
    plt.plot(freq/np.pi, abs(X))
    plt.ylabel('|X|')
    plt.axis([0, np.pi/np.pi, min(abs(X)), max(abs(X))])
    plt.title('Comparison')
    plt.legend('Original band')
    plt.subplot(212)
    plt.plot(freq/np.pi,abs(np.fft.fftshift(np.fft.fft(ys,lnx))),'r')
    plt.ylabel('|Band|')
    plt.axis([0, np.pi/np.pi, min(abs(np.fft.fft(ys))), max(abs(np.fft.fft(ys)))])
    plt.legend('Synthesized band')
    plt.show()
    fs = int(fs)
    spiowav.write('woman2_synth.wav', fs, ys.astype(np.int16))

    return

