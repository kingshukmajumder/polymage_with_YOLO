from __init__ import *
import sys
from polymage_common import set_ghosts

sys.path.insert(0, ROOT)

from compiler   import *
from constructs import *

def w_jacobi(U_, F_, l, name, app_data, T):
    pipe_data = app_data['pipe_data']

    y = pipe_data['y']
    x = pipe_data['x']

    # L = app_data['L']

    invhh = pipe_data['invhh']

    jacobi_c = pipe_data['jacobi_c']
    c = jacobi_c[l]

    extent = pipe_data['extent']
    interior = pipe_data['interior']
    # ghosts = pipe_data['ghosts']

    # inner_box = interior[l]['inner_box']

    k = c * invhh[l]

    kernel = \
        [[0,     k, 0], \
         [k, 1-4*k, k], \
         [0,     k, 0]]

    W_ = TStencil(([y, x], [extent[l], extent[l]]), Double, str(name), T)

    if U_ != None:
        stencil = Stencil(U_, [y, x], kernel)
        W_.defn = [stencil - c * F_(y, x)]
    else:
        # Initialize U_ ourselves with 0
        #
        # TODO: introducing a ZeroFunction (UnityFunction) construct would help
        # in 'memset'ting or initializing such functions.
        U0 = Function(([y, x], [extent[l], extent[l]]),
                      Double, 'stencil_input')
        U0.defn = [0]
        stencil = Stencil(U0, [y, x], kernel)
        W_.defn = [stencil - c * F_(y, x)]

    # if l == L:
    #     set_ghosts(W_, ghosts[l], U_(y, x))
    # else:
    #     set_ghosts(W_, ghosts[l], 0.0)

    return W_
