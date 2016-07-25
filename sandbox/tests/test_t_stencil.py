from __future__ import absolute_import, division, print_function

from fractions import Fraction
import sys
import subprocess
sys.path.insert(0, '../')

from compiler import *
from constructs import *


def test_t_stencil_1d():

    R = Parameter(Int, "R")
    T = Parameter(Int, "T")
    x = Variable(Int, "x")

    xrow = Interval(Int, 0, R-1)

    img = Image(Float, "input", [R])

    f = Function(([x], [xrow]), Float, "f")
    f.defn = [3.1416 * img(x)]

    stencil = Stencil(f, [x], [1, 2, 3])
    tstencil = TStencil(([x], [xrow]), Float, "out", T)
    tstencil.defn = [ stencil + img(x-1) ]

    p_est = [ (R, 1024)]

    opts = []
    opts += 'optimize_storage'

    # build the pipeline
    pipeline = buildPipeline([tstencil],
                             param_estimates = p_est,
                             pipe_name = "tstencil_1d",
                             options = opts)

    filename = "test_t_stencil_1d_graph"
    dot_file = filename+".dot"
    png_file = filename+".png"
    g = pipeline.pipeline_graph
    g.write(filename+".dot")
    dotty_str = "dot -Tpng "+dot_file+" -o "+png_file
    subprocess.check_output(dotty_str, shell=True)

    filename = 'test_t_stencil_1d.cpp'
    c_file = open(filename, 'w')
    c_file.write(pipeline.generate_code().__str__())
    c_file.close()

    return

def test_t_stencil_2d():

    R = Parameter(Int, "R")
    C = Parameter(Int, "C")
    T = Parameter(Int, "T")
    x = Variable(Int, "x")
    y = Variable(Int, "y")

    row = Interval(Int, 0, R-1)
    col = Interval(Int, 0, C-1)

    img = Image(Float, "input", [R, C])

    kernel = [[1, 1, 1], [1, 0, 1], [1, 1, 1]]
    stencil = Stencil(img, [x, y], kernel)
    tstencil = TStencil(([x, y], [row, col]), Float, "out", T)
    tstencil.defn = [ stencil + 10*img(x, y) ]

    p_est = [ (R, 1024), (C, 1024) ]

    # build the pipeline
    pipeline = buildPipeline([tstencil],
                             param_estimates = p_est,
                             pipe_name = "tstencil_2d")

    filename = "test_t_stencil_2d_graph"
    dot_file = filename+".dot"
    png_file = filename+".png"
    g = pipeline.pipeline_graph
    g.write(filename+".dot")
    dotty_str = "dot -Tpng "+dot_file+" -o "+png_file
    subprocess.check_output(dotty_str, shell=True)

    filename = 'test_t_stencil_2d.cpp'
    c_file = open(filename, 'w')
    c_file.write(pipeline.generate_code().__str__())
    c_file.close()

    return

def test_t_stencil_3d():

    P = Parameter(Int, "P")
    R = Parameter(Int, "R")
    C = Parameter(Int, "C")
    T = Parameter(Int, "T")
    x = Variable(Int, "x")
    y = Variable(Int, "y")
    z = Variable(Int, "z")

    plane = Interval(Int, 0, P-1)
    row = Interval(Int, 0, R-1)
    col = Interval(Int, 0, C-1)

    img = Image(Float, "input", [P, R, C])

    kernel = [[[0, 1, 0], [1, 0, 1], [0, 1, 0]],
              [[1, 0, 1], [0, 1, 0], [1, 0, 1]],
              [[0, 1, 0], [1, 0, 1], [0, 1, 0]]]
    stencil = Stencil(img, [x, y, z], kernel)
    tstencil = TStencil(([x, y, z], [plane, row, col]), Float, "out", T)
    tstencil.defn = [ stencil + 10*img(x, y, z) ]

    p_est = [ (P, 1024), (R, 1024), (C, 1024) ]

    # build the pipeline
    pipeline = buildPipeline([tstencil],
                             param_estimates = p_est,
                             pipe_name = "tstencil_3d")

    filename = "test_t_stencil_3d_graph"
    dot_file = filename+".dot"
    png_file = filename+".png"
    g = pipeline.pipeline_graph
    g.write(filename+".dot")
    dotty_str = "dot -Tpng "+dot_file+" -o "+png_file
    subprocess.check_output(dotty_str, shell=True)

    filename = 'test_t_stencil_3d.cpp'
    c_file = open(filename, 'w')
    c_file.write(pipeline.generate_code().__str__())
    c_file.close()

    return
