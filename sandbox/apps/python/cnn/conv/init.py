import sys
import os.path
from PIL import Image
import numpy as np
from arg_parser import parse_args

from printer import print_header, print_usage, print_line

def init_images(app_data):
    print("[init.py] : initializing images...")

    app_args = app_data['app_args']

    # input image: 
    img_path = app_args.img_file
    img = Image.open(img_path)
    input_mat = np.array(img)
    rows, cols, c = input_mat.shape

    K = 64
    C = c
    Y = cols
    X = rows
    Fh = 3
    Fw = 3
    N = 16
    weights = np.full((Fw, Fh, C, K), 1)
    bias = np.full((K), 1)

    # convert to float image
    IN = np.array(weights)
    IN1 = np.array(input_mat)
    IN2 = np.array(bias)
    IN = IN.astype(np.float64).ravel()
    IN1 = IN1.astype(np.float64).ravel()
    IN2 = IN2.astype(np.float64).ravel()

    # final output image
    OUT = np.zeros((X-Fw, Y-Fh, K), np.float64).ravel()

    img_data = {}
    img_data['IN'] = IN
    img_data['IN1'] = IN1
    img_data['OUT'] = OUT

    app_data['img_data'] = img_data
    app_data['K'] = K
    app_data['C'] = C
    app_data['Y'] = Y
    app_data['X'] = X
    app_data['Fh'] = Fh
    app_data['Fw'] = Fw
    app_data['rows'] = rows
    app_data['cols'] = cols
    app_data['IN2'] = IN2

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
    app_data['blas'] = app_args.blas
    app_data['pluto'] = bool(app_args.pluto)
    if(app_data['pluto']):
        # By default we add the tile size and 32
        if(app_args.tiles):
            app_data['tiles'] = app_args.tiles
        else:
            app_data['tiles'] = "32,32,32"
    return

def init_all(app_data):
    pipe_data = {}
    app_data['pipe_data'] = pipe_data

    get_input(app_data)

    init_images(app_data)

    return

