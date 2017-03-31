from __init__ import *
import sys
from polymage_common import set_ghosts

sys.path.insert(0, ROOT)

from compiler   import *
from constructs import *

def w_jacobi(U_, F_, l, name, app_data, T):
    pipe_data = app_data['pipe_data']

    z = pipe_data['z']
    y = pipe_data['y']
    x = pipe_data['x']

    invhh = pipe_data['invhh']

    jacobi_c = pipe_data['jacobi_c']
    c = jacobi_c[l]

    extent = pipe_data['extent']

    k = c * invhh[l]

    # common kernels
    row_0 = [0, 0, 0]
    row_mid_k = [0, k, 0]

    # mid plane kernel in z-dimension
    z_mid_plane = [row_mid_k, [k, 1-6*k, k], row_mid_k]
    """
        [[0,     k, 0], \
         [k, 1-6*k, k], \
         [0,     k, 0]]
    """

    # other plane kernels in z-dimension
    z_point = [row_0, row_mid_k, row_0]
    """
        [[0, 0, 0], \
         [0, k, 0], \
         [0, 0, 0]]
    """

    kernel = [z_point, z_mid_plane, z_point]
    """
       [
        [[0, 0, 0], \
         [0, k, 0], \
         [0, 0, 0]], \
        [[0,     k, 0], \
         [k, 1-6*k, k], \
         [0,     k, 0]]
        [[0, 0, 0], \
         [0, k, 0], \
         [0, 0, 0]]]
    """

    # determine the input to the stencil function
    if U_ != None:
        U = U_
    else:
        # Initialize U_ ourselves with 0
        U = Function(([z, y, x], [extent[l], extent[l], extent[l]]),
                     Double, 'zero_'+str(l))
        U.defn = [0]

    stencil = Stencil(U, [z, y, x], kernel)

    # TStencil function
    W_ = TStencil(([z, y, x], [extent[l], extent[l], extent[l]]),
                  Double, str(name), T)
    W_.defn = [stencil + c * F_(z, y, x)]

    return W_
