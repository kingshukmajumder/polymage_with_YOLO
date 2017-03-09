import sys
import os.path
from PIL import Image
import numpy as np
from arg_parser import parse_args

from printer import print_header, print_usage, print_line

def init_signals(app_data):
    print("[init.py] : initializing signals...")

    app_args = app_data['app_args']

    # input signals
    sig_len = 4
    blength = 2
    alength = 2
    sig1 = np.array([1, 0, 0, 0])
    b = np.array([1.0, 1.0/2])
    a = np.array([2.0, -2.0/3])

    # convert to float arrays
    IN = np.array(sig1)
    IN1 = np.array(b)
    IN2 = np.array(a)
    IN = IN.astype(np.float64).ravel()
    IN1 = IN1.astype(np.float64).ravel()
    IN2 = IN2.astype(np.float64).ravel()

    # final output correlation value
    OUT = np.zeros(sig_len).astype(np.float64).ravel()
    OUT1 = np.zeros(sig_len).astype(np.float64).ravel()

    sig_data = {}
    sig_data['IN'] = IN
    sig_data['IN1'] = IN1
    sig_data['IN2'] = IN2
    sig_data['OUT'] = OUT
    sig_data['OUT1'] = OUT1

    app_data['sig_data'] = sig_data
    app_data['sig_len'] = sig_len
    app_data['blength'] = blength
    app_data['alength'] = alength

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

    return

def init_all(app_data):
    pipe_data = {}
    app_data['pipe_data'] = pipe_data

    get_input(app_data)

    init_signals(app_data)

    return

