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
    def __init__(self, in_w, in_h, in_ch, num_sample, data):
        self._data = data
        self._in_w = in_w
        self._in_h = in_h
        self._in_ch = in_ch
        self._num_sample = num_sample
        self._out_dims = 4
        self._fwd_function = data
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

   
