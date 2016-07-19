import ctypes
import numpy as np
from cv2 import *
import sys
from structs import *
from PIL import Image, ImageFilter
from numba_driver import unsharp_numba_driver
from numba import *
import theano.tensor as T
from theano.tensor.nnet import conv2d
import theano

sys.path.insert(0, "../")

NUMBA_OPT = 10
NUMBA_LOOP_VECTORIZE = 1
NUMBA_ENABLE_AVX = 1

# unsharp mask parameters
thresh = 0.001
weight = 3

# PIL version
@jit("float32[:,:,:](uint8[:,:,:],none)",cache = True, forceobj=True, nogil = True)
def unsharp_pil(frame, lib_func):
    im = Image.fromarray(frame)
    kernelx = (0,0,0,0,0,0,0,0,0,0,1,4,6,4,1,0,0,0,0,0,0,0,0,0,0)
    kernely = (0,0,1,0,0,0,0,4,0,0,0,0,6,0,0,0,0,4,0,0,0,0,1,0,0)
    blurx = im.filter(ImageFilter.Kernel((5, 5), kernelx, scale = None, offset = 0))
    blury = blurx.filter(ImageFilter.Kernel((5, 5), kernely, scale = None, offset = 0))
    sharpen = Image.blend(im, blury, -weight)
    res = np.array(sharpen)
    return res

# OpenCV version
@jit("float32[:,:,:](uint8[:,:,:], none)", cache = True, forceobj=True, nogil = True)
def unsharp_cv(frame, lib_func):
    frame_f = np.float32(frame) / 255.0
    res = frame_f
    kernelx = np.array([1, 4, 6, 4, 1], np.float32) / 16
    kernely = np.array([[1], [4], [6], [4], [1]], np.float32) / 16
    blury = sepFilter2D(frame_f, -1, kernelx, kernely)
    sharpen = addWeighted(frame_f, (1 + weight), blury, (-weight), 0)
    th, choose = threshold(absdiff(frame_f, blury), thresh, 1, THRESH_BINARY)
    choose = choose.astype(bool)
    np.copyto(res, sharpen, 'same_kind', choose)
    return res

def unsharp_theano(frame,lib_func):
    frame = np.float32(frame) / 255.0
    kernelx = np.asarray([[[[1,4,6,4,1]]]], dtype = 'float32') / 16
    kernely = np.asarray([[[[1],[4],[6],[4],[1]]]], dtype = 'float32') / 16
    frame = np.rollaxis(frame,2)

    R = np.asarray([[frame[0]]], dtype='float32')
    G = np.asarray([[frame[1]]], dtype='float32')
    B = np.asarray([[frame[2]]], dtype='float32')

    """Start of Theano definitions"""

    #Blur function definition
    t_img = T.ftensor4("t_img")
    t_kernel = T.ftensor4("t_kernel")
    blurred = conv2d(input = t_img, filters = t_kernel, border_mode = 'half')
    blur = theano.function([t_img,t_kernel],blurred)

    #Sharpen function definition
    t_blurred = T.ftensor4("t_blurred")
    t_weight = T.fscalar("t_weight")
    sharpen = t_img * (1 + t_weight) - t_blurred * (t_weight)
    sharp = theano.function([t_img,t_blurred,t_weight], sharpen)

    #Masking function definition
    t_sharpen = T.ftensor4("t_sharpen")
    t_thresh = T.scalar("t_thresh")
    t_mask = T.switch(T.lt(abs(t_img - t_blurred), t_thresh), t_img, t_sharpen)
    masking = theano.function([t_img,t_blurred,t_sharpen,t_thresh], t_mask, mode=theano.Mode(linker='vm'))

    """End of Theano definitions"""

    Rblur = blur(blur(R,kernelx),kernely)
    Gblur = blur(blur(G,kernelx),kernely)
    Bblur = blur(blur(B,kernelx),kernely)

    Rsharp = sharp(R, Rblur, weight)
    Gsharp = sharp(G, Gblur, weight)
    Bsharp = sharp(B, Bblur, weight)

    Rfinal = masking(R,Rblur,Rsharp,thresh)[0][0]
    Gfinal = masking(G,Gblur,Gsharp,thresh)[0][0]
    Bfinal = masking(B,Bblur,Bsharp,thresh)[0][0]

    res = np.asarray([Rfinal,Gfinal,Bfinal])
    res = np.rollaxis(np.rollaxis(res,2),2)
    return res

def unsharp_polymage(frame, lib_func):
    rows = frame.shape[0]
    cols = frame.shape[1]
    res = np.empty((rows-4, cols-4, 3), np.float32)
    lib_func(ctypes.c_int(cols - 4), \
             ctypes.c_int(rows - 4), \
             ctypes.c_float(thresh), \
             ctypes.c_float(weight), \
             ctypes.c_void_p(frame.ctypes.data), \
             ctypes.c_void_p(res.ctypes.data))
    return res

def add_unsharp_app(app_id):
    # 1. modes
    modes = [ModeType.CV2, ModeType.P_NAIVE, ModeType.P_OPT, \
        ModeType.PIL, ModeType.NUMBA, ModeType.THEANO]
    # 2. modes that need shared library
    lib_modes = [ModeType.P_NAIVE, ModeType.P_OPT]

    # 3. set python functions from frame_process.py
    app_func_map = {}
    app_func_map[ModeType.CV2] = unsharp_cv
    app_func_map[ModeType.P_NAIVE] = unsharp_polymage
    app_func_map[ModeType.P_OPT] = unsharp_polymage
    app_func_map[ModeType.PIL] = unsharp_pil
    app_func_map[ModeType.NUMBA] = unsharp_numba_driver
    app_func_map[ModeType.THEANO] = unsharp_theano

    # 4. create an App object
    app_dir = os.path.dirname(os.path.realpath(__file__))
    app = App(app_id, app_dir, modes, lib_modes, app_func_map)

    return app
