import sys
import os.path
from PIL import Image
import numpy as np
from arg_parser import parse_args

from printer import print_header, print_usage, print_line

def init_signals(app_data):
    print("[init.py] : initializing signal...")

    app_args = app_data['app_args']

    # input signal
    length = 10000
    t = np.arange(0, 1, 1.0 / length)
    sig = 2.5+np.cos(2*np.pi*203*t)+np.sin(2*np.pi*721*t)+np.cos(2*np.pi*1001*t)

    # convert to float arrays
    IN = np.array(sig)
    IN = IN.astype(np.float64).ravel()

    # final output analytic signal
    OUT = np.zeros(length).astype(np.complex).ravel()

    sig_data = {}
    sig_data['IN'] = IN
    sig_data['OUT'] = OUT

    app_data['sig_data'] = sig_data
    app_data['length'] = length

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

