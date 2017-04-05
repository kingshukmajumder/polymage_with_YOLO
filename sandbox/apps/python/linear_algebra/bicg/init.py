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
    cols = 128
    A = np.ndarray((rows, cols))
    s = np.ndarray((cols))
    q = np.ndarray((rows))
    p = np.ndarray((cols))
    r = np.ndarray((rows))

    for i in range(cols):
        p[i] = (i % cols) / cols
        s[i] = 0.0

    for i in range(rows):
        q[i] = 0.0
        r[i] = (i % rows) / rows
        for j in range(cols):
            A[i][j] = (i * (j + 1) % rows) / rows

    # convert to float image
    IN_P = p
    IN_R = r
    IN_A = (np.array(A)).astype(np.float64).ravel()

    # final output image
    OUT_S = s
    OUT_Q = q

    img_data = {}
    img_data['IN_P'] = IN_P
    img_data['IN_R'] = IN_R
    img_data['OUT_S'] = OUT_S
    img_data['OUT_Q'] = OUT_Q
    img_data['IN_A'] = IN_A

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
    app_data['blas'] = bool(app_args.blas)
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

