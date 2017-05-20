from __future__ import absolute_import, division, print_function

import logging
import targetc as genc
import math
from constructs import *

logging.basicConfig(format="%(levelname)s: %(name)s: %(message)s")

class Layer(object):
    def __init__(self, in_layer):
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
    def params(self):
        return self._params
    @property
    def forward_pass(self):
        return self._fwd_function

    def back_propagate(self, bwd_func):
        return bwd_func

class DataLayer(Layer):
    def __init__(self, in_w, in_h, in_ch, num_sample, data, typ):
        self._data = data
        self._in_w = in_w
        self._in_h = in_h
        self._in_ch = in_ch
        self._num_sample = num_sample
        self._out_dims = 4
        self._fwd_function = data
        self._typ = typ
        Layer.__init__(0)

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
    def num_sample(self):
        return self._num_sample
    @property
    def data(self):
        return self._data
    @property
    def typ(self):
        return self._typ
    @property
    def out_dims(self):
        return self._out_dims
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

    def back_propagate(self, bwd_func):
        assert(bwd_func)
        # There is no back propogation for the data layer
        # Simply returning
        return

class ReLULayer(Layer):
    def __init__(self, in_layer):
        assert(in_layer)
        self._in_f = in_layer.forward
        dim = in_layer.out_dims
        Layer.__init__(in_layer)
        if dim == 1:
            x = Variable(UInt, 'x')
            X = Interval(UInt, 0, out_dim_size(0)) 
            forward = Function(([x],[X]), Float, "forward")
            forward.defn = [max(0, in_forward(x))]
        elif dim == 2:
            x = Variable(UInt, 'x')
            X = Interval(UInt, 0, out_dim_size(0)) 
            y = Variable(UInt, 'y')
            Y = Interval(UInt, 0, out_dim_size(1)) 
            forward = Function(([x, y], [X, Y]), Float, "forward")
            forward.defn = [max(0, in_forward(x, y))]
        elif dim == 3:
            x = Variable(UInt, 'x')
            X = Interval(UInt, 0, out_dim_size(0)) 
            y = Variable(UInt, 'y')
            Y = Interval(UInt, 0, out_dim_size(1)) 
            z = Variable(UInt, 'z')
            Z = Interval(UInt, 0, out_dim_size(2)) 
            forward = Function(([x, y, z], [X, Y, Z]), Float, "forward")
            forward.defn = [max(0, in_forward(x, y, z))]
        elif dim == 4:
            x = Variable(UInt, 'x')
            X = Interval(UInt, 0, out_dim_size(0)) 
            y = Variable(UInt, 'y')
            Y = Interval(UInt, 0, out_dim_size(1)) 
            z = Variable(UInt, 'z')
            Z = Interval(UInt, 0, out_dim_size(2)) 
            w = Variable(UInt, 'w')
            W = Interval(UInt, 0, out_dim_size(3)) 
            forward = Function(([x, y, z, w], [X, Y, Z, W]), Float, "forward")
            forward.defn = [max(0, in_forward(x, y, z, w))]
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
        if not f_in_grad.defn == None:
            dim = self._in_layer.out_dims
            if dim == 1:
                x = Variable(UInt, 'x')
                X = Interval(UInt, 0, out_dim_size(0)) 
                f_in_grad = Function(([x],[X]), Float, "f_in_grad")
                f_in_grad.defn = bwd_func(x) * Select(Condition(in_f(x) > 0), 1, 0)
            elif dim == 2:
                x = Variable(UInt, 'x')
                X = Interval(UInt, 0, out_dim_size(0)) 
                y = Variable(UInt, 'y')
                Y = Interval(UInt, 0, out_dim_size(1)) 
                f_in_grad = Function(([x, y], [X, Y]), Float, "f_in_grad")
                f_in_grad.defn = bwd_func(x, y) * Select(Condition(in_f(x, y) > 0), 1, 0)
            elif dim == 3:
                x = Variable(UInt, 'x')
                X = Interval(UInt, 0, out_dim_size(0)) 
                y = Variable(UInt, 'y')
                Y = Interval(UInt, 0, out_dim_size(1)) 
                z = Variable(UInt, 'z')
                Z = Interval(UInt, 0, out_dim_size(2)) 
                f_in_grad = Function(([x, y, z], [X, Y, Z]), Float, "f_in_grad")
                f_in_grad.defn = bwd_func(x, y, z) * Select(Condition(in_f(x, y, z) > 0), 1, 0)
            elif dim == 4:
                x = Variable(UInt, 'x')
                X = Interval(UInt, 0, out_dim_size(0)) 
                y = Variable(UInt, 'y')
                Y = Interval(UInt, 0, out_dim_size(1)) 
                z = Variable(UInt, 'z')
                Z = Interval(UInt, 0, out_dim_size(2)) 
                w = Variable(UInt, 'w')
                W = Interval(UInt, 0, out_dim_size(3)) 
                f_in_grad = Function(([x, y, z, w], [X, Y, Z, W]), Float, "f_in_grad")
                f_in_grad.defn = bwd_func(x, y, z, w) * Select(Condition(in_f(x, y, z, w) > 0), 1, 0)
            else:
                assert(0)

    def out_dim_size(i):
        return in_layer.out_dim_size(i)
