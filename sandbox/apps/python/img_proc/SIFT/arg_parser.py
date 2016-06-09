#This is the arg_parser for sift.py

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

    parser.add_option('--img1',
                      action='store',
                      dest='img_file1',
                      help='input image file path for image1')

    parser.add_option('-t', '--timer',
                      action='store_true',
                      dest='timer',
                      default=False,
                      help='True : report execution time, \
                            False: do not collect timing info')

    parser.add_option('-d', '--display',
                      action='store_true',
                      dest='display',
                      default=False,
                      help='display output image')

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

    (options, args) = parser.parse_args()

    return options
