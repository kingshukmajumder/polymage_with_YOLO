import sys
import ctypes
from cv2 import *
import numpy as np
class c_demo_params(ctypes.Structure):
        _fields_ = [
               ('cfgfile',      ctypes.c_char_p                 ), 
               ('weightfile',   ctypes.c_char_p                 ), 
               ('thresh',       ctypes.c_float                  ),
               ('cam_index',    ctypes.c_int                    ),
               ('filename',     ctypes.c_char_p                 ),
               ('names',        ctypes.POINTER(ctypes.c_char_p) ),
               ('classes',      ctypes.c_int                    ),
               ('delay',        ctypes.c_int                    ),
               ('prefix',       ctypes.c_char_p                 ),
               ('avg_frames',   ctypes.c_int                    ),
               ('hier',         ctypes.c_float                  ),
               ('w',            ctypes.c_int                    ),
               ('h',            ctypes.c_int                    ),
               ('frames',       ctypes.c_int                    ),
               ('fullscreen',   ctypes.c_int                    )]    

def get_params(lib):
    LP_c_char = ctypes.POINTER(ctypes.c_char)
    LP_LP_c_char = ctypes.POINTER(LP_c_char)
    
    
    lib.run_detector2.argtypes = (ctypes.c_int, # argc
                            LP_LP_c_char) # argv
    lib.run_detector2.restype  = c_demo_params
    lib.load_network_p.argtypes = (ctypes.c_char_p,ctypes.c_char_p,ctypes.c_int)
    lib.load_network_p.restype   = ctypes.c_void_p
    def get_c_args(inp_argv):
        argc = len(inp_argv)
        argv = (LP_c_char * (argc + 1))()
        for i, arg in enumerate(inp_argv):
            enc_arg = arg.encode('utf-8')
            argv[i] = ctypes.create_string_buffer(enc_arg)
        return argc,argv
    inputs = ['darknet.py', 'paramsDetector', 'demo', 'cfg/coco.data', 'cfg/yolo.cfg', 'yolo.weights', 'videoplayback.mp4']
    argc,argv = get_c_args(inputs)
    params = lib.run_detector2(argc, argv)
   
    #import pdb;pdb.set_trace()
    params.net = lib.load_network_p(params.cfgfile,params.weightfile,0)
    return params

def run_detector(lib_func,params,res,frame):
    imout = res.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
    img = frame.ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte))
    imh = frame.shape[0]
    imw = frame.shape[1]
    imc = frame.shape[2]
    imstep = frame.strides[0]
    lib_func.argtypes = (
           ctypes.c_void_p,                     # net 
           ctypes.c_float ,                     # thresh    
           ctypes.POINTER(ctypes.c_float),                        # imout
           ctypes.POINTER(ctypes.c_ubyte),                         # img
           ctypes.c_int,                            # imh
           ctypes.c_int,                            # imw
           ctypes.c_int,                            # imc
           ctypes.c_int,                            # imstep
           ctypes.POINTER(ctypes.c_char_p),     # names     
           ctypes.c_int,                        # classes   
           ctypes.c_int,                        # delay     
           ctypes.c_char_p,                     # prefix    
           ctypes.c_int,                        # avg_frames
           ctypes.c_float,                      # hier      
           ctypes.c_int,                        # w         
           ctypes.c_int,                        # h         
           ctypes.c_int,                        # frames    
           ctypes.c_int)                        # fullscreen
 
    args = [params.net,
        params.thresh,
        imout,
        img,
        imh,
        imw,
        imc,
        imstep,
        params.names,
        params.classes,
        params.delay,
        params.prefix,
        params.avg_frames,
        params.hier,
        params.w,
        params.h,
        params.frames,
        params.fullscreen]
    lib_func(*args)

def run_demo(): 
    dll_filename = './darknet_naive.so'
    lib = ctypes.CDLL(dll_filename)
    
    params = get_params(lib)
    videofile = params.filename
    vid = VideoCapture(sys.argv[-1])
    frame = vid.read()[1]
    res = np.empty(frame.shape, np.float32)
    
    img = frame.ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte))
       
    while(1):
        frame = vid.read()[1]
        run_detector(lib.demo3,params,res,frame)
        imshow ('video',res)
        waitKey(1)
        
    imshow ('video',res)
    waitKey(0)
    destroyAllWindows()
if __name__ == '__main__':
    run_demo()
