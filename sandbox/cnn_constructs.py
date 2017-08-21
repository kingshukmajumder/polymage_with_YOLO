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

pipe_logger = logging.getLogger("pipe.py")
pipe_logger.setLevel(logging.DEBUG)
LOG = pipe_logger.log

class Network(Function):

    # Convolution operation
    # _input_layer: previous layer/ input to the convolution (in_w x in_h x in_ch)
    # _weights: k kernels/stencils (f x f x in_ch x k)
    # _fn_name: function name
    # _bias: bias (optional parameter)
    # _pad: pad size (optional parameter)
    @staticmethod
    def convolution(_input_layer, _weights, _fn_name, _bias=None, _pad=None):
        assert (_input_layer)
        assert (_weights)
        assert (_fn_name)

        input_layer = _input_layer
        weights = _weights
        bias = _bias
        fn_name = _fn_name
        # Input parameters
        # Update this to 4 to support for batches
        assert (len(input_layer.dimensions) == 3)
        in_w = input_layer.dimensions[0]
        in_h = input_layer.dimensions[1]
        in_ch = input_layer.dimensions[2]

        k = Variable(UInt, 'k')
        c = Variable(UInt, 'c')
        x = Variable(UInt, 'x')
        y = Variable(UInt, 'y')
        fh = Variable(UInt, 'fh')
        fw = Variable(UInt, 'fw')

        # Padding for the input
        pad = _pad
        if not (pad == None or pad == 0):
            p_w = in_w + (2 * pad)
            p_h = in_h + (2 * pad)
            cond = Condition(x, '>=', pad) & \
                        Condition(x, '<=', p_w - pad - 1) & \
                        Condition(y, '>=', pad) & \
                        Condition(y, '<=', p_h - pad - 1)
            pad_fn_name = fn_name + "_pad"
            input_pad = Matrix(Double, pad_fn_name, [p_w, p_h, in_ch], [x, y, c])
            expr = input_layer(x - pad, y - pad, c)
            input_pad.defn = [Case(cond, expr)]


        # Weight parameters
        assert (len(weights.dimensions) == 4)
        wt_fw = weights.dimensions[0]
        wt_fh = weights.dimensions[1]
        wt_ch = weights.dimensions[2]
        wt_k = weights.dimensions[3]

        LOG(logging.DEBUG, "Weights: "+str(wt_fw)+" x "+str(wt_fh)+" x "+str(wt_ch)+" x "+str(wt_k))

        assert (wt_ch == in_ch)

        Fhi = Interval(UInt, 0, wt_fh - 1)
        Fwi = Interval(UInt, 0, wt_fw - 1)
        Ki = Interval(UInt, 0, wt_k - 1)
        Ci = Interval(UInt, 0, wt_ch - 1)
        if (pad == None or pad == 0):
            Yi = Interval(UInt, 0, in_h - wt_fh)
            Xi = Interval(UInt, 0, in_w - wt_fw)
        else:
            Yi = Interval(UInt, 0, p_h - wt_fh)
            Xi = Interval(UInt, 0, p_w - wt_fw)

        output = Reduction(([x, y, k], [Xi, Yi, Ki]),
                           ([k, c, y, x, fh, fw], [Ki, Ci, Yi, Xi, Fhi, Fwi]), Double, fn_name)
        if (pad == None or pad == 0):
            output.defn = [Reduce(output(x, y, k), input_layer(x + fw, y + fh, c) * weights(fw, fh, c, k), Op.Sum)]
            output.dimensions = [in_w - wt_fw + 1, in_h - wt_fh + 1, wt_k]
            output.reductionDimensions = [wt_k, wt_ch, in_h - wt_fh + 1, in_w - wt_fw + 1, wt_fh, wt_fw]
        else:
            output.defn = [Reduce(output(x, y, k), input_pad(x + fw, y + fh, c) * weights(fw, fh, c, k), Op.Sum)]
            output.dimensions = [p_w - wt_fw + 1, p_h - wt_fh + 1, wt_k]
            output.reductionDimensions = [wt_k, wt_ch, p_h - wt_fh + 1, p_w - wt_fw + 1, wt_fh, wt_fw]

        output.is_mat_func = True

        LOG(logging.DEBUG, "Convolution: " + str(output.dimensions[0]) + " x " + str(output.dimensions[1]) + " x " + str(output.dimensions[2]))

        if not (_bias == None):
            output.default = bias(k)
        return output

    # Rectified Linear Unit (Normalization operation)
    # _input_layer: previous layer/ input to the ReLU (in_w x in_h x in_ch)
    # _fn_name: function name
    @staticmethod
    def ReLU(_input_layer, _fn_name):
        assert (_fn_name)
        assert (_input_layer)

        input_layer = _input_layer
        fn_name = _fn_name
        x = Variable(UInt, 'x')
        y = Variable(UInt, 'y')
        z = Variable(UInt, 'z')

        X = input_layer.dimensions[0]
        Y = input_layer.dimensions[1]
        Z = input_layer.dimensions[2]

        LOG(logging.DEBUG, "ReLU: " + str(X) + " x " + str(Y) + " x " + str(Z))

        # Normalization
        forward = Matrix(input_layer.typ, fn_name, [X, Y, Z], [x, y, z])
        forward.defn = [Max(Cast(input_layer.typ, 0.0), input_layer(x, y, z))]
        return forward

    # Maxpooling operation. Downsamples image by using max operation
    # _input_layer: previous layer/ input to the ReLU (in_w x in_h x in_ch)
    # _fh: kernel/stencil height
    # _fw: kernel/stencil weight
    # _stride: stride for applying the kernel
    # _fn_name: function name
    @staticmethod
    def maxpool(_input_layer, _fw, _fh, _stride, _fn_name):
        assert (_fn_name)
        assert (_input_layer)
        input_layer = _input_layer
        fn_name = _fn_name
        Fh = _fh
        Fw = _fw
        stride = _stride
        k = Variable(Int, 'k')
        x = Variable(Int, 'x')
        y = Variable(Int, 'y')
        fh = Variable(Int, 'fh')
        fw = Variable(Int, 'fw')

        # input parameters
        X = input_layer.dimensions[0]
        Y = input_layer.dimensions[1]
        K = input_layer.dimensions[2]

        Xo = (X - Fw) / stride + 1
        Yo = (Y - Fh) / stride + 1

        LOG(logging.DEBUG, "Maxpool: "+str(Xo)+" x "+str(Yo)+" x "+str(K))

        Ki = Interval(Int, 0, K - 1)
        Fhi = Interval(Int, 0, Fh - 1)
        Fwi = Interval(Int, 0, Fw - 1)
        Xi = Interval(Int, 0, Xo - 1)
        Yi = Interval(Int, 0, Yo - 1)

        # Downsample operation
        # TODO: Add default to max of negative double. Otherwise Max operation will always return 0
        maxpool = Reduction(([x, y, k], [Xi, Yi, Ki]), ([k, y, x, fh, fw], [Ki, Yi, Xi, Fhi, Fwi]), Double, fn_name)
        maxpool.defn = [Reduce(maxpool(x, y, k), input_layer(stride * x + fw, stride * y + fh, k), Op.Max)]
        maxpool.is_mat_func = True
        maxpool.dimensions = [Xo, Yo, K]
        maxpool.reductionDimensions = [K, Yo, Xo, Fh, Fw]
        return maxpool

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