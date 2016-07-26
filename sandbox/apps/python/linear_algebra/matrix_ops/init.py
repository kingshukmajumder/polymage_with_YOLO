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
    rows, cols = 256,256
    mat1 = np.full((rows,cols),7)
    mat2 = np.full((rows,cols),7)

    # convert to float image
    IN = np.array(mat1)
    IN1 = np.array(mat2)
    IN = IN.astype(np.float32).ravel()
    IN1 = IN.astype(np.float32).ravel()

    # final output image
    OUT = np.zeros((rows, cols), np.float32).ravel()

    img_data = {}
    img_data['IN'] = IN
    img_data['IN1'] = IN1
    img_data['OUT'] = OUT

    app_data['img_data'] = img_data
    app_data['rows'] = rows
    app_data['cols'] = cols

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

    return

def init_all(app_data):
    pipe_data = {}
    app_data['pipe_data'] = pipe_data

    get_input(app_data)

    init_images(app_data)

    return

