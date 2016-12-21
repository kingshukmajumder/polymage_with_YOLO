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

    coeff = c * invhh[l]

    z_kernel = [[0, coeff, 0], [coeff, 1 - 6 * coeff, coeff], [0, coeff, 0]]
    z_minus_1_kernel = [[0, 0, 0], [0, coeff, 0], [0, 0, 0]]
    z_plus_1_kernel = [[0, 0, 0], [0, coeff, 0], [0, 0, 0]]

    kernel = [z_minus_1_kernel, z_kernel, z_plus_1_kernel]

    W_ = TStencil(([z, y, x], [extent[l], extent[l], extent[l]]), Double, str(name), T)

    if U_ != None:
        stencil = Stencil(U_, [z, y, x], kernel)
        W_.defn = [stencil - c * F_(z, y, x)]
    else:
        stencil_input = Function(([z, y, x], [extent[l], extent[l], extent[l]]),
                                 Double, 'stencil_input')
        stencil_input.defn = [0]
        stencil = Stencil(stencil_input, [z, y, x], kernel)
        W_.defn = [stencil - c * F_(z, y, x)]

    return W_
