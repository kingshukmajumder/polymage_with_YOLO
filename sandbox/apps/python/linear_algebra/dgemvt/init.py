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
    rows = 128
    A = np.ndarray((rows,rows))
    x = np.ndarray((rows))
    y = np.ndarray((rows))
    w = np.ndarray((rows))
    z = np.ndarray((rows))

    fn = 8

    for i in range(rows):
        y[i] = (i * i + 2 * i +1) % 256
        z[i] = (255 * i + 123) % 256
        x[i] = 0.0
        w[i] = 0.0
        for j in range(rows):
            A[i][j] = (i * j + j + i + 1) % 256

    # convert to float image
    IN_Y = (np.array(y)).astype(np.float64).ravel()
    IN_Z = (np.array(z)).astype(np.float64).ravel()
    IN_A = (np.array(A)).astype(np.float64).ravel()

    # final output image
    OUT_X = (np.array(x)).astype(np.float64).ravel()
    OUT_W = (np.array(w)).astype(np.float64).ravel()


    img_data = {}
    img_data['IN_Y'] = IN_Y
    img_data['IN_Z'] = IN_Z
    img_data['OUT_X'] = OUT_X
    img_data['OUT_W'] = OUT_W
    img_data['IN_A'] = IN_A

    app_data['img_data'] = img_data
    app_data['rows'] = rows

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
    if(app_data['matrix']):
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

