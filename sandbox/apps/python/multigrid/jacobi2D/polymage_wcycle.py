from __init__ import *

import sys
from polymage_smoother import w_jacobi
from polymage_defect import defect
from polymage_restrict import restrict
from polymage_interpolate import interpolate

sys.path.insert(0, ROOT)

from compiler import *
from constructs import *

def w_cycle(app_data):
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
    def rec_w_cycle(v, f, l, visit):

        visit[l] += 1

        # coarsest level
        if l == 0:
            ''' COARSE-SMOOTHING '''
            if nuc == 0:
                return v

            if visit[l] == 1:
                smooth_p1[l] = {}

            if l == L:
                fname = "Wcycle"
            else:
                fname = "Coarse"+"__visit_"+str(visit[l])

            smooth_p1[l][visit[l]] = \
                w_jacobi(v, f, l, fname, app_data, Tc)

            return smooth_p1[l][visit[l]]
        ###################################################
        # all other finer levels
        else:
            ''' PRE-SMOOTHING '''
            if visit[l] == 1:
                smooth_p1[l] = {}

            fname = "Pre_L"+str(l)+"__visit_"+str(visit[l])

            smooth_p1[l][visit[l]] = \
                w_jacobi(v, f, l, fname, app_data, T1)

            if nu1 <= 0:
                smooth_out = v
            else:
                smooth_out = smooth_p1[l][visit[l]]

            ###############################################
            ''' RESIDUAL '''

            if visit[l] == 1:
                r_h[l] = {}

            dname = "defect_L"+str(l)+"__visit_"+str(visit[l])
            r_h[l][visit[l]] = defect(smooth_out, f, l, dname, pipe_data)

            ###############################################
  
            ''' RESTRICTION '''
            if visit[l] == 1:
                r_2h[l] = {}

            rname = "restrict_L"+str(l-1)+"__visit_"+str(visit[l])
            r_2h[l][visit[l]] = restrict(r_h[l][visit[l]], l, rname, pipe_data)

            ###############################################
 
            ''''''''''''''''''
            ''' NEXT LEVEL '''
            ''''''''''''''''''

            if visit[l] == 1:
                e_2h[l] = {}

            # e_2h <- 0
            e_2h[l][visit[l]] = \
                rec_w_cycle(None, r_2h[l][visit[l]], l-1, visit)

            e_2h[l][visit[l]] = \
                rec_w_cycle(e_2h[l][visit[l]], r_2h[l][visit[l]], l-1, visit)

            ###############################################

            ''' INTERPOLATION & CORRECTION '''
            if l == L and nu2 <= 0:
                fname = "Wcycle"
            else:
                fname = "interp_correct_L"+str(l)+"__visit_"+str(visit[l])

            if nu1 <= 0:
                correct_in = v
            else:
                correct_in = smooth_p1[l][visit[l]]

            if visit[l] == 1:
                ec[l] = {}

            ec[l][visit[l]] = \
                interpolate(e_2h[l][visit[l]], correct_in, l, fname, pipe_data)

            if nu2 <= 0:
                return ec[l][visit[l]]
 
            ###############################################

            ''' POST-SMOOTHING '''

            if visit[l] == 1:
                smooth_p2[l] = {}

            fname = "Post_L"+str(l)+"__visit_"+str(visit[l])
            if l == L:
                fname = "Wcycle"

            smooth_p2[l][visit[l]] = \
                w_jacobi(ec[l][visit[l]], f, l, fname, app_data, T2)
 
            return smooth_p2[l][visit[l]]
    #######################################################

    visit = {}
    visit[L] = 0
    for l in range(0, L):
        visit[l] = 0

    # one whole v-cycle beginning at the finest level
    u = rec_w_cycle(V, F, L, visit)

    return u
