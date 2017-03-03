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
    u = np.ndarray((rows))
    v = np.ndarray((rows))
    w = np.ndarray((rows))
    z = np.ndarray((rows))
    
    r = np.ndarray((1))

    r[0] = 0.0

    for i in range(rows):
        u[i] = (i * i + 2 * i + 1) % 256
        v[i] = (255 * i + 123) % 256
        w[i] = (i * i - 21) % 256
        z[i] = 0.0

    # convert to float image
    IN_U = u
    IN_V = v
    IN_W = w
    IN_Z = z

    # final output image
    OUT_R = r 


    img_data = {}
    img_data['IN_U'] = IN_U
    img_data['IN_V'] = IN_V
    img_data['IN_W'] = IN_W
    img_data['IN_Z'] = IN_Z
    img_data['OUT_R'] = OUT_R

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

