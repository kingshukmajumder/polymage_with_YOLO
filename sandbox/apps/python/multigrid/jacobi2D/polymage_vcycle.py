from __init__ import *

import sys
from polymage_smoother import w_jacobi
from polymage_defect import defect
from polymage_restrict import restrict
from polymage_interpolate import interpolate

sys.path.insert(0, ROOT)

from compiler import *
from constructs import *

def v_cycle(app_data):
    pipe_data = app_data['pipe_data']

    N = pipe_data['N']
    L = app_data['L']

    nu1 = app_data['nu1']
    nu2 = app_data['nu2']
    nuc = app_data['nuc']
    T1 = pipe_data['T1']
    T2 = pipe_data['T2']
    Tc = pipe_data['Tc']

    # initial guess
    V = Image(Double, "V_", [N[L]+2, N[L]+2])
    # rhs
    F = Image(Double, "F_", [N[L]+2, N[L]+2])

    jacobi_c = pipe_data['jacobi_c']

    # pre-smoothing and coarse-smoothing outputs
    smooth_p1 = {}
    # post-smoothing outputs
    smooth_p2 = {}

    # defect outputs
    r_h = {}
    # restrict outputs
    r_2h = {}
    # error outputs
    e_h = {}
    # interpolated error outputs
    e_2h = {}
    # corrected error outputs
    ec = {}

    #######################################################
    def rec_v_cycle(v, f, l):

        # coarsest level
        if l == 0:
            ''' COARSE-SMOOTHING '''
            if nuc == 0:
                return v

            if l == L:
                fname = app_data['cycle_name']
            else:
                fname = "Coarse"

            smooth_p1[l] = w_jacobi(v, f, l, fname, app_data, Tc)

            return smooth_p1[l]
        ###################################################
        # all other finer levels
        else:
            ''' PRE-SMOOTHING '''
            fname = "Pre_L"+str(l)

            smooth_p1[l] = w_jacobi(v, f, l, fname, app_data, T1)

            if nu1 <= 0:
                smooth_out = v
            else:
                smooth_out = smooth_p1[l]

            ###############################################
            ''' RESIDUAL '''

            r_h[l] = defect(smooth_out, f, l, "defect_L"+str(l),
                            pipe_data)

            ###############################################
            ''' RESTRICTION '''
            r_2h[l] = restrict(r_h[l], l, "restrict_L"+str(l-1), pipe_data)

            ###############################################
 
            ''''''''''''''''''
            ''' NEXT LEVEL '''
            ''''''''''''''''''
            # e_2h <- 0
            e_2h[l] = rec_v_cycle(None, r_2h[l], l-1)

            ###############################################

            ''' INTERPOLATION & CORRECTION '''
            if l == L and nu2 <= 0:
                fname = app_data['cycle_name']
            else:
                fname = "interp_correct_L"+str(l)

            if nu1 <= 0:
                correct_in = v
            else:
                correct_in = smooth_p1[l]

            ec[l] = interpolate(e_2h[l], correct_in, l, fname, pipe_data)

            if nu2 <= 0:
                return ec[l]
 
            ###############################################

            ''' POST-SMOOTHING '''
            fname = "Post_L"+str(l)
            if l == L:
                fname = app_data['cycle_name']

            smooth_p2[l] = w_jacobi(ec[l], f, l, fname, app_data, T2)
 
            return smooth_p2[l]
    #######################################################

    # one whole v-cycle beginning at the finest level
    u = rec_v_cycle(V, F, L)

    return u
