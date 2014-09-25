import ctypes
import numpy as np
import time
import cv2
import sys

from common import clock, draw_str, StatValue
#import video

# load polymage shared libraries
libharris = ctypes.cdll.LoadLibrary("./harris.so")
libbilateral = ctypes.cdll.LoadLibrary("./bilateral.so")

harris = libharris.pipeline_harris
bilateral = libbilateral.pipeline_bilateral
bilateral_naive = libbilateral.pipeline_naive

fn = sys.argv[1]
cap = cv2.VideoCapture(fn)

frames = 0
#startTime = time.clock()
startTime = time.clock()
cv_mode = True
harris_mode = False
bilateral_mode = False
naive_mode = False

while(cap.isOpened()):
    ret, frame = cap.read()

    frameStart = clock()
    rows = frame.shape[0]
    cols = frame.shape[1]
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = np.float32(gray)
    if harris_mode:
        if cv_mode:
            res = cv2.cornerHarris(gray, 3, 3, 0.04)
        else:    
            res = np.zeros((rows, cols), np.float32) 
            harris(ctypes.c_int(cols-2), ctypes.c_int(rows-2), \
            ctypes.c_void_p(gray.ctypes.data), ctypes.c_void_p(res.ctypes.data))
        res = cv2.cvtColor(res, cv2.COLOR_GRAY2RGB)     
    elif bilateral_mode:
        gray = gray/255
        res = np.zeros((rows, cols), np.float32)
        if naive_mode:
            bilateral_naive(ctypes.c_int(cols), ctypes.c_int(rows), \
            ctypes.c_void_p(gray.ctypes.data), ctypes.c_void_p(res.ctypes.data))
        else:
            bilateral(ctypes.c_int(cols), ctypes.c_int(rows), \
            ctypes.c_void_p(gray.ctypes.data), ctypes.c_void_p(res.ctypes.data))
    else:
        res = frame

    frameEnd = clock()
    cv2.rectangle(res, (0, 0), (750, 150), (255, 255, 255), thickness=cv2.cv.CV_FILLED)
    draw_str(res, (40, 40), "frame interval :  %.1f ms" % (frameEnd*1000 - frameStart*1000))
    if cv_mode and harris_mode:
        draw_str(res, (40, 80), "Pipeline     :  " + str("OpenCV"))
    elif bilateral_mode or harris_mode:
        draw_str(res, (40, 80), "Pipeline     :  " + str("PolyMage"))
    if harris_mode:    
        draw_str(res, (40, 120), "Benchmark   :  " + str("Harris Corner"))
    cv2.imshow('threaded video', res)

    ch = 0xFF & cv2.waitKey(1)
    if ch == ord('q'):
        break
    if ch == ord(' '):
        cv_mode = not cv_mode
    if ch == ord('h'):
        harris_mode = not harris_mode
        bilateral_mode = False
    if ch == ord('b'):
        bilateral_mode = not bilateral_mode
        harris_mode = False
    frames += 1

cap.release()
cv2.destroyAllWindows()
