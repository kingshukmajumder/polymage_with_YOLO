from __future__ import absolute_import, division, print_function

import logging
import targetc as genc
import math
from constructs import *

logging.basicConfig(format="%(levelname)s: %(name)s: %(message)s")

class Layer(Function):
    def __init__(self, in_layer, ):
        self._in_layer = in_layer

    @property
    def input_layer(self):
        return self._in_layer
    @property
    def out_dims(self):
        return self._out_dims
    @property
    def out_dim_size(self):
        return self._out_dim_size
    @property
    def typ(self):
        return self._typ

class DataLayer(Function):
    def __init__(self, _typ, _name, _dims, _var):
        self._in_w = _dims[0]
        self._in_h = _dims[1]
        self._in_ch = _dims[2]
        self._out_dims = 3
        self._typ = _typ
        self._dims = _dims
        intervals = []
        variables = []
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
        assert(i < 4)
        size = 0
        if i == 0:
            size = self.in_w
        elif i == 1:
            size = self.in_h
        elif i == 2:
            size = self.in_ch
        elif i == 3:
            size = self.num_sample
        return size

    def clone(self, input=False):
        var = [v.clone() for v in self._variables]
        dimensions = self.dimensions.copy()
        newFunc = DataLayer(self._typ, self._name, dimensions, var)
        newFunc.description = self.description
        return newFunc

class ReLULayer(Layer):
    def __init__(self, in_layer):
        assert(in_layer)
        self._in_f = in_layer.forward
        dim = in_layer.out_dims
        Layer.__init__(in_layer)
        if dim == 1:
            x = Variable(UInt, 'x')
            X = Interval(UInt, 0, self.out_dim_size(0))
            forward = Function(([x],[X]), in_layer.typ, "forward_relu")
            forward.defn = [Max(Cast(in_layer.typ, 0.0), self.in_forward(x))]
        elif dim == 2:
            x = Variable(UInt, 'x')
            X = Interval(UInt, 0, self.out_dim_size(0))
            y = Variable(UInt, 'y')
            Y = Interval(UInt, 0, self.out_dim_size(1))
            forward = Function(([x, y], [X, Y]), in_layer.typ, "forward_relu")
            forward.defn = [Max(Cast(in_layer.typ, 0.0), self.in_forward(x, y))]
        elif dim == 3:
            x = Variable(UInt, 'x')
            X = Interval(UInt, 0, self.out_dim_size(0))
            y = Variable(UInt, 'y')
            Y = Interval(UInt, 0, self.out_dim_size(1))
            z = Variable(UInt, 'z')
            Z = Interval(UInt, 0, self.out_dim_size(2))
            forward = Function(([x, y, z], [X, Y, Z]), in_layer.typ, "forward_relu")
            forward.defn = [Max(Cast(in_layer.typ, 0.0), self.in_forward(x, y, z))]
        elif dim == 4:
            x = Variable(UInt, 'x')
            X = Interval(UInt, 0, self.out_dim_size(0))
            y = Variable(UInt, 'y')
            Y = Interval(UInt, 0, self.out_dim_size(1))
            z = Variable(UInt, 'z')
            Z = Interval(UInt, 0, self.out_dim_size(2))
            w = Variable(UInt, 'w')
            W = Interval(UInt, 0, self.out_dim_size(3))
            forward = Function(([x, y, z, w], [X, Y, Z, W]), in_layer.typ, "forward_relu")
            forward.defn = [Max(Cast(in_layer.typ, 0.0), self.in_forward(x, y, z, w))]
        else:
            assert(0)

    @property
    def out_dims(self):
        return self._in_layer.out_dims
    @property
    def out_dim_size(self):
        return self._in_layer.out_dim_size
    @property
    def in_forward(self):
        return self._in_f

    def back_propagate(self, bwd_func):
        assert(bwd_func)
        if not self.f_in_grad.defn == None:
            dim = self._in_layer.out_dims
            if dim == 1:
                x = Variable(UInt, 'x')
                X = Interval(UInt, 0, self.out_dim_size(0))
                f_in_grad = Function(([x],[X]), Float, "f_in_grad")
                f_in_grad.defn = bwd_func(x) * Select(Condition(self.in_f(x) > 0), 1, 0)
            elif dim == 2:
                x = Variable(UInt, 'x')
                X = Interval(UInt, 0, self.out_dim_size(0))
                y = Variable(UInt, 'y')
                Y = Interval(UInt, 0, self.out_dim_size(1))
                f_in_grad = Function(([x, y], [X, Y]), Float, "f_in_grad")
                f_in_grad.defn = bwd_func(x, y) * Select(Condition(self.in_f(x, y) > 0), 1, 0)
            elif dim == 3:
                x = Variable(UInt, 'x')
                X = Interval(UInt, 0, self.out_dim_size(0))
                y = Variable(UInt, 'y')
                Y = Interval(UInt, 0, self.out_dim_size(1))
                z = Variable(UInt, 'z')
                Z = Interval(UInt, 0, self.out_dim_size(2))
                f_in_grad = Function(([x, y, z], [X, Y, Z]), Float, "f_in_grad")
                f_in_grad.defn = bwd_func(x, y, z) * Select(Condition(self.in_f(x, y, z) > 0), 1, 0)
            elif dim == 4:
                x = Variable(UInt, 'x')
                X = Interval(UInt, 0, self.out_dim_size(0))
                y = Variable(UInt, 'y')
                Y = Interval(UInt, 0, self.out_dim_size(1))
                z = Variable(UInt, 'z')
                Z = Interval(UInt, 0, self.out_dim_size(2))
                w = Variable(UInt, 'w')
                W = Interval(UInt, 0, self.out_dim_size(3))
                f_in_grad = Function(([x, y, z, w], [X, Y, Z, W]), Float, "f_in_grad")
                f_in_grad.defn = bwd_func(x, y, z, w) * Select(Condition(self.in_f(x, y, z, w) > 0), 1, 0)
            else:
                assert(0)

    def out_dim_size(self, i):
        return self.in_layer.out_dim_size(i)
