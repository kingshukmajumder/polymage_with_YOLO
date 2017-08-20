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
    pipe_name = app_data['app']

    X1 = app_data['X1'] 
    Y1 = app_data['Y1'] 

    K1 = app_data['K1'] 
    K2 = app_data['K2'] 
    K3 = app_data['K3'] 
    K4 = app_data['K4'] 
    # K5 = app_data['K5'] 
    # K6 = app_data['K6'] 
    # K7 = app_data['K7'] 
    # K8 = app_data['K8'] 
    # K9 = app_data['K9'] 
    # K10 = app_data['K10'] 
    # K11 = app_data['K11'] 
    # K12 = app_data['K12'] 
    # K13 = app_data['K13'] 
   
    C1 = app_data['C1']  
   
    Fh1 = app_data['Fh1'] 
    Fh2 = app_data['Fh2'] 
    Fh3 = app_data['Fh3'] 
    Fh4 = app_data['Fh4'] 
    # Fh5 = app_data['Fh5'] 
    # Fh6 = app_data['Fh6'] 
    # Fh7 = app_data['Fh7'] 
    # Fh8 = app_data['Fh8'] 
    # Fh9 = app_data['Fh9'] 
    # Fh10 = app_data['Fh10'] 
    # Fh11 = app_data['Fh11'] 
    # Fh12 = app_data['Fh12'] 
    # Fh13 = app_data['Fh13']  
   
    Fw1 = app_data['Fw1'] 
    Fw2 = app_data['Fw2'] 
    Fw3 = app_data['Fw3'] 
    Fw4 = app_data['Fw4'] 
    # Fw5 = app_data['Fw5'] 
    # Fw6 = app_data['Fw6'] 
    # Fw7 = app_data['Fw7'] 
    # Fw8 = app_data['Fw8'] 
    # Fw9 = app_data['Fw9'] 
    # Fw10 = app_data['Fw10'] 
    # Fw11 = app_data['Fw11'] 
    # Fw12 = app_data['Fw12'] 
    # Fw13 = app_data['Fw13']  

    Fhm1 = app_data['Fhm1'] 
    Fhm2 = app_data['Fhm2'] 
    # Fhm3 = app_data['Fhm3'] 
    # Fhm4 = app_data['Fhm4'] 
    # Fhm5 = app_data['Fhm5'] 
   
    Fwm1 = app_data['Fwm1'] 
    Fwm2 = app_data['Fwm2'] 
    # Fwm3 = app_data['Fwm3'] 
    # Fwm4 = app_data['Fwm4'] 
    # Fwm5 = app_data['Fwm5']

    img_data = app_data['img_data']

    IN0 = img_data['IN0']
    IN1 = img_data['IN1']
    IN2 = img_data['IN2']
    IN3 = img_data['IN3']
    IN4 = img_data['IN4']
    # IN5 = img_data['IN5']
    # IN6 = img_data['IN6']
    # IN7 = img_data['IN7']
    # IN8 = img_data['IN8']
    # IN9 = img_data['IN9']
    # IN10 = img_data['IN10']
    # IN11 = img_data['IN11']
    # IN12 = img_data['IN12']
    # IN13 = img_data['IN13']
    
    OUT = img_data['OUT']

    # lib function name
    func_name = 'pipeline_'+app_data['app']
    pipe_func = app_data[func_name]

    # lib function args
    pipe_args = []
    pipe_args += [ctypes.c_int(C1)]
    
    pipe_args += [ctypes.c_int(K1)]
    pipe_args += [ctypes.c_int(K2)]
    pipe_args += [ctypes.c_int(K3)]
    pipe_args += [ctypes.c_int(K4)]
    # pipe_args += [ctypes.c_int(K6)]
    # pipe_args += [ctypes.c_int(K7)]
    # pipe_args += [ctypes.c_int(K8)]
    # pipe_args += [ctypes.c_int(K9)]
    # pipe_args += [ctypes.c_int(K10)]
    # pipe_args += [ctypes.c_int(K11)]
    # pipe_args += [ctypes.c_int(K12)]
    # pipe_args += [ctypes.c_int(K13)]

    pipe_args += [ctypes.c_int(Fh1)]
    pipe_args += [ctypes.c_int(Fh2)]
    pipe_args += [ctypes.c_int(Fh3)]
    pipe_args += [ctypes.c_int(Fh4)]
    # pipe_args += [ctypes.c_int(Fh5)]
    # pipe_args += [ctypes.c_int(Fh6)]
    # pipe_args += [ctypes.c_int(Fh7)]
    # pipe_args += [ctypes.c_int(Fh8)]
    # pipe_args += [ctypes.c_int(Fh9)]
    # pipe_args += [ctypes.c_int(Fh10)]
    # pipe_args += [ctypes.c_int(Fh11)]
    # pipe_args += [ctypes.c_int(Fh12)]
    # pipe_args += [ctypes.c_int(Fh13)]
    
    pipe_args += [ctypes.c_int(Fw1)]
    pipe_args += [ctypes.c_int(Fw2)]
    pipe_args += [ctypes.c_int(Fw3)]
    pipe_args += [ctypes.c_int(Fw4)]
    # pipe_args += [ctypes.c_int(Fw5)]
    # pipe_args += [ctypes.c_int(Fw6)]
    # pipe_args += [ctypes.c_int(Fw7)]
    # pipe_args += [ctypes.c_int(Fw8)]
    # pipe_args += [ctypes.c_int(Fw9)]
    # pipe_args += [ctypes.c_int(Fw10)]
    # pipe_args += [ctypes.c_int(Fw11)]
    # pipe_args += [ctypes.c_int(Fw12)]
    # pipe_args += [ctypes.c_int(Fw13)]

    pipe_args += [ctypes.c_int(Fhm1)]
    pipe_args += [ctypes.c_int(Fhm2)]
    # pipe_args += [ctypes.c_int(Fhm3)]
    # pipe_args += [ctypes.c_int(Fhm4)]
    # pipe_args += [ctypes.c_int(Fhm5)]

    pipe_args += [ctypes.c_int(Fwm1)]
    pipe_args += [ctypes.c_int(Fwm2)]
    # pipe_args += [ctypes.c_int(Fwm3)]
    # pipe_args += [ctypes.c_int(Fwm4)]
    # pipe_args += [ctypes.c_int(Fwm5)]
    
    pipe_args += [ctypes.c_int(X1)]
    pipe_args += [ctypes.c_int(Y1)]
    
    pipe_args += [ctypes.c_void_p(IN0.ctypes.data)]
    pipe_args += [ctypes.c_void_p(IN1.ctypes.data)]
    pipe_args += [ctypes.c_void_p(IN2.ctypes.data)]
    pipe_args += [ctypes.c_void_p(IN3.ctypes.data)]
    pipe_args += [ctypes.c_void_p(IN4.ctypes.data)]
    # pipe_args += [ctypes.c_void_p(IN5.ctypes.data)]
    # pipe_args += [ctypes.c_void_p(IN6.ctypes.data)]
    # pipe_args += [ctypes.c_void_p(IN7.ctypes.data)]
    # pipe_args += [ctypes.c_void_p(IN8.ctypes.data)]
    # pipe_args += [ctypes.c_void_p(IN9.ctypes.data)]
    # pipe_args += [ctypes.c_void_p(IN10.ctypes.data)]
    # pipe_args += [ctypes.c_void_p(IN11.ctypes.data)]
    # pipe_args += [ctypes.c_void_p(IN12.ctypes.data)]
    # pipe_args += [ctypes.c_void_p(IN13.ctypes.data)]
    pipe_args += [ctypes.c_void_p(OUT.ctypes.data)]

    # call lib function
    pipe_func(*pipe_args)
    
    return

def crp(app_data):
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
    print(app_data['img_data']['OUT'])
    if timer == True:
        t2 = time.time()

        time_taken = float(t2) - float(t1)
        print("")
        print("[exec_pipe] : time taken to execute = ", (time_taken * 1000) / runs, " ms")

    return

