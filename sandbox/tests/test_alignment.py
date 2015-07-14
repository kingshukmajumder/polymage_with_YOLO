from __future__ import absolute_import, division, print_function

from fractions import Fraction
import sys
sys.path.insert(0, '../')

from compiler import *
from constructs import *
from expression import *

R = Parameter(Int, "R")
C = Parameter(Int, "C")
P = Parameter(Int, "P")
B = Parameter(Int, "B")

x = Variable(Int, "x")
y = Variable(Int, "y")
z = Variable(Int, "z")
w = Variable(Int, "w")
c = Variable(Int, "c")

row = Interval(Int, 0, R+1)
col = Interval(Int, 0, C+1)
plane = Interval(Int, 0, P+1)
box = Interval(Int, 0, B+1)
cr  = Interval(Int, 0, 3)

cond = Condition(x, '>=', 1) & Condition(x, '<=', R) & \
       Condition(y, '>=', 1) & Condition(y, '<=', C)

cond4D = Condition(x, '>=', 1) & Condition(x, '<=', R) & \
         Condition(y, '>=', 1) & Condition(y, '<=', C) & \
         Condition(z, '>=', 1) & Condition(z, '<=', P) & \
         Condition(w, '>=', 1) & Condition(w, '<=', B)


def test_gray():
    img = Image(Float, "img", [R+2, C+2, 3])

    gray = Function(([x, y], [row, col]), Float, "gray")
    gray.defn = [ img(x, y, 0) * 0.299 \
                + img(x, y, 1) * 0.587 \
                + img(x, y, 2) * 0.114 ]

    vector = Function(([x], [row]), Float, "vector")
    vector.defn = [ gray(x, x) + gray(x, 0) + gray(0, x) ]

    pipeline = buildPipeline([vector], grouping = [[gray, vector]])

def test_flip():
    img = Image(Int, "img", [R+2, C+2])

    flip1 = Function(([y, x], [col, row]), Int, "flip1")
    flip1.defn = [ img(x+1, y) + img(x, y+1) ]

    flip2 = Function(([x, y], [row, col]), Int, "flip2")
    flip2.defn = [ flip1(y-1, x) + flip1(y, x-1) ]

    pipeline = buildPipeline([flip2], grouping = [[flip1, flip2]])

def test_robin():
    img = Image(Short, "img", [R+2, C+2, 3])

    robin1 = Function(([c, x, y], [cr, row, col]), Short, "robin1")
    robin1.defn = [ img(x, y, c) + 1 ]

    robin2 = Function(([y, c, x], [col, cr, row]), Short, "robin2")
    robin2.defn = [ robin1(c, x, y) - 1 ]

    robin3 = Function(([x, y, c], [row, col, cr]), Short, "robin3")
    robin3.defn = [ robin2(y, c, x) + 1 ]

    pipeline = buildPipeline([robin3], grouping = [[robin1, robin2, robin3]])

def test_high_dim():
    img = Image(Short, "img", [B+2, P+2, R+2, C+2])

    random1 = Function(([w, y, z, x], [box, row, plane, col]), Double, "random1")
    random1.defn = [ Case(cond4D, img(w, z, y, x) + 1) ]

    random2 = Function(([z, x, y, w], [plane, col, row, box]), Double, "random2")
    random2.defn = [ Case(cond4D, random1(w, y, z, x) - 1) ]

    random3 = Function(([x, w, y, z], [col, box, row, plane]), Double, "random3")
    random3.defn = [ Case(cond4D, random2(z, x, y, w) + 1) ]

    random4 = Function(([y, z, w, x], [row, plane, box, col]), Double, "random4")
    random4.defn = [ Case(cond4D, random3(x, w, y, z) - 1) ]

    random5 = Function(([z, w, x, y], [plane, box, col, row]), Double, "random5")
    random5.defn = [ Case(cond4D, random4(y, z, w, x) + 1) ]

    pipeline = buildPipeline([random5], grouping = [[random1, random2, random3, random4, random5]])

