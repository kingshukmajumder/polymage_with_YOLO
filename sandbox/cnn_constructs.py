from __future__ import absolute_import, division, print_function

from expr_ast import *
from expr_types import *
from expression import *
import logging
import targetc as genc
import math
from utils import *
import copy
from constructs import *


logging.basicConfig(format="%(levelname)s: %(name)s: %(message)s")

class Network(Function):

    @staticmethod
    def ReLU(_input_layer):
        input_layer = _input_layer
        x = Variable(UInt, 'x')
        X = input_layer.dimensions[0]
        y = Variable(UInt, 'y')
        Y = input_layer.dimensions[1]
        z = Variable(UInt, 'z')
        Z = input_layer.dimensions[2]
        forward = Matrix(input_layer.typ, "forward_relu", [X, Y, Z], [x, y, z])
        forward.defn = [Max(Cast(input_layer.typ, 0.0), input_layer(x, y, z))]
        return forward

class DataLayer(Function):
    def __init__(self, _typ, _name, _dims, _var=None):
        self._in_w = _dims[0]
        self._in_h = _dims[1]
        self._in_ch = _dims[2]
        self._out_dims = 3
        self._typ = _typ
        self._dims = _dims
        intervals = []
        variables = []
        i = 0
        if(_var == None):
            for dim in self._dims:
                # Just assuming it will not be more that UInt
                intervals.append(Interval(UInt, 0, dim-1))
                variables.append(Variable(UInt, "_" + _name + str(i)))
                i = i + 1
            self._variables = variables
        else:
            for dim in self._dims:
                # Just assuming it will not be more that UInt
                intervals.append(Interval(UInt, 0, dim - 1))
            self._variables = _var
            variables = _var
        self._intervals = intervals
        self.description = _name
        Function.__init__(self,(variables, intervals),_typ,_name)

    @property
    def dimensions(self):
        return self._dims
    @property
    def in_w(self):
        return self._in_w
    @property
    def in_h(self):
        return self._in_h
    @property
    def in_ch(self):
        return self._in_ch
    @property
    def out_dims(self):
        return self._out_dims
    @property
    def name(self):
        return self._name
    @property
    def type(self):
        return self._type
    @property
    def out_dim_size(self, i):
        assert(i < 3)
        size = 0
        if i == 0:
            size = self.in_w
        elif i == 1:
            size = self.in_h
        elif i == 2:
            size = self.in_ch
        return size

    def clone(self, input=False):
        var = [v.clone() for v in self._variables]
        dimensions = self.dimensions.copy()
        newFunc = DataLayer(self._typ, self._name, dimensions, var)
        newFunc.description = self.description
        return newFunc