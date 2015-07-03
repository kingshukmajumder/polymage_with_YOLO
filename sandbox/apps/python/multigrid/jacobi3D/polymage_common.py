from __future__ import absolute_import, division, print_function

import sys
sys.path.insert(0, '../../../../optimizer')
sys.path.insert(0, '../../../../frontend')

from Compiler   import *
from Constructs import *

from fractions  import Fraction

def setGhosts(r, ghosts, value):
    for ghost in ghosts:
        r.defn.append(Case(ghosts[ghost], value))

    return

def setVars(impipeDict, dataDict):
    L = dataDict['L']

    z = Variable(Int, "z")
    y = Variable(Int, "y")
    x = Variable(Int, "x")

    impipeDict['z'] = z
    impipeDict['y'] = y
    impipeDict['x'] = x

    n = Parameter(Int, "n")
    impipeDict['n'] = n

    # grid size at each level
    N = {}
    # jacobi weight (3D)
    omega = 8.0/9.0
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

        # omega.D^-1 = omega.(d^-1.I) = omega * h^2/6.0
        # d^-1 depends on diagonal elements of A^h
        dinv = (h*h)/6.0
        jacobi_c[l] = omega * dinv
    #endfor

    impipeDict['N'] = N

    impipeDict['invhh']    = invhh
    impipeDict['jacobi_c'] = jacobi_c

    # extent in each dimension
    extent = {}
    for l in range(0, L+1):
        extent[l] = Interval(Int, 0, N[l]+1)

    impipeDict['extent'] = extent

    return

def setCases(impipeDict, dataDict):
    z = impipeDict['z']
    y = impipeDict['y']
    x = impipeDict['x']

    N = impipeDict['N']
    L = dataDict['L']

    interior = {}
    ghosts = {}
    for l in range(0, L+1):
        # grid interior
        interior[l] = {}

        interior[l]['inZ'] = Condition(z, ">=", 1  ) \
                           & Condition(z, "<=", N[l])
        interior[l]['inY'] = Condition(y, ">=", 1  ) \
                           & Condition(y, "<=", N[l])
        interior[l]['inX'] = Condition(x, ">=", 1  ) \
                           & Condition(x, "<=", N[l])
 
        interior[l]['innerBox'] = interior[l]['inZ'] \
                                & interior[l]['inY'] \
                                & interior[l]['inX']
 
        # grid ghosts
        ghosts[l] = {}
 
        # front and back planes
        ghosts[l]['ghostFront']  = Condition(z, "==", 0)
        ghosts[l]['ghostBack']   = Condition(z, "==", N[l]+1)
 
        # top and bottom planes
        ghosts[l]['ghostTop']    = Condition(y, "==", 0) \
                                 & interior[l]['inZ']
        ghosts[l]['ghostBottom'] = Condition(y, "==", N[l]+1) \
                                 & interior[l]['inZ']
 
        # left and right planes
        ghosts[l]['ghostLeft']   = Condition(x, "==", 0) \
                                 & interior[l]['inY'] \
                                 & interior[l]['inZ']
        ghosts[l]['ghostRight']  = Condition(x, "==", N[l]+1) \
                                 & interior[l]['inY'] \
                                 & interior[l]['inZ']

    impipeDict['interior'] = interior
    impipeDict['ghosts'] = ghosts

    return
