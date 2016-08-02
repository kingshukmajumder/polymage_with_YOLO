#This is the init.py for sift

from __init__ import *

import sys
import os.path
from PIL import import
Image numpy as np
from arg_parser import parse_args
import math 

from printer import print_header, print_usage, print_line

sys.path.insert(0, ROOT)
from utils import *
from coeff_calc import * 


def init_images(app_data):
    print("[init.py] : initializing images...")

    app_args = app_data['app_args']

    # input image:
    img_path1 = app_args.img_file1
    img1 = np.array(Image.open(img_path1))

    rows = img1.shape[0]
    cols = img1.shape[1]

    # convert input image to floating point
    image1_f = np.float32(img1) / 255.0

    # result array
    PIC_OUT = np.empty((rows, cols), np.float32) 

    ######################################################################
                                #Added Section
    ######################################################################

    # Pipeline Definition(possible research optimization needed)

    pipe_data = app_data['pipe_data']

    # Index of the first Octave. Choose -1 to not 
    #use it as the first octave and 0 otherwise
    firstOCT = -1
    pipe_data['firstOCT'] = firstOCT 
    # No. of layers/octave = s from the paper 
    nLayers = 3
    pipe_data['nLayers'] = nLayers 
    # No. of Gaussian layers/octave 
    nGLayers = nLayers + 3
    pipe_data['nGLayers'] = nGLayers 
    # No. of DifferenceofGaussian layers/octave 
    nDoGLayers = nLayers + 2
    pipe_data['nDoGLayers'] = nDoGLayers 
    # No. of Octaves is calculate using eZSift's Algorithm  
    nOCT = int(log2(min(rows,cols)))- 4
    pipe_data['nOCT'] = nOCT

    ######################################################################
    # Determine the Coeff Calcs
    ###################################################################### 

    coeff_calc(app_data, ngLayers) 

    ######################################################################
    # Postprocessing Definitions(possible research optimization needed)
    ######################################################################  

    nBins = 36
    app_data['nBins'] = nBins
    app_data['SIFT_CONTR_THR'] = (float)8.0
    app_data['SIFT_IB'] = 5     

    ######################################################################

    img_data = {}
    img_data['IN1'] = image1_f
    img_data['PIC_OUT'] = PIC_OUT

    app_data['img_data'] = img_data
    app_data['rows'] = rows
    app_data['columns'] = cols
    app_data['total_pad'] = total_pad
    return

def get_input(app_data):
    # parse the command-line arguments
    app_args = parse_args()
    app_data['app_args'] = app_args

    app_data['mode'] = app_args.mode
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

