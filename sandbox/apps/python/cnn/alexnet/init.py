import sys
import os.path
from PIL import Image
import numpy as np
from arg_parser import parse_args

from printer import print_header, print_usage, print_line

def init_images(app_data):
    print("[init.py] : initializing images...")

    app_args = app_data['app_args']

    # img_path = app_args.img_file
    # img = Image.open(img_path)
    # input_mat = np.array(img)
    # rows, cols, c = input_mat.shape

    # input matrix: 
    Y1 = 227
    X1 = 227

    K1 = 96
    C1 = 3
    Fh1 = 11
    Fw1 = 11
    Fhm1 = 3
    Fwm1 = 3
    weights1 = np.full((Fw1, Fh1, C1, K1), 1)
    input_mat = np.full((X1, Y1, C1), 1)
    
    K2 = 256
    C2 = 96
    Fh2 = 5
    Fw2 = 5
    Fhm2 = 3
    Fwm2 = 3
    weights2 = np.full((Fw2, Fh2, C2, K2), 1)
    
    K3 = 384
    C3 = 256
    Fh3 = 3
    Fw3 = 3
    weights3 = np.full((Fw3, Fh3, C3, K3), 1)

    K4 = 384
    C4 = 384
    Fh4 = 3
    Fw4 = 3
    weights4 = np.full((Fw4, Fh4, C4, K4), 1)

    K5 = 256
    C5 = 384
    Fh5 = 3
    Fw5 = 3
    Fhm5 = 3
    Fwm5 = 3
    weights5 = np.full((Fw5, Fh5, C5, K5), 1)

    # convert to float image
    IN0 = np.array(input_mat)
    IN0 = IN0.astype(np.float64).ravel()
    
    IN1 = np.array(weights1)
    IN2 = np.array(weights2)
    IN3 = np.array(weights3)
    IN4 = np.array(weights4)
    IN5 = np.array(weights5)
    
    IN1 = IN1.astype(np.float64).ravel()
    IN2 = IN2.astype(np.float64).ravel()
    IN3 = IN3.astype(np.float64).ravel()
    IN4 = IN4.astype(np.float64).ravel()
    IN5 = IN5.astype(np.float64).ravel()
    

    # final output image


    app_data['X1'] = X1
    app_data['Y1'] = Y1
    
    app_data['K1'] = K1
    app_data['K2'] = K2
    app_data['K3'] = K3
    app_data['K4'] = K4
    app_data['K5'] = K5
  
    app_data['C1'] = C1
    
    app_data['Fh1'] = Fh1
    app_data['Fh2'] = Fh2
    app_data['Fh3'] = Fh3
    app_data['Fh4'] = Fh4
    app_data['Fh5'] = Fh5
   
    app_data['Fw1'] = Fw1
    app_data['Fw2'] = Fw2
    app_data['Fw3'] = Fw3
    app_data['Fw4'] = Fw4
    app_data['Fw5'] = Fw5

    app_data['Fhm1'] = Fhm1
    app_data['Fhm2'] = Fhm2
    app_data['Fhm5'] = Fhm5
   
    app_data['Fwm1'] = Fwm1
    app_data['Fwm2'] = Fwm2
    app_data['Fwm5'] = Fwm5


    # Xo = (((((X1 - Fw1) + 1) - Fw1) // 2) + 1)
    # Yo = (((((Y1 - Fh1) + 1) - Fh1) // 2) + 1)
    OUT = np.zeros((7, 7, 256), np.float64).ravel()
    
    img_data = {}
    img_data['IN0'] = IN0
    img_data['IN1'] = IN1
    img_data['IN2'] = IN2
    img_data['IN3'] = IN3
    img_data['IN4'] = IN4
    img_data['IN5'] = IN5
    img_data['OUT'] = OUT

    app_data['img_data'] = img_data
    
    
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

