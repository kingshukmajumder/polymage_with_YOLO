import sys
import os.path
from PIL import Image
import numpy as np
from arg_parser import parse_args

from printer import print_header, print_usage, print_line

def init_images(app_data):
    print("[init.py] : initializing images...")

    app_args = app_data['app_args']

    # input pluto: 
    rows1, cols1 = 128,128
    #rows2, cols2 = 128,128
    v1 = np.full((rows1,1),7)
    v2 = np.full((rows1,1),7)
    # v3 = np.full((rows1,1),7)

    # convert to float image
    IN = np.array(v1)
    IN1 = np.array(v2)
    # IN2 = np.array(mat3)
    # IN3 = np.array(v1)
    # IN4 = np.array(v2)
    # IN5 = np.array(v3)
    IN = IN.astype(np.float64).ravel()
    IN1 = IN1.astype(np.float64).ravel()
    # IN2 = IN2.astype(np.float64).ravel()
    # IN3 = IN3.astype(np.float64).ravel()
    # IN4 = IN4.astype(np.float64).ravel()
    # IN5 = IN5.astype(np.float64).ravel()

    # final output image
    OUT = np.zeros((1, 1), np.float64).ravel()
    # OUT1 = np.zeros((rows1, 1), np.float64).ravel()
    # OUT2 = np.zeros((rows1, 1), np.float64).ravel()
    
    img_data = {}
    img_data['IN'] = IN
    img_data['IN1'] = IN1
    # img_data['IN2'] = IN2
    # img_data['IN3'] = IN3
    # img_data['IN4'] = IN4
    # img_data['IN5'] = IN5
    img_data['OUT'] = OUT
    # img_data['OUT1'] = OUT1
    # img_data['OUT2'] = OUT2

    app_data['img_data'] = img_data
    app_data['rows1'] = rows1
    app_data['cols1'] = cols1
    # app_data['rows2'] = rows2
    #app_data['cols2'] = cols2

    return

def get_input(app_data):
    # parse the command-line arguments
    # arg_parser.py 
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
    # init.py file ---- Setting of app_data 
    get_input(app_data)

    # init.py file ---- Initializing the image 
    init_images(app_data)
    return

