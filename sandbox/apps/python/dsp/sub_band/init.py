import sys
import os.path
from PIL import Image
import numpy as np
import scipy.io.wavfile as spiowav
from arg_parser import parse_args

from printer import print_header, print_usage, print_line

def init_signals(app_data):
    print("[init.py] : initializing signal...")

    app_args = app_data['app_args']

    # input signal
    wav = spiowav.read('woman2_orig.wav')
    Fs = float(wav[0])
    sig = np.array(wav[1])
    length = len(sig)

    # convert to float arrays
    IN = np.array(sig)
    IN = IN.astype(np.float64).ravel()

    # final output synthesized signal
    OUT = np.zeros(length).astype(np.float64).ravel()
    # output band signals
    OUT0 = np.zeros(length//4).astype(np.float64).ravel()
    OUT1 = np.zeros(length//4).astype(np.float64).ravel()
    OUT2 = np.zeros(length//4).astype(np.float64).ravel()
    OUT3 = np.zeros(length//4).astype(np.float64).ravel()

    sig_data = {}
    sig_data['IN'] = IN
    sig_data['OUT'] = OUT
    sig_data['OUT0'] = OUT0
    sig_data['OUT1'] = OUT1
    sig_data['OUT2'] = OUT2
    sig_data['OUT3'] = OUT3

    app_data['sig_data'] = sig_data
    app_data['length'] = length
    app_data['freq'] = Fs

    return

def get_input(app_data):
    # parse the command-line arguments
    app_args = parse_args()
    app_data['app_args'] = app_args

    app_data['mode'] = app_args.mode
    app_data['runs'] = int(app_args.runs)
    app_data['graph_gen'] = bool(app_args.graph_gen)
    app_data['timer'] = app_args.timer

    # storage optimization
    app_data['optimize_storage'] = bool(app_args.optimize_storage)
    # early freeing of allocated arrays
    app_data['early_free'] = bool(app_args.early_free)
    # pool allocate option
    app_data['pool_alloc'] = bool(app_args.pool_alloc)

    app_data['blas'] = bool(app_args.blas)

    app_data['matrix'] = bool(app_args.matrix)

    app_data['fft'] = bool(app_args.fft)

    return

def init_all(app_data):
    pipe_data = {}
    app_data['pipe_data'] = pipe_data

    get_input(app_data)

    init_signals(app_data)

    return

