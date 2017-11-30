import ctypes
import numpy as np
from cv2 import *
import sys
from structs import *
from darknet_helper import get_params, run_detector
sys.path.insert(0, "../")
import _ctypes
thresh = 0.001
weight = 3
params = None
lib_naive=None
lib_opt=None
lib_orig=None
def darknet_init():
    global params
    global lib_naive
    global lib_opt
    global lib_orig
    dll_filename = './darknet/darknet_naive.so'
    lib = ctypes.CDLL(dll_filename)
    params = get_params(lib)
    lib_naive = lib

   # dll_filename = './darknet/darknet.so'
   # lib_opt = ctypes.CDLL(dll_filename)
    lib_opt = lib_naive
    lib_orig = lib_naive

def darknet_naive(frame, lib_func):
    global lib_naive
    res = np.empty(frame.shape, np.float32)
    run_detector(lib_naive.pipeline_naive,params, res,frame)
    return res

def darknet_opt(frame, lib_func):
    global lib_opt
    res = np.empty(frame.shape, np.float32)
    run_detector(lib_opt.pipeline_opt,params, res,frame)
    return res

def darknet_orig(frame, lib_func):
    global lib_orig
    res = np.empty(frame.shape, np.float32)
    run_detector(lib_orig.pipeline_orig,params, res,frame)
    return res



def add_darknet_app(app_id):
    darknet_init()
    # 1. modes
    modes = [ModeType.CV2, ModeType.P_NAIVE, ModeType.P_OPT]
    # 2. modes that need shared library
    lib_modes = []

    # 3. set python functions from frame_process.py
    app_func_map = {}
    app_func_map[ModeType.CV2] = darknet_orig
    app_func_map[ModeType.P_NAIVE] = darknet_naive
    app_func_map[ModeType.P_OPT] = darknet_opt
    app_func_map[ModeType.PIL] = darknet_naive
    app_func_map[ModeType.NUMBA] = darknet_naive

    # 4. create an App object
    app_dir = os.path.dirname(os.path.realpath(__file__))
    app = App(app_id, app_dir, modes, lib_modes, app_func_map)

    return app
