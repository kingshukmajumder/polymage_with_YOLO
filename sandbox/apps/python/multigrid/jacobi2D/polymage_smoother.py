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

    invhh = pipe_data['invhh']

    jacobi_c = pipe_data['jacobi_c']
    c = jacobi_c[l]

    extent = pipe_data['extent']

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
        # TODO: introducing a ZeroFunction (and UnityFunction) construct would help
        # in 'memset'ting or initializing such functions with 0 (and 1, resp.)
        U = Function(([y, x], [extent[l], extent[l]]),
                     Double, 'zero_'+str(l))
        U.defn = [0]
        stencil = Stencil(U, [y, x], kernel)
        W_.defn = [stencil - c * F_(y, x)]

    return W_
