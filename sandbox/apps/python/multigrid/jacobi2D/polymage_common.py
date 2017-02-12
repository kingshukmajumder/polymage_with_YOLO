from __init__ import *

import sys
sys.path.insert(0, ROOT)

from compiler import *
from constructs import *

from fractions  import Fraction

def set_ghosts(r, ghosts, value):
    for ghost in ghosts:
        r.defn.append(Case(ghosts[ghost], value))

    return

def set_vars(app_data):
    pipe_data = app_data['pipe_data']

    L = app_data['L']

    y = Variable(Int, "y")
    x = Variable(Int, "x")

    pipe_data['y'] = y
    pipe_data['x'] = x

    n = Parameter(Int, "n")
    T1 = Parameter(Int, "T1")
    T2 = Parameter(Int, "T2")
    T3 = Parameter(Int, "T3")
    pipe_data['n'] = n
    pipe_data['T1'] = T1
    pipe_data['T2'] = T2
    pipe_data['Tc'] = T3

    # grid size at each level
    N = {}
    # jacobi weight (2D)
    omega = 4.0/5.0
    # mulitplier in the jacobi computation
    jacobi_c = {}
    # 1.0/(h*h)
    invhh = {}

    for l in range(0,L+1):
        if l == 0:
            N[0] = n
        else:
            N[l] = 2*N[l-1]+1

        h = 1.0/(N[l]+1)
        invhh[l] = 1.0/(h*h)

        # omega.D^-1 = omega.(d^-1.I) = omega * h^2/4.0
        # d^-1 depends on diagonal elements of A^h
        dinv = (h*h)/4.0
        jacobi_c[l] = omega * dinv
    #endfor

    pipe_data['N'] = N

    pipe_data['invhh']    = invhh
    pipe_data['jacobi_c'] = jacobi_c

    # extent in each dimension
    extent = {}
    for l in range(0, L+1):
        extent[l] = Interval(Int, 0, N[l]+1)

    pipe_data['extent'] = extent

    return

def set_cases(app_data):
    pipe_data = app_data['pipe_data']
    y = pipe_data['y']
    x = pipe_data['x']

    N = pipe_data['N']
    L = app_data['L']

    interior = {}
    ghosts = {}
    for l in range(0, L+1):
        # grid interior
        interior[l] = {}

        interior[l]['in_y'] = Condition(y, ">=", 1) \
                            & Condition(y, "<=", N[l])
        interior[l]['in_x'] = Condition(x, ">=", 1) \
                            & Condition(x, "<=", N[l])

        interior[l]['inner_box'] = interior[l]['in_y'] \
                                 & interior[l]['in_x']

        # grid ghosts
        ghosts[l] = {}

        # top and bottom planes
        ghosts[l]['ghost_top'] = Condition(y, "==", 0)
        ghosts[l]['ghost_bottom'] = Condition(y, "==", N[l]+1)

        # left and right planes
        ghosts[l]['ghost_left'] = Condition(x, "==", 0) \
                                & interior[l]['in_y']
        ghosts[l]['ghost_right'] = Condition(x, "==", N[l]+1) \
                                 & interior[l]['in_y']

    pipe_data['interior'] = interior
    pipe_data['ghosts'] = ghosts

    return
