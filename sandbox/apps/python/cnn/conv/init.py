import sys
import os.path
from PIL import Image
import numpy as np
from arg_parser import parse_args

from printer import print_header, print_usage, print_line

def init_images(app_data):
    print("[init.py] : initializing images...")

    app_args = app_data['app_args']

    # input matrix: 
    N = 1
    Oc = 12
    Ic = 3 
    Y = 32
    X = 32
    Kh = 3
    Kw = 3
    weights = np.full((Oc, Ic, Kh, Kw), 1)
    input_mat = np.full((N, Ic, Y, X), 1)

    # convert to float image
    IN = np.array(weights)
    IN1 = np.array(input_mat)
    IN = IN.astype(np.float32).ravel()
    IN1 = IN1.astype(np.float32).ravel()

    # final output image
    OUT = np.zeros((N, Oc, Y, X), np.float32).ravel()

    img_data = {}
    img_data['IN'] = IN
    img_data['IN1'] = IN1
    img_data['OUT'] = OUT

    app_data['img_data'] = img_data
    app_data['N'] = N
    app_data['Oc'] = Oc
    app_data['Ic'] = Ic
    app_data['Y'] = Y
    app_data['X'] = X
    app_data['Kh'] = Kh
    app_data['Kw'] = Kw

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

    return

def init_all(app_data):
    pipe_data = {}
    app_data['pipe_data'] = pipe_data

    get_input(app_data)

    init_images(app_data)

    return

