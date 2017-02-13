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
    length1 = 4
    length2 = 5
    sig1 = np.array([1, 2, 3, 4])
    sig2 = np.array([0, 1, 0.5, 0.25, 0.75])

    # convert to float arrays
    IN = np.array(sig1)
    IN1 = np.array(sig2)
    IN = IN.astype(np.float64).ravel()
    IN1 = IN1.astype(np.float64).ravel()

    # final output correlation value
    OUT = np.zeros(length1 + length2 - 1).astype(np.float64).ravel()

    sig_data = {}
    sig_data['IN'] = IN
    sig_data['IN1'] = IN1
    sig_data['OUT'] = OUT

    app_data['sig_data'] = sig_data
    app_data['length1'] = length1
    app_data['length2'] = length2

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

