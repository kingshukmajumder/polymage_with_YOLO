from __init__ import *

import sys
import subprocess
import numpy as np
from fractions import Fraction

sys.path.insert(0, ROOT)

from compiler import *
from constructs import *

def sift(app_data):

    R = Parameter(Int, "R")
    C = Parameter(Int, "C")
    x = Variable(Int, "x")
    y = Variable(Int, "y")

    app_data['R'] = R
    app_data['C'] = C
    

    # OCT Images
    img = Image(Float, "img", [R, C])

    nOCT = pipe_data['nOCT']
    nGLayers = pipe_data['nGLayers']
    nLayers  = pipe_data['nLayers']
    nDoGLayers = pipe_data['nDoGLayers']
    gCoeff = pipe_data['gCoeff']

    # Gaussian pyramid construction

    ######################################################################################################################################

    def pyr_down(src, l, name):
        dec_factor = 1 << l
        org_factor = 1 << (l-1)
        dec_rowr = Interval(Int, l, (R/dec_factor)-2)
        dec_colr = Interval(Int, l, (C/dec_factor)-2)
        colr = Interval(Int, l-1, (C/org_factor)-2)

        downx = Function(([x, y], [dec_rowr, colr]),
                         Float, "Dx_" + str(l) + "_" + name)
        downx.defn = [ (1 * f(2*x-2, y) + \
                        4 * f(2*x-1, y) + \
                        6 * f(2*x  , y) + \
                        4 * f(2*x+1, y) + \
                        1 * f(2*x+2, y)) * 0.0625 ]

        downy = Function(([x, y], [dec_rowr, dec_colr]),
                         Float, "Dy_" + str(l) + "_" + name)
        downy.defn = [ (1 * downx(x, 2*y-2) + \
                        4 * downx(x, 2*y-1) + \
                        6 * downx(x, 2*y  ) + \
                        4 * downx(x, 2*y+1) + \
                        1 * downx(x, 2*y+2)) * 0.0625 ]

        return downy

    OCT_img = {}
    OCT_img[0] = img
    for l in range(1, nOCT):
        OCT_img[l] = pyr_down(OCT_img[l-1], l, "img")

    ######################################################################################################################################

    def gauss(fd, m, l, Layers, coeff, name):


        

    Gauss_img = {}
    for m in range(0, nOCT):
        for l in range(0, nGlayers):
            Gauss_img1[m*nGlayers)+l+1] = gauss(OCT_img[(m*nGlayers)+l], m, l, nGlayers, "img")

    ######################################################################################################################################

    def dog(src1, src2, m, Layers, l, name):
        dec_factor = 1 << m
        dec_rowr = Interval(Int, m, (R/dec_factor)-2)
        dec_colr = Interval(Int, m, (C/dec_factor)-2)

        dogsub = Function(([x,y], [dec_rowr,dec_colr]), 
                            Float, "Dog_" + str(m*Layers +l) + "_" + name)
        dogsub.defn = [src2(x,y) - src1(x,y)]

        return dogsub 

    Dog_img = {}
    for m in range(0, nOCT):
        row_start = m*nGlayers
        for l in range(0,nDoGLayers):
            Dog_img[i*nDoGLayers+j] = dog(Gauss_img[row_start+j], Gauss_img[row_start+j+1], m, Layers, l, "img")

    ######################################################################################################################################

    def grad_ort(src, m, Layers, l, name):
        dec_factor = 1 << m
        dec_rowr = Interval(Int, m, (R/dec_factor)-2)
        dec_colr = Interval(Int, m, (C/dec_factor)-2)

        # Defintion of dr
        dr = Function(([x,y], [dec_rowr,dec_colr],),
                        Float, "dr_" + str(m*Layers +l) + "_" + name)
        dr.defn = [src(x+1,y) - src(x-1,y)]

        kpt = Struct("Kpt")
        kpt.defn = [["row", Int] , "col", "level", "grad", "ort"]

        # Defintion of dc
        dc = Function(([x,y], dec_rowr,dec_colr]),
                        Float, "dc_" + str(m*Layers +l) + "_" + name)
        dc.defn = [src(x,y+1) - src(x,y-1)]

        # Defintion of Gradient Data 
        grad_data = Function(([x,y], dec_rowr,dec_colr]),
                        Float, "grad_" + str(m*Layers +l) + "_" + name)
        grad_data.defn = [sqrtf((dr(x,y)*dr(x,y)) + (dc(x,y) * dc(x,y)))]

        # Defintion of Gradient Data 
        ort_data = Function(([x,y], dec_rowr,dec_colr]),
                        Float, "ort_" + str(m*layers +l) + "_" + name)
        ort_data.defn = []

        return grad_data, ort_data

     Grad_img = {}
     Ort_img = {}
     for m in range(0, nOCT):
        for l in range(1, nLayers):
            layer_index = i * nGlayers + j
            Grad_img[layer_index], Ort_img[layer_index] = grad_ort(Gauss_img[layer_index], m, l, "img")

    ######################################################################################################################################

    def kpt_det(low, current, high):

        return 0


    for m in range(0, nOCT): 
        for l in range(1, nDoGLayers): 
            layer_index = i * nDoGlayers + j
                dummy = kpt_det()

