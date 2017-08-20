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
    Y1 = 224
    X1 = 224

    K1 = 64
    C1 = 3
    Fh1 = 3
    Fw1 = 3
    weights1 = np.full((Fw1, Fh1, C1, K1), 1)
    input_mat = np.full((X1, Y1, C1), 1)
    
    K2 = 64
    C2 = 64
    Fh2 = 3
    Fw2 = 3
    weights2 = np.full((Fw2, Fh2, C2, K2), 1)
    
    K3 = 128
    C3 = 64
    Fh3 = 3
    Fw3 = 3
    weights3 = np.full((Fw3, Fh3, C3, K3), 1)

    K4 = 128
    C4 = 128
    Fh4 = 3
    Fw4 = 3
    weights4 = np.full((Fw4, Fh4, C4, K4), 1)

    # K5 = 256
    # C5 = 128
    # Fh5 = 3
    # Fw5 = 3
    # weights5 = np.full((Fw5, Fh5, C5, K5), 1)

    # K6 = 256
    # C6 = 256
    # Fh6 = 3
    # Fw6 = 3
    # weights6 = np.full((Fw6, Fh6, C6, K6), 1)

    # K7 = 256
    # C7 = 256
    # Fh7 = 3
    # Fw7 = 3
    # weights7 = np.full((Fw7, Fh7, C7, K7), 1)

    # K8 = 512
    # C8 = 256
    # Fh8 = 3
    # Fw8 = 3
    # weights8 = np.full((Fw8, Fh8, C8, K8), 1)
    
    # K9 = 512
    # C9 = 512
    # Fh9 = 3
    # Fw9 = 3
    # weights9 = np.full((Fw9, Fh9, C9, K9), 1)
    
    # K10 = 512
    # C10 = 512
    # Fh10 = 3
    # Fw10 = 3
    # weights10 = np.full((Fw10, Fh10, C10, K10), 1)
    
    # K11 = 512
    # C11 = 512
    # Fh11 = 3
    # Fw11 = 3
    # weights11 = np.full((Fw11, Fh11, C11, K11), 1)
    
    # K12 = 512
    # C12 = 512
    # Fh12 = 3
    # Fw12 = 3
    # weights12 = np.full((Fw12, Fh12, C12, K12), 1)
    
    # K13 = 512
    # C13 = 512
    # Fh13 = 3
    # Fw13 = 3
    # weights13 = np.full((Fw13, Fh13, C13, K13), 1)
    
    Fhm1 = 2
    Fwm1 = 2
    Fhm2 = 2
    Fwm2 = 2
    # Fhm3 = 2
    # Fwm3 = 2
    # Fhm4 = 2
    # Fwm4 = 2
    # Fhm5 = 2
    # Fwm5 = 2
    # convert to float image
    IN0 = np.array(input_mat)
    IN0 = IN0.astype(np.float64).ravel()
    
    IN1 = np.array(weights1)
    IN2 = np.array(weights2)
    IN3 = np.array(weights3)
    IN4 = np.array(weights4)
    # IN5 = np.array(weights5)
    # IN6 = np.array(weights6)
    # IN7 = np.array(weights7)
    # IN8 = np.array(weights8)
    # IN9 = np.array(weights9)
    # IN10 = np.array(weights10)
    # IN11 = np.array(weights11)
    # IN12 = np.array(weights12)
    # IN13 = np.array(weights13)
    
    IN1 = IN1.astype(np.float64).ravel()
    IN2 = IN2.astype(np.float64).ravel()
    IN3 = IN3.astype(np.float64).ravel()
    IN4 = IN4.astype(np.float64).ravel()
    # IN5 = IN5.astype(np.float64).ravel()
    # IN6 = IN6.astype(np.float64).ravel()
    # IN7 = IN7.astype(np.float64).ravel()
    # IN8 = IN8.astype(np.float64).ravel()
    # IN9 = IN9.astype(np.float64).ravel()
    # IN10 = IN10.astype(np.float64).ravel()
    # IN11 = IN11.astype(np.float64).ravel()
    # IN12 = IN12.astype(np.float64).ravel()
    # IN13 = IN13.astype(np.float64).ravel()
    

    # final output image
    # Xo = (((((X1 - Fw1) + 1) - Fw1) // 2) + 1)
    # Yo = (((((Y1 - Fh1) + 1) - Fh1) // 2) + 1)
    OUT = np.zeros((56, 56, 128), np.float64).ravel()

    app_data['X1'] = X1
    app_data['Y1'] = Y1
    
    app_data['K1'] = K1
    app_data['K2'] = K2
    app_data['K3'] = K3
    app_data['K4'] = K4
    # app_data['K5'] = K5
    # app_data['K6'] = K6
    # app_data['K7'] = K7
    # app_data['K8'] = K8
    # app_data['K9'] = K9
    # app_data['K10'] = K10
    # app_data['K11'] = K11
    # app_data['K12'] = K12
    # app_data['K13'] = K13
  
    app_data['C1'] = C1
    
    app_data['Fh1'] = Fh1
    app_data['Fh2'] = Fh2
    app_data['Fh3'] = Fh3
    app_data['Fh4'] = Fh4
    # app_data['Fh5'] = Fh5
    # app_data['Fh6'] = Fh6
    # app_data['Fh7'] = Fh7
    # app_data['Fh8'] = Fh8
    # app_data['Fh9'] = Fh9
    # app_data['Fh10'] = Fh10
    # app_data['Fh11'] = Fh11
    # app_data['Fh12'] = Fh12
    # app_data['Fh13'] = Fh13
   
    app_data['Fw1'] = Fw1
    app_data['Fw2'] = Fw2
    app_data['Fw3'] = Fw3
    app_data['Fw4'] = Fw4
    # app_data['Fw5'] = Fw5
    # app_data['Fw6'] = Fw6
    # app_data['Fw7'] = Fw7
    # app_data['Fw8'] = Fw8
    # app_data['Fw9'] = Fw9
    # app_data['Fw10'] = Fw10
    # app_data['Fw11'] = Fw11
    # app_data['Fw12'] = Fw12
    # app_data['Fw13'] = Fw13

    app_data['Fhm1'] = Fhm1
    app_data['Fhm2'] = Fhm2
    # app_data['Fhm3'] = Fhm3
    # app_data['Fhm4'] = Fhm4
    # app_data['Fhm5'] = Fhm5
   
    app_data['Fwm1'] = Fwm1
    app_data['Fwm2'] = Fwm2
    # app_data['Fwm3'] = Fwm3
    # app_data['Fwm4'] = Fwm4
    # app_data['Fwm5'] = Fwm5


   
    
    img_data = {}
    img_data['IN0'] = IN0
    img_data['IN1'] = IN1
    img_data['IN2'] = IN2
    img_data['IN3'] = IN3
    img_data['IN4'] = IN4
    # img_data['IN5'] = IN5
    # img_data['IN6'] = IN6
    # img_data['IN7'] = IN7
    # img_data['IN8'] = IN8
    # img_data['IN9'] = IN9
    # img_data['IN10'] = IN10
    # img_data['IN11'] = IN11
    # img_data['IN12'] = IN12
    # img_data['IN13'] = IN13
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

