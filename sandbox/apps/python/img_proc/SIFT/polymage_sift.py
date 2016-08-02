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
    

    # Pulling in the initialized app 
    # and pipe data 

    img = Image(Float, "img", [R, C])

    # No. of Octaves
    nOCT = pipe_data['nOCT']

    # No. of Gaussian Layers / Octave
    nGLayers = pipe_data['nGLayers']

    # No. of total layers/Octave
    nLayers  = pipe_data['nLayers']

    # No. of Difference of Gaussian Layers / Octave
    # Note: Can be deleted as this can be directly 
    # calcualted from nLayers
    nDoGLayers = pipe_data['nDoGLayers']

    # Coefficient 2D List from the coeff_calc
    # function being called in init.py
    gCoeff = pipe_data['gCoeff']

    # SIFT Image Border Specification by the user
    SIFT_IB = app_data['SIFT_IB']

    # SIFT Max Interpretation Steps Specification by the user
    SIFT_IS = app_data['SIFT_IS']

    # SIFT Sub Pixel Threshold Specification by the user 
    SIFT_ST = app_data['SIFT_ST']

    # SIFT Contrast Threshold Specification by the user
    SIFT_CT = app_data['SIFT_CT']

    # SIFT Curvature Threshold Specification by the user 
    SIFT_CUT = app_data['SIFT_CUT']

    # SIFT Sigma value Specification by the user 
    SIFT_SIGMA = app_data['SIFT_SIGMA']

    # The number of SIFT intervals per octave value 
    # specification by the user
    SIFT_INTVLS = app_data['SIFT_INTVLS']

    # This is the radius in which we will Bin the 
    # orinetations 
    SIFT_O_RADIUS = app_data['SIFT_O_RADIUS']

    # SIFT Original Sigma Factor 
    SIFT_ORI_F = app_data['SIFT_ORI_F']

    # SIFT Keypoint Subpixel Threshold 
    SIFT_K_SP_THR = app_data['SIFT_K_SP_THR']

    # This is the height of the Image needed for computations 
    # within polymage code (Int of the no. of Rows)
    IMG_H = app_data['R']

    # This is the width of the Image needed for computations 
    # within the polymage code (Int of no. of Columns)
    IMG_W = app_data['H']

    # Gaussian pyramid construction STAGE 1: 
    # Standard pyramid downsampling based on the variable nOCT 
    # (number of octaves)
    #
    # This is currently a seperable kernel that has been copied
    # from Polymage's Pyramid Blending application 

    def pyr_down(src, l, name):
        dec_factor = 1 << l
        org_factor = 1 << (l-1)
        dec_rowr = Interval(Int, l, (R/dec_factor)-2)
        dec_colr = Interval(Int, l, (C/dec_factor)-2)
        colr = Interval(Int, l-1, (C/org_factor)-2)

        downx = Function(([x, y], [dec_rowr, colr]),
                         Float, "Dx_" + str(l) + "_" + name)
        downx.defn = [ (1 * src(2*x-2, y) + \
                        4 * src(2*x-1, y) + \
                        6 * src(2*x  , y) + \
                        4 * src(2*x+1, y) + \
                        1 * src(2*x+2, y)) * 0.0625 ]

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

    # Gaussian pyramid construction STAGE 2: 
    # Create Gaussian pyramids using the previous 
    # calculations of Octaves 

    def gauss(src, m, l, Layers, coeff, gS, name):
        dec_factor = 1 << m
        dec_rowr = Interval(Int, m, (R/dec_factor)-2)
        dec_colr = Interval(Int, m, (C/dec_factor)-2)



    Gauss_img = {}
    for m in range(0, nOCT):
        for l in range(0, nGlayers):
            #Precompute the size of the coefficient vector
            gS = len(gCoeff[l])
            # If we are at the very base of the pyramid
            if (m == 0) & (l == 0) :
                Gauss_img1[0] = gauss(OCT_img[0], m, l, nGlayers, gCoeff[l], gS, "img")
            # If we are at the very first image of a particular octave 
            #
            # NOTE: Personally think this is a redundant calcualtion but 
            # following eZSIFT's implmentation for now
            elif (i > 0) & (l == 0) :
                Gauss_img1[m*nGlayers] = pyr_down(Gauss_img[(m-1)*nGlayers], m, "img")
            # If we are at any other image within the octave 
            else :
                Gauss_img1[m*nGlayers)+l] = gauss(OCT_img[(m*nGlayers)+l-1], m, l, \
                                                gCoeff[l], nGlayers, gS, "img")

    # Difference of Gaussian pyramid construction STAGE:
    # Looks at the number of the Difference of Gaussian Layers (nDoGLayers) and 
    # subtracts layers from each other in a specific octave 

    def dog(src1, src2, m, layers, l, name):
        dec_factor = 1 << m
        dec_rowr = Interval(Int, m, (R/dec_factor)-2)
        dec_colr = Interval(Int, m, (C/dec_factor)-2)

        dogsub = Function(([x,y], [dec_rowr,dec_colr]), 
                            Float, "Dog_" + str(m*layers +l) + "_" + name)
        dogsub.defn = [src2(x,y) - src1(x,y)]

        return dogsub 

    Dog_img = {}
    for m in range(0, nOCT):
        row_start = m*nGlayers
        for l in range(0,nDoGLayers):
            Dog_img[m*nDoGLayers+l] = dog(Gauss_img[row_start+l], \
                            Gauss_img[row_start+l+1], m, Layers, l, "img")

    # Gradient and Orientation pyramid construction STAGE: 
    # Calculates the gradient and orientation for each and every point 
    # throughout the whole Gaussian pyramid 

    def grad_ort(src, m, layers, l, name):
        dec_factor = 1 << m
        dec_rowr = Interval(Int, m, (R/dec_factor)-2)
        dec_colr = Interval(Int, m, (C/dec_factor)-2)

        # Defintion of dr (Does this need to be a function?)
        dr = Function(([x,y], [dec_rowr,dec_colr],),
                        Float, "dr_" + str(m*layers +l) + "_" + name)
        dr.defn = [src(x+1,y) - src(x-1,y)]

        # Defintion of dc (Does this need to be a function?)
        dc = Function(([x,y], [dec_rowr,dec_colr]),
                        Float, "dc_" + str(m*layers +l) + "_" + name)
        dc.defn = [src(x,y+1) - src(x,y-1)]

        # Defintion of Gradient Data 
        grad_data = Function(([x,y], [dec_rowr,dec_colr]),
                        Float, "grad_" + str(m*layers +l) + "_" + name)
        grad_data.defn = [sqrtf((dr(x,y)*dr(x,y)) + (dc(x,y) * dc(x,y)))]

        # Defintion of Gradient Data 
        ort_data = Function(([x,y], [dec_rowr,dec_colr]),
                        Float, "ort_" + str(m*layers +l) + "_" + name)
        ort_data.defn = [ArcTan(dr(x,y),dc(x,y))]

        return grad_data, ort_data

     Grad_img = {}
     Ort_img = {}
     for m in range(0, nOCT):
        for l in range(1, nLayers):
            layer_index = m * nGlayers + l
            Grad_img[layer_index], Ort_img[layer_index] = grad_ort(Gauss_img[layer_index], m, l, "img")


    # Initializations and declrations needed to process the keypoint stages of the program 
    Keypoint = PolyStruct({'x': Float, 'y': Float, 'octave' : Int, 'layer': Int, 'rlayer': Float, \
                            'scale': Float, 'ci': Float, 'ri': Float, 'layer_scale': Float, \
                            'Ort': Float, 'grad': Float, 'tmp_r': Float, 'tmp_c': Float,  \
                            'tmp_layer': Float, 'x_ri': Int, 'x_ci': Int})
    k = Keypoint.Iterator("k")

    # Keypoint Detection STAGE:
    # Uses 3 inputs: low, high and current to emulate a 3D stencil which 
    # checks whether a particular point on the gaussian pyramid is an 
    # extrema/ maxima 
    #
    # Function also returns the specific domain for the keypoints of each 
    # layer of the Gaussian pyramid that can be used for further functions 
    def kpt_det(low, current, high, g_img, o_img, kpt_list, SIFT_IB, m, layers, name):
        # SIFT image border can be used that ignores a few pixels from the edge of the 
        # image
        dec_factor = 1 << m
        dec_rowr = Interval(Int, m+SIFT_IB, (R/dec_factor)-2-SIFT_IB)
        dec_colr = Interval(Int, m+SIFT_IB, (C/dec_factor)-2-SIFT_IB)

        # The weighting is still going the 1 as we do not want to change the values of the 
        # pixels 
        main_kernel = [[1, 1, 1],[1, 1, 1], [1, 1, 1]]
        stencil_lMx = Stencil(low, [x,y], main_kernel, Op.Max)
        stencil_cMx = Stencil(current, [x,y], main_kernel, Op.Max)
        stencil_hMx = Stencil(high, [x,y], main_kernel, Op.Max)
        stencil_lMn = Stencil(low, [x,y], main_kernel, Op.Min)
        stencil_cMn = Stencil(current, [x,y], main_kernel, Op.Min)
        stencil_hMn = Stencil(high, [x,y], main_kernel, Op.Min)
       
        current_point = current(x,y)
        cond1 = Condition((current_point, ">=" stencil_lMx) & (current_point, ">=" stencil_cMx) & \
                                (current_point, ">=" stencil_hMx))
        cond2 = Condition((current_point, "<=" stencil_lMn) & (current_point, "<=" stencil_cMn) & \
                                (current_point, "<=" stencil_hMn))
        main_cond = cond1 | cond2 

        # Keypoints selected based on the condition specified above. 
        # x_ci, x_ri, tmp_c, tmp_r are variables that are used for the keypoint 
        # refinement. The rest of the variables are actual attributes of the 
        # keypoint 
        kpt_dec_func = Function(([x,y],[dec_rowr, dec_colr]), Keypoint, \
                        "keypoint_detection"+ str(m*layers +l) + "_" + name)  
        kpt_dec_func.defn = [Select(cond, Keypoint(x=x, y=y, octave=m, layer=layer, rlayer =0, \
                                scale =0, ri =x, ci =y, layer_scale =0,  ort=o_img[x,y], \
                                grad=g_img[x,y], tmp_r=0, tmp_c=0, tmp_layer=0, \
                                dx=dx, dy=dy, ds=ds, xs=xs, \
                                xc=xc, xr=xr, dxx=dxx, dyy=dyy, dxy=dxy), \
                                NULL)] 

        return kpt_dec_func

    pre_kpt = {}
    
    for m in range(0, nOCT): 
        for l in range(1, nDoGLayers): 
            layer_index = m * nDoGlayers + l
            pre_kpt[layer_index] = kpt_det(Dog_img[layer_index-1],Dog_img[layer_index], \
                                            Dog_img[layer_index+1], Grad_img[layer_index], \
                                            Ort_img[layer_index],kpt_list, SIFT_IB, m, l, "img")

    # Keypoint refinement Stage 1:
    # Use the keypoints calculated in the previous stage and update 
    # values that are going to be used in the next function.
    # 
    # Doing a Breadth First approach here, in terms of the stress 
    # tests, which are multiple passes, depending on the specification 
    # by the user 
    #
    # Divided into two functions as of now due to the existence of 
    # breaks at the end of each of these functions 

    def kpt_refine1a(low, current, high, range_, m, l, check, name):

        x = k.x
        y = k.y 

        # First Derivative
        dx = (current(x,y+1) - current(x,y-1)) * 0.5
        dy = (current(x+1,y) - current(x-1,y)) * 0.5
        ds = (high(x,y) - low(x,y)) * 0.5

        # Second Derivative
        v2 = 2 * current(x,y)
        dxx = current(x,y+1) + current(x,y-1) - v2
        dyy = current(x+1,y) + current(x-1,y) - v2
        dss = high(x,y) + low(x,y) - v2
        dxy = (current(x+1,y+1) - current(x+1,y-1)) - \
                (current(x-1,y+1) + current(x-1,y-1)) * 0.25
        dxs = (high(x,y+1) - high(x,y-1) - low(x,y+1) + low(x-1,y)) \
                * 0.25 
        dys = (high(x+1,y) - high(x-1,y) - low(x+1,y) + low(x-1,y)) * \
                0.25

        # Matrix Construction 1 
        cond0 = Condition(x, '==', 0)
        cond1 = Condition(x, '==', 1)
        cond2 = Condition(x, '==', 2)

        dD = Matrix( ([x], [Interval(0, 2)]), Float, "vectorBuild_" + \
                            str(m*layers +l) + "_" + name)
        dD.defn = [Case(cond0, -dx), Case(cond1, -dy), Case(cond2, -ds)]

        # Matrix Construction 2
        cond0 = Condition((x, '==', 0) & (y, "==", 0))
        cond1 = Condition((x, '==', 1) & (y, "==", 0))
        cond2 = Condition((x, '==', 2) & (y, "==", 0)) 
        cond3 = Condition((x, '==', 0) & (y, "==", 1))
        cond4 = Condition((x, '==', 1) & (y, "==", 1))
        cond5 = Condition((x, '==', 2) & (y, "==", 1)) 
        cond6 = Condition((x, '==', 0) & (y, "==", 2))
        cond7 = Condition((x, '==', 1) & (y, "==", 2))
        cond8 = Condition((x, '==', 2) & (y, "==", 2)) 

        Intrvl = Interval(0,2)

        # I want to create the matrix: 
        # [dxx dxy dxs]
        # |dxy dyy dys|
        # [dxs dys dss]

        H = Matrix( ([x, y], [Intrvl, Intrvl]), Float, "matrixBuild" + \
                            str(m*layers +l) + "_" + name)
        H.defn = [Case(cond0, dxx), Case(cond1, dxy), Case(cond2, dxs), \
                    Case(cond3, dxy), Case(cond4, dyy), Case(cond5, dys), \
                    Case(cond6, dxs), Case(cond7, dys), Case(cond8, dss)]

        # Determinant of the Matrix H
        det = Matrix.det(H)

        # fabsf and numeric_limit need to be added to the inbuilt functions 
        # Please refer to a C++ reference for function defintions
        cond = Condition(fabsf(det), "<", Climits.Min)) 

        first_check = Function(([k], range_), Uint, \
                        "first_check"+ str(m*layers +l) + "_" + name) 
        first_check.defn = [Select(cond, check = 1, check = 0)]

        return first_check

    def kpt_refine1b(low, current, high, range_, m, l, check, name):

        # This is needed to find out the length and width of a particular
        # image at a particular point
        dec_factor = 1 << k.m

        x = k.x
        y = k.y 

        # First Derivative
        dx = (current(x,y+1) - current(x,y-1)) * 0.5
        dy = (current(x+1,y) - current(x-1,y)) * 0.5
        ds = (high(x,y) - low(x,y)) * 0.5

        # Second Derivative
        v2 = 2 * current(x,y)
        dxx = current(x,y+1) + current(x,y-1) - v2
        dyy = current(x+1,y) + current(x-1,y) - v2
        dss = high(x,y) + low(x,y) - v2
        dxy = (current(x+1,y+1) - current(x+1,y-1)) - \
                (current(x-1,y+1) + current(x-1,y-1)) * 0.25
        dxs = (high(x,y+1) - high(x,y-1) - low(x,y+1) + low(x-1,y)) \
                * 0.25 
        dys = (high(x+1,y) - high(x-1,y) - low(x+1,y) + low(x-1,y)) * \
                0.25

        # Matrix Construction 1 
        cond0 = Condition(x, '==', 0)
        cond1 = Condition(x, '==', 1)
        cond2 = Condition(x, '==', 2)

        dD = Matrix( ([x], [Interval(0, 2)]), Float, "vectorBuild_" + \
                            str(m*layers +l) + "_" + name)
        dD.defn = [Case(cond0, -dx), Case(cond1, -dy), Case(cond2, -ds)]

        # Matrix Construction 2
        cond0 = Condition((x, '==', 0) & (y, "==", 0))
        cond1 = Condition((x, '==', 1) & (y, "==", 0))
        cond2 = Condition((x, '==', 2) & (y, "==", 0)) 
        cond3 = Condition((x, '==', 0) & (y, "==", 1))
        cond4 = Condition((x, '==', 1) & (y, "==", 1))
        cond5 = Condition((x, '==', 2) & (y, "==", 1)) 
        cond6 = Condition((x, '==', 0) & (y, "==", 2))
        cond7 = Condition((x, '==', 1) & (y, "==", 2))
        cond8 = Condition((x, '==', 2) & (y, "==", 2)) 

        Intrvl = Interval(0,2)

        # I want to create the matrix: 
        # [dxx dxy dxs]
        # |dxy dyy dys|
        # [dxs dys dss]

        H = Matrix( ([x, y], [Intrvl, Intrvl]), Float, "matrixBuild" + \
                            str(m*layers +l) + "_" + name)
        H.defn = [Case(cond0, dxx), Case(cond1, dxy), Case(cond2, dxs), \
                    Case(cond3, dxy), Case(cond4, dyy), Case(cond5, dys), \
                    Case(cond6, dxs), Case(cond7, dys), Case(cond8, dss)]

        # Determinant of the Matrix H
        det = Matrix.det(H)

        # Scale_ADJOINT Function needs to be implemented 
        tmp = 1.0/det
        H_invert = Matrix.Scale_adjoint(tmp, H)
        x_Hat = H_invert * dD

        a = 0 
        b = 1 
        c = 2 
        x_s = x_Hat[c]
        x_r = x_Hat[b]
        x_c = x_Hat[a]

        tmp_r = k.x + xr
        tmp_c = k.y + xc
        tmp_layer = k.layer + xs

        xci_cond1 = Condition((xc, ">=", SIFT_K_SP_THR) & (k.x, "<", (IMG_W/dec_factor)-2))) 
        xci_cond2 =  Condition((xc, "<=", -SIFT_K_SP_THR) & (k.x, ">", 1))

        xri_cond1 = Condition((xr, ">=", SIFT_K_SP_THR) & (k.y, "<", (IMG_H/dec_factor)-2))) 
        xri_cond2 =  Condition((xr, "<=", -SIFT_K_SP_THR) & (k.y, ">", 1))

        x_ci = Select(xci_cond1, 1, 0) + Select(xci_cond2, -1, 0)
        x_ri = Select(xri_cond1, 1, 0) + Select(xri_cond2, -1, 0)

        main_cond = Condition((x_ci, "==", 0)& (x_ri. "==", 0) & (xs_i, "==", 0))

        new_r = k.x + x_ri
        new_c = k.y + x_ci

        kpt_ref_func = Function(([k], range_), Keypoint, \
                        "kpt_ref_func"+ str(m*layers +l) + "_" + name) 
        kpt_ref_func.defn = [Keypoint(x=new_r, y=new_c, octave=k.m, layer=k.layer, rlayer =0, \
                                scale =0, ri =k.ri, ci =k.ci, layer_scale =0, \
                                ort=k.ort, grad=k.grad, tmp_r=0, tmp_c=0, tmp_layer=0, \
                                dx=dx, dy=dy, ds=ds, xs=xs, \
                                xc=xc, xr=xr, dxx=dxx, dyy=dyy, dxy=dxy), \
                                NULL]

        second_check = Function(([k], range_), Uint, \
                        "second_check"+ str(m*layers +l) + "_" + name) 
        second_check.defn = [Select(main_cond, bool_kpt2(True), bool_kpt2(False))]

        return kpt_ref_func, second_check

    mid1_kpt = {}
    mid_check1 = {}
    mid_check2 = {}

    for m in range(0, nOCT): f
        for l in range(1, nDoGLayers): 
            layer_index = m * nDoGlayers + l
            # This for loop is defined by the user
            for k in range(0, SIFT_IS):
                flag = 0 
                if (k == 0) : 
                    mid_check1[layer_index] = kpt_refine1a(Dog_img[layer_index-1], \
                                                            Dog_img[layer_index], \
                                                            Dog_img[layer_index+1], \
                                                            kpt_dec_func.range_(), \
                                                            m, l, bool_kpt1, "kpt")
                    if (bool_kpt1 == False):
                        flag = 1
                    else : 
                        mid1_kpt[layer_index], mid_check2[layer_index] = kpt_refine1a(Dog_img[layer_index-1], \
                                                                                        Dog_img[layer_index], \
                                                                                        Dog_img[layer_index+1], \
                                                                                        kpt_dec_func.range_(), \
                                                                                        m, l, bool_kpt2, "kpt")
                        if (bool_kpt2 == False) :
                            flag = 1
                else : 
                    mid_check1[layer_index] = kpt_refine1a(Dog_img[layer_index-1], \
                                                            Dog_img[layer_index], \
                                                            Dog_img[layer_index+1], \
                                                            kpt_refine1b.range_(), \
                                                            m, l, bool_kpt1, "kpt")
                    if (bool_kpt1 == False):
                        flag = 1
                    else : 
                        mid1_kpt[layer_index], mid_check2[layer_index] = kpt_refine1a(Dog_img[layer_index-1], \
                                                                                        Dog_img[layer_index], \
                                                                                        Dog_img[layer_index+1], \
                                                                                        kpt_dec_func.range_(), \
                                                                                        m, l, bool_kpt2, "kpt")
                        if (bool_kpt2 == False)
                            flag = 1
                if flag == 1
                    break

    # Keypoint refinement Stage 2:
    # Use the updated keypoint values from the previous step to 
    # filter out the keypoints based on various thresholds
    # This is a single pass step 

    def kpt_refine2(low, current, high, range_, m, l, name):
        dec_factor = 1 << k.m

        # Mostly doesn't happen but a safety measure
        cond1 = Condition((fabsf(k.xc), ">=", 1.5) || \
                            (fabsf(k.xr), ">=", 1.5) || \
                            (fabsf(k.xs), ">=", 1.5))

        # If the row, column or layer are out of range, not a keypoint
        cond2 = Condition((k.tmp_layer, "<", 0) || \
                            (k.tmp_layer, ">", nGlayers-1) || \
                            (k.tmp_r, "<", 0) || \
                            (k.tmp_r, "<", (IMG_H/dec_factor)-1) || \
                            (k.tmp_c, "<", 0) || \
                            (k.tmp_c, "<", (IMG_W/dec_factor)-1))

        value = current(k.x,k.y) + 0.5 + ((k.dx*k.xc) + (k.dy*xr) + \
                                            (k.ds*k.xs))

        #Checking whether the pixel will pass the contrast threshold
        cond3 = Condition(fabsf(value) < SIFT_CT)

        trH = k.dxx + k.dyy
        detH = (k.dxx * k.dyy) - (k.dxy* k.dxy)
        response = ((SIFT_CUT + 1) * (SIFT_CUT))/ SIFT_CUT

        # Another checking condition, the science of which escapes 
        # me 
        cond4 = Condition((det_H, "<=", 0) & \
                            ((trH * trH / detH), ">=", response))

        # The main condition that is used for selecting the keypoints
        main_cond = cond1 & cond2 & cond3 & cond4

        # Variables that will be used to update values to the Keypoint 
        l_scale = SIFT_SIGMA * powf(2.0, k.tmp_layer/SIFT_INTVLS)
        norm = powf(2.0, k.octave -1)
        kpt_c = tmp_c * norm
        kpt_r = tmp_r * norm
        n_scale = l_scale * norm

        # Final process that ends the sifting(pardon the pun) of the Kepoints by 
        # creating a new list of Keypoint Structures
        cond_combine = Function(([k], range_), Keypoint, \
                        "keypoint_refinement2"+ str(m*layers +l) + "_" + name)  
        cond_combine.defn = [Select(main_cond, Keypoint(x=kpt_c, y=kpt_r, octave=k.m, \
                                layer=k.layer, rlayer=k.tmp_layer, scale=n_scale,\
                                ci = k.tmp_c, ri = k.tmp_r, layer_scale=l_scale, ort=k.ort, \
                                grad=k.grad, tmp_r=k.tmp_r, tmp_c=k.tmp_c, \
                                tmp_layer=k.tmp_layer, dx=k.dx, dy=k.dy, ds=k.ds, xs=k.xs, \
                                xc=k.xc, xr=k.xr, dxx=k.dxx, dyy=k.dyy, dxy=k.dxy), NULL)] 
        return cond_combine

    refined_list = {}

    for m in range(0, nOCT): 
        for l in range(1, nDoGLayers): 
            layer_index = m * nDoGlayers + l
            refined_list1[layer_index] = kpt_refine2(Dog_img[layer_index-1], \
                                                        Dog_img[layer_index],\
                                                        Dog_img[layer_index+1], \
                                                        kpt_dec_func.range_(), m, l, "kpt")

    Mid_calc = PolyStruct('d_kptr': Float, 'd_kptc': Float)
    md = Variable(Mid_calc)

    def ort_hist1(range_, m, l, name):
        #Casting to an Int needs to be made a function in Polymage? 
        kptr_ri = int(kpt.ri+0.5)
        kptr_ci = int(kpt.ci+0.5)

        dd_kptr = kpt.ri-kptr_ri
        dd_kptc = kpt.ci-kptr_ci

        mid_update = Function(([k], dom), Float, \
                            "d_kptr"+ str(m*layers +l) + "_" + name)
        mid_update = [Mid_calc(d_kptr=d_kptr, d_kptc=d_kptc)]

        return mid_update

    tmp_bin = Polybin(36)

    def ort_hist2(grd, ort, range_, m_range_, m, l, name): 
        dec_factor = 1 << k.m
        win_radius = int(SIFT_O_RADIUS*k.kpt_scale)
        sigma = SIFT_ORI_F * k,layer_scale
        exp_factor =  -1.0/(2.0*sigma*sigma)

        i1 = Interval(Int, -win_radius, win_radius)

        r = int(kpt.ri+0.5)

        cond1 = Condition((r, "<=", 0) || (r, ">=", (IMG_H/dec_factor)-1))

        c = int(kpt.ci+0.5)

        cond2 = Condition((c, "<=", 0) || (c, ">=", (IMG_W/dec_factor)-1))

        magni = grd(r,c)
        angle = ort(r,c)

        double_pi = 6.283185307179586
        fbin = angle * nBins / double_pi

        weight = Exp((i-md.d_kptr) * (i-md.d_kptr) + (j-md.d_kptc) \
                            * (i-md.d_kptc) * exp_factor)
        bin = int(fbin - 0.5)
        d_fbin = fbin - 0.5 - bin 
        
        # Need to discuss the syntax of Polybin with Siddharth and then proceed


    MidU_stack = {}
    Refined_list2 = {}

    for m in range(0, nOCT): 
    for l in range(1, nDoGLayers): 
        layer_index = m * nDoGlayers + l
        MidU_stack[layer_index] = ort_hist1(cond_combine.range_(), m, l, "kpt")
        Refined_list2[layer_index] = ort_hist(Grad_img[layer_index-1], \
                                                Ort_img[layer_index],\
                                                Dog_img[layer_index+1], \
                                                cond_combine.range_(), mid_update.range_(), \
                                                m, l, "kpt")

    # FINAL RETURN #
    # This will be a list of keypoints instead of an image 
    return Refined_list2, Grad_img, Ort_img


