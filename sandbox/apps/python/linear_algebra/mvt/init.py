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
    rows1 = 128
    mat1 = np.full((rows1,rows1),7)
    vec1 = np.full((rows1),7)
    vec2 = np.full((rows1),7)

    # convert to float image
    IN = np.array(mat1)
    IN1 = np.array(vec1)
    IN2 = np.array(vec2)
    IN = IN.astype(np.float64).ravel()
    IN1 = IN1.astype(np.float64).ravel()
    IN2 = IN2.astype(np.float64).ravel()

    for i in range(rows1):
        vec1[i] = ((i + 3) % rows1) / rows1
        vec2[i] = ((i + 4) % rows1) / rows1
        for j in range(rows1):
           mat1[i][j] = (i * j % rows1) / rows1 

    # final output image
    OUT = np.zeros((rows1), np.float64).ravel()
    OUT1 = np.zeros((rows1), np.float64).ravel()

    img_data = {}
    img_data['IN'] = IN
    img_data['IN1'] = IN1
    img_data['IN2'] = IN2
    img_data['OUT'] = OUT
    img_data['OUT1'] = OUT1

    app_data['img_data'] = img_data
    app_data['rows1'] = rows1

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

