from __future__ import absolute_import, division, print_function

from fractions import Fraction
import sys
sys.path.insert(0, '../')

from compiler import *
from constructs import *

def test_reduction():

    R = Parameter(Int, "R")
    C = Parameter(Int, "C")
    x = Variable(Int, "x")
    y = Variable(Int, "y")
    z = Variable(Int, "z")

    row = Interval(Int, 0, R-1)
    col = Interval(Int, 0, C-1)

    img = Image(Float, "img", [R, C])

    cond = Condition(z, '<', x)

    N, beta = Wave.kaiserord(2.285 + 7.95 - 0.001, 1/Pi())

    s = Reduction(([x], [row]), ([x, z, y], [row, row, col]), Float, "s")
    s.defn = [ Case(cond, Reduce(s(x), N * beta * img(z, y) * img(x, y), Op.Sum)) ]

    p_estimates = [(R, 1000), (C, 1000)]
    pipeline = buildPipeline([s], \
                             pipe_name="s",
                             param_estimates=p_estimates)

    filename = 'red_naive.cpp'
    c_file = open(filename, 'w')
    c_file.write(pipeline.generate_code().__str__())
    c_file.close()
