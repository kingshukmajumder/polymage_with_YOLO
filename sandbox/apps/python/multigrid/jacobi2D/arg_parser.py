from __init__ import *

import optparse
import sys

sys.path.insert(0, ROOT+'apps/python/')

from pipe_options import *

def parse_args():

    help_str = \
    '"new" : from scratch | "existing" : compile and run |  "ready" : just run'
    parser.add_option('-m', '--mode',
                      type='choice',
                      action='store',
                      dest='mode',
                      choices=['new', 'existing', 'ready', 'tune'],
                      default=['new'],
                      help=help_str)

    parser.add_option('-c', '--cycle',
                      action='store',
                      dest='cycle',
                      choices=['V', 'W'],
                      default=['V'],
                      help='Multigrid Cycle Type (V or W)')

    parser.add_option('--nit',
                      action='store',
                      dest='nit',
                      help='Number of MG cycle iterations')

    parser.add_option('--n',
                      action='store',
                      dest='n',
                      default=255,
                      help='coarse-grid size in each dimension')

    parser.add_option('--L',
                      action='store',
                      dest='L',
                      default=2,
                      help='Number of multigrid levels')

    parser.add_option('--nu1',
                      action='store',
                      dest='nu1',
                      default=1,
                      help='Pre-smoothing steps')

    parser.add_option('--nuc',
                      action='store',
                      dest='nuc',
                      default=1,
                      help='Coarse smoothing steps')

    parser.add_option('--nu2',
                      action='store',
                      dest='nu2',
                      default=1,
                      help='Post-smoothing steps')

    parser.add_option('-p', '--problem',
                      action='store',
                      dest='problem',
                      default=1,
                      help='problem type')

    parser.add_option('-r', '--runs',
                      action='store',
                      dest='runs',
                      default=1,
                      help='number of runs')

    parser.add_option('-t', '--timer',
                      action='store_true',
                      dest='timer',
                      default=False,
                      help='True : report execution time, \
                            False: do not collect timing info')

    parser.add_option('--cxx',
                      action='store',
                      dest='cxx',
                      choices=['g++', 'icpc'],
                      default=['g++'],
                      help='CXX Compiler')

    parser.add_option('--cxx_flags',
                      action='store',
                      dest='cxx_flags',
                      default=['-O3'],
                      help='CXX Compiler flags')

    parser.add_option('--graph-gen',
                      action='store_true',
                      dest='graph_gen',
                      default=False,
                      help='True : generate .dot & .png file of pipeline graph, \
                            False: don\'t')

    parser.add_option('--naive',
                      action='store_true',
                      dest='naive',
                      default=False,
                      help='True : Run polymage naive. set g_size=1, \
                            False: don\'t')


    (options, args) = parser.parse_args()

    return options
