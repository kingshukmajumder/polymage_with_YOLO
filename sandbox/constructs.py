#
# Copyright 2014-2016 Vinay Vasista, Ravi Teja Mullapudi, Uday Bondhugula,
# and others from Multicore Computing Lab, Department of Computer Science
# and Automation, Indian Institute of Science
#

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# constructs.py : Front-end design of PolyMage is defined here.
#

from __future__ import absolute_import, division, print_function

# TODO remove this at some point
from expr_ast import *
from expr_types import *
from expression import *
import logging
import targetc as genc
import math
from utils import *

logging.basicConfig(format="%(levelname)s: %(name)s: %(message)s")

"""
class Max(InbuiltFunction):
    def __init__(self, _leftExpr, _rightExpr, typeCheck = True):
        if typeCheck:
            _leftTyp = getType(_leftExpr)
            _rightTyp = getType(_rightExpr)
            assert _leftTyp == _rightTyp
        InbuiltFunction.__init__(self, _leftExpr, _rightExpr)
   
    def getType(self):
        return getType(self._args[0])

    def clone(self):
        cloneArgs = [ arg.clone() for arg in self._args ]
        return Max(cloneArgs[0], cloneArgs[1])

    def __str__(self):
        leftStr = self._args[0].__str__()
        rightStr = self._args[1].__str__()
        return "isl_max(" + leftStr + ", " + rightStr + ")"  

class Min(InbuiltFunction):
    def __init__(self, _leftExpr, _rightExpr, typeCheck = True):
        if typeCheck:
            _leftTyp = getType(_leftExpr)
            _rightTyp = getType(_rightExpr)
            assert _leftTyp == _rightTyp
        InbuiltFunction.__init__(self, _leftExpr, _rightExpr)
    
    def getType(self):
        return getType(self._args[0])

    def clone(self):
        cloneArgs = [ arg.clone() for arg in self._args ]
        return Min(cloneArgs[0], cloneArgs[1])

    def __str__(self):
        leftStr = self._args[0].__str__()
        rightStr = self._args[1].__str__()
        return "isl_min(" + leftStr + ", " + rightStr + ")"
"""

class Pow(InbuiltFunction):
    def __init__(self, _leftExpr, _rightExpr):
        InbuiltFunction.__init__(self, _leftExpr, _rightExpr)
   
    def getType(self):
        return Double

    def clone(self):
        cloneArgs = [ arg.clone() for arg in self._args ]
        return Pow(cloneArgs[0], cloneArgs[1])

    def __str__(self):
        leftStr = self._args[0].__str__()
        rightStr = self._args[1].__str__()
        return "pow(" + leftStr + ", " + rightStr + ")"

class Powf(InbuiltFunction):
    def __init__(self, _leftExpr, _rightExpr):
        InbuiltFunction.__init__(self, _leftExpr, _rightExpr)
    
    def getType(self):
        return Float

    def clone(self):
        cloneArgs = [ arg.clone() for arg in self._args ]
        return Powf(cloneArgs[0], cloneArgs[1])

    def __str__(self):
        leftStr = self._args[0].__str__()
        rightStr = self._args[1].__str__()
        return "powf(" + leftStr + ", " + rightStr + ")"

class Log(InbuiltFunction): # Natural Log
    def __init__(self, _expr):
        InbuiltFunction.__init__(self, _expr)

    def getType(self):
        return Double

    def clone(self):
        return Log(self._args[0].clone())

    def __str__(self):
        return "log(" +  self._args[0].__str__() +  ")"

class RandomFloat(InbuiltFunction): # Random Float b/w 0.0f and 1.0f
    def __init__(self):
        InbuiltFunction.__init__(self)

    def getType(self):
        return Float

    def clone(self):
        return RandomFloat()

    def __str__(self):
        return "(static_cast<float> (rand()) / static_cast<float> (RAND_MAX))"

class Pi(InbuiltFunction):
    def __init__(self):
        InbuiltFunction.__init__(self)

    def getType(self):
        return Double

    def clone(self):
        return Pi()

    def __str__(self):
        return "M_PI"

class Exp(InbuiltFunction):
    def __init__(self, _expr):
        InbuiltFunction.__init__(self, _expr)

    def getType(self):
        return Double

    def clone(self):
        return Exp(self._args[0].clone())

    def __str__(self):
        return "std::exp(" +  self._args[0].__str__() +  ")"

class Sin(InbuiltFunction):
    def __init__(self, _expr):
        InbuiltFunction.__init__(self, _expr)

    def getType(self):
        return Double

    def clone(self):
        return Sin(self._args[0].clone())

    def __str__(self):
        return "std::sin(" +  self._args[0].__str__() +  ")"

class Cos(InbuiltFunction):
    def __init__(self, _expr):
        InbuiltFunction.__init__(self, _expr)
    
    def getType(self):
        return Double

    def clone(self):
        return Cos(self._args[0].clone())

    def __str__(self):
        return "std::cos(" +  self._args[0].__str__() +  ")"

class Sqrt(InbuiltFunction):
    def __init__(self, _expr):
        InbuiltFunction.__init__(self, _expr)
    
    def getType(self):
        return Double

    def clone(self):
        return Sqrt(self._args[0].clone())

    def __str__(self):
        return "std::sqrt(" +  self._args[0].__str__() +  ")"

class Sqrtf(InbuiltFunction):
    def __init__(self, _expr):
        InbuiltFunction.__init__(self, _expr)
    
    def getType(self):
        return Float

    def clone(self):
        return Sqrtf(self._args[0].clone())

    def __str__(self):
        return "std::sqrtf(" +  self._args[0].__str__() +  ")"

class Conj(InbuiltFunction):
    def __init__(self, _expr):
        InbuiltFunction.__init__(self, _expr)

    def getType(self):
        return Complex

    def clone(self):
        return Conj(self._args[0].clone())

    def __str__(self):
        return "std::conj(" + self._args[0].__str__() + ")"

class Real(InbuiltFunction):
    def __init__(self, _expr):
        InbuiltFunction.__init__(self, _expr)

    def getType(self):
        return Double

    def clone(self):
        return Real(self._args[0].clone())

    def __str__(self):
        return "(" + self._args[0].__str__() + ").real()"

class Abs(InbuiltFunction):
    def __init__(self, _expr):
        InbuiltFunction.__init__(self, _expr)

    def getType(self):
        argType = getType(self._args[0])
        return Double if argType is Complex else argType

    def clone(self):
        return Abs(self._args[0].clone())

    def __str__(self):
        return "std::abs(" +  self._args[0].__str__() +  ")"

class ChbEvl(InbuiltFunction):
    def __init__(self, x, arr_typ):
        InbuiltFunction.__init__(self, x, arr_typ)

    def getType(self):
        return Double

    def clone(self):
        return ChbEvl(self._args[0].clone(), self._args[1].clone())

    def __str__(self):
        return "chbevl(" + self._args[0].__str__() + ", " \
                                    + self._args[1].__str__() + ")"

class Cast(AbstractExpression):
    def __init__(self, _typ, _expr):
        _expr = Value.numericToValue(_expr)
        assert _typ in [Float, Double, 
                        UChar, Char, 
                        UShort, Short, 
                        UInt, Int, 
                        ULong, Long,
                        Complex]
        assert(isinstance(_expr, AbstractExpression))
        self._typ  = _typ
        self._expr = _expr

    @property
    def typ(self):
        return self._typ

    @property 
    def expression(self):
        return self._expr

    def collect(self, objType):
        objs = []
        objs += self._expr.collect(objType)
        if (type(self) == objType):
            objs += [self]
        return list(set(objs))

    def clone(self):
        return Cast(self._typ, self._expr.clone())
    
    def replace_refs(self, ref_to_expr_map):
        self._expr = substitute_refs(self._expr, ref_to_expr_map)

    def __str__(self):
        exprStr = self._expr.__str__()
        return "(" + str(genc.TypeMap.convert(self._typ)) + ") " + \
               "(" + exprStr + ")"

    def macro_expand(self):
        self._expr = self._expr.macro_expand()
        return self


class Select(AbstractExpression):
    def __init__(self, _cond, _trueExpr, _falseExpr, typeCheck = True):
        assert(isinstance(_cond, Condition))
        _trueExpr = Value.numericToValue(_trueExpr)
        _falseExpr = Value.numericToValue(_falseExpr)
        assert(isinstance(_trueExpr, AbstractExpression))
        assert(isinstance(_falseExpr, AbstractExpression))
        if typeCheck:
            trueType = getType(_trueExpr)
            falseType = getType(_falseExpr)
            assert trueType == falseType, str(_trueExpr)+" == "+str(_falseExpr)
        self._trueExpr = _trueExpr
        self._falseExpr = _falseExpr
        self._cond = _cond

    @property 
    def condition(self):
        return self._cond
    @property
    def trueExpression(self):
        return self._trueExpr     
    @property
    def falseExpression(self):
        return self._falseExpr

    def collect(self, objType):
        objs = []
        objs += self._cond.collect(objType)
        objs += self._trueExpr.collect(objType)
        objs += self._falseExpr.collect(objType)
        if (type(self) == objType):
            objs += [self]
        return list(set(objs))

    def replace_refs(self, ref_to_expr_map):
        self._cond.replace_refs(ref_to_expr_map)
        self._true_expr = substitute_refs(self._true_expr, ref_to_expr_map)
        self._false_expr = substitute_refs(self._false_expr, ref_to_expr_map)
    
    def clone(self):
        return Select(self._cond.clone(),
                      self._trueExpr.clone(),
                      self._falseExpr.clone())

    def __str__(self):
        condStr = self._cond.__str__()
        trueStr = self._trueExpr.__str__()
        falseStr = self._falseExpr.__str__()
        return "(" + condStr + "? " + trueStr + ": " + falseStr + ")"

    def macro_expand(self):
        self._trueExpr = self._trueExpr.macro_expand()
        self._falseExpr = self._falseExpr.macro_expand()
        return self

class Max(Select):
    def __init__(self, _leftExpr, _rightExpr, typeCheck = True):
        Select.__init__(self, Condition(_leftExpr, '>', _rightExpr),
                                        _leftExpr, _rightExpr, typeCheck)
class Min(Select):
    def __init__(self, _leftExpr, _rightExpr, typeCheck = True):
        Select.__init__(self, Condition(_leftExpr, '<', _rightExpr), 
                                        _leftExpr, _rightExpr, typeCheck)

class Variable(AbstractExpression):
    def __init__(self, _typ, _name):
        self._name    = _name
        self._typ     = _typ
    
    @property 
    def name(self):
        return self._name

    @property 
    def typ(self):
        return self._typ

    def clone(self):
        return self

    def __str__(self):
        return self._name.__str__()

    def macro_expand(self):
        return self

class Parameter(Variable):
    def __init__(self, _typ, _name):
        Variable.__init__(self, _typ, _name)
    
class Interval(object):
    def __init__(self, _typ,  _lb, _ub):
        _lb   = Value.numericToValue(_lb)
        _ub   = Value.numericToValue(_ub)
        assert(isinstance(_lb, AbstractExpression))
        assert(isinstance(_ub, AbstractExpression))
        self._lb   = _lb
        self._ub   = _ub
        self._typ  = _typ
 
    @property 
    def lowerBound(self):
        return self._lb
    @property 
    def upperBound(self):
        return self._ub
    @property 
    def typ(self):
        return self._typ

    def collect(self, objType):
        if (type(self) is objType):
            return [self]
        objs = self._lb.collect(objType)
        objs += self._ub.collect(objType)
        return list(set(objs))

    def clone(self):
        return Interval(self._typ, 
                        self._lb.clone(), 
                        self._ub.clone())

    def __str__(self):
        return '(' + self._lb.__str__() + ', ' +\
               self._ub.__str__() + ')'

class Reference(AbstractExpression):
    def __init__(self, _obj, _args):
        _args = [ Value.numericToValue(arg) for arg in _args]
        for arg in _args:
            assert(isinstance(arg, AbstractExpression))
        self._obj  = _obj
        self._args = _args

    @property
    def objectRef(self):
        return self._obj

    def _replace_ref_object(self, cloneObj):
        self._obj = cloneObj

    @property
    def arguments(self):
        return self._args

    def clone(self):
        cloneArgs = [arg.clone() for arg in self._args]
        return Reference(self._obj, cloneArgs)

    def collect(self, objType):
        objs = []
        for arg in self._args:
            objs += arg.collect(objType)
        if (type(self) is objType):
            objs += [self]
        return list(set(objs))

    def __str__(self):
        arg_str = ", ".join([arg.__str__() for arg in self._args])
        return self._obj.name + "(" + arg_str + ")"

    def macro_expand(self):
        expanded_args = []
        for arg in self._args:
            expanded_args.append(arg.macro_expand())

        self.args = expanded_args
        return self

# returns lengths of stuff one level deep in the list
# returns 0 if the object is a value
def get_inner_dimensions(lst):
    if isinstance(lst, list):
        dim = []
        for x in lst:
            if isinstance(x, list):
                dim.append(len(x))
            else:
                dim.append(0)
        return dim
    else:
        return 0


def list_elements_equal(lst):
    return not lst or lst.count(lst[0]) == len(lst)


def is_valid_kernel(kernel, num_dimensions):
    """Checks if the given kernel is a valid stencil by making sure
    that length(vardom) = nesting of kernel
    Parameters
    ----------
    kernel: list
    the kernel corresponding to the Stencil. This is usually a nested list

    num_dimensions: int
    number of dimensions the kernel posesses
    Returns
    -------
    is_valid: Bool
    """

    def is_valid_kernel_reucur(kernel, num_dimensions, closure_data):

        inner_dim = get_inner_dimensions(kernel)
        assert list_elements_equal(inner_dim), ("kernel does not have "
                                                "equal dimensions.\n"
                                                "Erroring dimensions: %s\n"
                                                "Kernel: %s" % (inner_dim,
                                                                kernel))
        if isinstance(kernel, list):
            for subkernel in kernel:
                new_closure_data = {
                    "total_dim": closure_data["total_dim"],
                    "parent": [kernel] + closure_data["parent"]
                }
                assert is_valid_kernel_reucur(subkernel,
                                              num_dimensions - 1,
                                              new_closure_data)
        else:
            if num_dimensions < 0:
                error_str = ("kernel has more dimensions than expected")
            elif num_dimensions > 0:
                error_str = ("Kernel has less dimensions than expected")
            else:
                return True

            parent_chain = " →\n\t".join(map(str, closure_data["parent"]))
            assert num_dimensions == 0, ("%s\n"
                                        "Expected Dimensions: %s\n"
                                        "Incorrect Kernel: %s\n" %
                                        (error_str,
                                         closure_data["total_dim"],
                                         parent_chain))
        return True
    
    
    # workaround for python scope madness - scopes get absolutely
    # _wrecked_ in a recursive inner function, so just pass around
    # a closure like the C people we are
    closure_data = {
        "total_dim": num_dimensions,
        "parent": []
    }
    return is_valid_kernel_reucur(kernel, num_dimensions, closure_data)

def get_valid_kernel_sizes(kernel):
    """
    Provides the sizes along the dimensions of the kernel,
    outermost to innermost for a valid kernel

    Parameters
    ----------
    kernel: nested list
    a valid N-dimensional kernel for computation
    
    Returns
    -------
    sizes: list
    1-D list of sizes, dimensions are ordered outermost to innermost
    """

    def kernel_dim_recur(subkernel):
        if isinstance(subkernel, list):
            if len(subkernel) > 0:
                return [len(subkernel)] + kernel_dim_recur(subkernel[0])
            else:
                return [0]

        else:
            return []
    return kernel_dim_recur(kernel)


def check_type(given_variable, expected_type):
    if not isinstance(given_variable, expected_type):
        raise TypeError("Expected {given_value} to be of type {expected_type}."
            "\nGiven Value: {given_value}"
            "\nGiven Type: {given_type}"
            "\nExpected Type: {expected_type}".format({
                "expected_type": str(type(given_variable)),
                "given_type": str(type(given_variable)),
                "given_value": str(given_variable)
            }))


class Stencil(AbstractExpression):
    def __init__(self, _input_fn, _iteration_vars, _kernel, _origin=None):
        check_type(_input_fn, Function)
        self._input_fn = _input_fn

        for v in _iteration_vars:
            check_type(v, Variable)
        self._iteration_vars = _iteration_vars

        assert is_valid_kernel(_kernel, len(_iteration_vars))
        self._kernel = _kernel

        self._sizes = get_valid_kernel_sizes(self._kernel)

        self._origin = _origin
        if self._origin is None:
            self._origin = list(map(lambda x: (x-1) // 2, self._sizes))

    @property
    def input_func(self):
        return self._input_fn
    @property
    def iter_vars(self):
        return self._iteration_vars
    @property
    def kernel(self):
        return self._kernel
    @property
    def sizes(self):
        return self._sizes
    @property
    def origin(self):
        return self._origin

    def __str__(self):
        return ("Stencil object"
                "\n%s"
                "\n\tinput: %s"
                "\n\titeration vars: %s"
                "\n\tdimension sizes: %s"
                "\n\torigin: %s"
                "\n\tkernel: %s" % (str(Stencil.macro_expand(self)),
                                    self._input_fn,
                                    list(map(str, self.iter_vars)),
                                    self.sizes,
                                    self._origin, self.kernel))

    @staticmethod
    def _build_indexed_kernel_recur(origin_vector, iter_vars, chosen_indeces,
                                    to_choose_sizes, subkernel):
        """
        Builds a list [([variable index], kernel weight] by taking the kernel,
        origin offset, and list of variables as parameters

        Parameters
        ----------
        origin_vector: [Int]
        the relative origin of the kernel with respect to the top left.
        If origin is (0, 0), then the kernel is built up as
        (x, y) to (x + w, y + h), since (0, 0) is taken to be the origin of the
        kernel.
        Usually, the origin is (w/2, h/2, ...)

        iter_vars: [Variable]
        Variables that represnt the iteration axes to
        index the source function
        Usually x, y, z, ...

        chosen_indeces: [Expression]
        pass "frozen" incdeces that have already been chosen. The function
        is now expected to generate all sub-indeces for these chosen
        indeces. One way to look at this is that chosen_indeces represents the
        chosen vector components of the final index.

        to_choose_sizes: [Int]
        Represents the sizes of the indeces that are yet to be chosen. Hence,
        these need to be looped over to pick _every_ index in these indeces.

        subkernel: [Int]^k (k-nested list)
        the remaining sub-space of the kernel that is yet to be chosen. Must
        be indexed from to_choose_sizes.

        Invariants
        ----------
        total kernel dimension: K
        subkernel dimension: K_s

        dim(origin_vector) = K
        len(iter_vars) = K
        len(to_choose_sizes) + len(chosen_indeces) = K

        K_s = len(to_choose_sizes)

        Returns
        -------
        indexed_kernel: [([index_expr: Expression], kernel_weight : Int)]

        Returns a list of tuples
        Each tuple has a list of indexing expressions, used to index the
        Kernel outermost to innerpost, along with the corresponding kernel
        weight at that index.
        """
        chosen = []
        for i in range(to_choose_sizes[0]):
            index_wrt_origin = iter_vars[0] + (i - origin_vector[0])
            if len(to_choose_sizes) == 1:
                chosen.append((chosen_indeces + [index_wrt_origin],
                              subkernel[i]))
            else:
                indexed = \
                    Stencil._build_indexed_kernel_recur(origin_vector[1:],
                                                        iter_vars[1:],
                                                        chosen_indeces +
                                                        [index_wrt_origin],
                                                        to_choose_sizes[1:],
                                                        subkernel[i])
                chosen.extend(indexed)
        return chosen

    @staticmethod
    def _build_indexed_kernel(origin, iter_vars, kernel):
        assert is_valid_kernel(kernel, num_dimensions=len(iter_vars))
        kernel_sizes = get_valid_kernel_sizes(kernel)
        return Stencil._build_indexed_kernel_recur(origin,
                                                   iter_vars,
                                                   [],
                                                   kernel_sizes,
                                                   kernel)

    def macro_expand(self):
        indexed_kernel = self._build_indexed_kernel(self._origin,
                                                    self._iteration_vars,
                                                    self.kernel)
        index_expr = 0
        for (indeces, weight) in indexed_kernel:
            ref = Reference(self._input_fn, indeces)
            index_expr += ref * weight

        # do this to force a pair of brackets around the entire indexing
        # expression
        # TODO: check if this is actually essential
        index_expr = 1 * index_expr

        return index_expr

class TStencil(object):
    def __init__(self, _var_domain, _kernel, _name,
                 _origin=None, _timesteps=1):

        self.name = _name
        self.var_domain = _var_domain
        self.timesteps = int(_timesteps)

        assert is_valid_kernel(_kernel, len(_var_domain))
        self.size = get_valid_kernel_sizes(_kernel)
        self.kernel = _kernel

        if _origin is None:
            self.origin = list(map(lambda x: math.floor(x / 2), self.size))

    def getObjects(self, objType):
        objs = []
        for interval in self.var_domain:
            objs += interval.collect(objType)
        return list(set(objs))

    def __str__(self):
        return ("Stencil object (%s)"
                "\n\tdomain: %s"
                "\n\tdimensions: %s"
                "\n\ttimesteps: %s"
                "\n\torigin: %s"
                "\n\tkernel: %s" % (self.name, list(map(str, self.var_domain)),
                                    self.size, self.timesteps,
                                    self.origin, self.kernel))



class Condition(object):
    def __init__(self, _left, _cond, _right):
        _left  = Value.numericToValue(_left)
        _right = Value.numericToValue(_right)
        assert(_cond in ['<', '<=', '>', '>=', '==', '!=', '&&', '||'])
        if _cond in ['<', '<=', '>', '>=', '==', '!=']:
            assert(isinstance(_left, AbstractExpression))
            assert(isinstance(_right, AbstractExpression))
        if _cond in ['&&', '||']:
            assert(isinstance(_left, Condition))
            assert(isinstance(_right, Condition))
        self._left  = _left
        self._right = _right
        self._cond  = _cond

    @property
    def lhs(self):
        return self._left
    @property
    def rhs(self):
        return self._right
    @property
    def conditional(self):
        return self._cond
   
    def clone(self):
        return Condition(self._left.clone(), self._cond, 
                         self._right.clone())

    def collect(self, objType):
        if (type(self) is objType):
            return [self]
        objs = self._left.collect(objType) + self._right.collect(objType)
        return list(set(objs))

    def replace_refs(self, ref_to_expr_map):
        if(isinstance(self._left, Condition)):
            self._left.replace_refs(ref_to_expr_map)
        else:
            self._left = substitute_refs(self._left, ref_to_expr_map)
        if(isinstance(self._right, Condition)):
            self._right.replace_refs(ref_to_expr_map)
        else:
            self._right = substitute_refs(self._right, ref_to_expr_map)

    def split_to_conjuncts(self):
        conjuncts = []
        if self._cond in ['<', '<=', '>', '>=', '==']:
            conjuncts.append([self])
        elif (self._cond  == '!='):
            less_than = Condition(self._left, '<', self._right)
            conjuncts.append([less_than])
            greater_than = Condition(self._left, '>', self._right)
            conjuncts.append([greater_than])
        elif (self._cond == '||'):
            conjuncts = self._left.split_to_conjuncts() + \
                        self._right.split_to_conjuncts()
        elif (self._cond == '&&'):
            left_conjuncts = self._left.split_to_conjuncts()
            right_conjuncts = self._right.split_to_conjuncts()
            for lconjunct in left_conjuncts:
                for rconjunct in right_conjuncts:
                    conjuncts.append(lconjunct + rconjunct)
        else:
            assert False
        return conjuncts

    def __and__(self, other):
        assert(isinstance(other, Condition))
        return Condition(self, '&&', other)

    def __or__(self, other):
        assert(isinstance(other, Condition))
        return Condition(self, '||', other)
    
    def __str__(self):        
        if (self._cond is None):
            assert self._left is None and self._right is None
            return ""
        left_str = self._left.__str__()
        right_str = self._right.__str__()
        return "(" + left_str + " " + self._cond + " " + right_str + ")"


class Case(object):
    def __init__(self, _cond, _expr):
        _expr = Value.numericToValue(_expr)
        assert(isinstance(_cond, Condition))
        assert(isinstance(_expr, (AbstractExpression, Reduce)))
        self._cond = _cond

        if isinstance(_expr, AbstractExpression):
            self._expr = _expr.macro_expand()
        else:
            self._expr = _expr

    @property
    def condition(self):
        return self._cond
    @property
    def expression(self):
        return self._expr

    def collect(self, objType):
        if (type(self) is objType):
            return [self]
        objs = self._cond.collect(objType) + self._expr.collect(objType)
        return list(set(objs))

    def replace_refs(self, ref_to_expr_map):
        self._cond.replace_refs(ref_to_expr_map)
        self._expr = substitute_refs(self._expr, ref_to_expr_map)

    def clone(self):
        return Case(self._cond.clone(), self._expr.clone())

    def __str__(self):
        return 'Case(' + self._cond.__str__() + ')' +\
                '{ ' + self._expr.__str__() + ' }'

class Op(object):
    Sum = 0
    Mul = 1
    Min = 2
    Max = 3

class Idiom_type(object):
    mat_mat_mul = 0
    mat_vec_mul = 1
    sig_fft = 2
    sig_ifft = 3

class Reduce(object):
    def __init__(self, _red_ref, _expr, _op_typ):
        assert isinstance(_red_ref, Reference)
        assert isinstance(_red_ref.objectRef, Reduction)
        _expr = Value.numericToValue(_expr)
        assert isinstance(_expr, AbstractExpression)
        assert _op_typ in [Op.Sum, Op.Mul, Op.Min, Op.Max]

        self._red_ref = _red_ref
        self._expr = _expr
        self._op_typ = _op_typ

    @property 
    def accumulate_ref(self):
        return self._red_ref
    @property 
    def expression(self):
        return self._expr
    @property 
    def op_type(self):
        return self._op_typ

    def replace_refs(self, ref_to_expr_map):
        self._expr = substitute_refs(self._expr, ref_to_expr_map)
        self._red_ref = substitute_refs(self._red_ref, ref_to_expr_map)

    def collect(self, objType):
        if (type(self) is objType):
            return [self]
        
        objs = self._red_ref.collect(objType) + self._expr.collect(objType)
        return list(set(objs))  

    def clone(self):
        return Reduce(self._red_ref.clone(), self._expr.clone(), self._op_typ)

    def __str__(self):
        op_str = None
        op_sep = None
        if (self._op_typ == Op.Sum):
            op_str = ''
            op_sep = ' + '
        elif (self._op_typ == Op.Mul):
            op_str = ''
            op_sep = ' * '
        elif (self._op_typ == Op.Min):
            op_str = 'Min'
            op_sep = ', '
        elif (self._op_typ == Op.Max):
            op_str = 'Max'
            op_sep = ', '
        else:
            assert False

        ret_str = 'Reduce [ ' + self._red_ref.__str__() + ' = ' + \
                  op_str + '(' + self._red_ref.__str__() + op_sep + \
                  self._expr.__str__() + ') ]'
        return ret_str

class Function(object):
    def __init__(self, _varDom, _typ, _name, _const=""):
        self._name      = _name
        # Type of the scalar range of the function
        self._typ       = _typ
        # Variables of the function
        self._variables = None
        # Constant function (standalone)
        if _const == "const":
            self._const = True
        else:
            self._const = False

        # Gives the domain of each variable. Domain of each variable is
        # expected to be over integers. Function evaluation in the
        # lexicographic order of the domain is assumed to be valid.

        assert(len(_varDom[0]) == len(_varDom[1]))
        for i in range(0, len(_varDom[0])):
            assert(isinstance(_varDom[0][i], Variable))
            assert(isinstance(_varDom[1][i], Interval))
            assert(_varDom[0][i].typ ==  _varDom[1][i].typ)
        # add check to ensure that upper bound and lower bound expressions
        # for each variable are only defined in terms of the function and
        # global parameters

        # Should bounds be restricted only to parameters or function variables
        # be allowed? No for now

        # Should the domain be restricted to the positive quadrant?
        # Can this be done automatically
        self._variables = _varDom[0]
        self._varDomain = _varDom[1]

        # dimensionality of the Function
        self._ndims = len(self._variables)

        # * Body of a function is composed of Case and Expression constructs.
        # * The Case constructs are expected to be non-overlapping. Therefore,
        #   value at each point in the function domain is uniquely defined.
        self._body      = []

        self._mat_func = False

        self.no_return_value = False
        self._dimensions = []

    @property
    def name(self):
        return self._name
    @property
    def typ(self):
        return self._typ
    @property
    def is_const_func(self):
        return self._const

    @property
    def no_return_value(self):
        return self._no_return_value

    @no_return_value.setter
    def no_return_value(self, _value):
        self._no_return_value = _value


    # Property to check if the function is of Matrix type
    @property
    def is_mat_func(self):
        return  self._mat_func

    @is_mat_func.setter
    def is_mat_func(self, _is_mat_func):
        self._mat_func = _is_mat_func

    @property
    def idiom_match_found(self):
        return self._idiom_match_found

    @property
    def dimensions(self):
        return self._dimensions

    @dimensions.setter
    def dimensions(self, dims):
        self._dimensions = dims

    @property
    def idiom(self):
        return self._idiom

    @property
    def variableDomain(self):
        return (self._variables, self._varDomain)
           
    @property
    def domain(self):
        return self._varDomain

    @property
    def variables(self):
        return self._variables

    @property
    def ndims(self):
        return self._ndims

    @property
    def defn(self):
        return self._body
    @defn.setter
    def defn(self, _def):
        assert(self._body == [])
        assert(len(_def) > 0), str(_def) + " " + str(self._name)
        case_type = 0
        non_case_type = 0
        for case in _def:
            case = Value.numericToValue(case)
            assert(isinstance(case, (Case, AbstractExpression))),str(case)

            # if the function is defined using Case, all the definition parts
            # in the list '_def' must be of the type Case.
            if isinstance(case, Case):
                case_type += 1
            else:
                non_case_type += 1

            assert(non_case_type <= 1)
            assert(case_type * non_case_type == 0)

            # check if the Case and Expression constructs only use
            # function variables and global parameters

            # MOD -> if _def is not a Case, shouldnt it be disallowed after
            # the first definition?
            self._body.append(case)

    def set_idiom_match_found(self,match_found):
        self._idiom_match_found = match_found

    def set_idiom(self,idiom):
        self._idiom = idiom

    def __call__(self, *args):
        assert(len(args) == len(self._variables))
        for arg in args:
            arg = Value.numericToValue(arg)
            assert(isinstance(arg, AbstractExpression))
        return Reference(self, args)

    def replace_refs(self, ref_to_expr_map):
        num_cases = len(self._body)
        for i in range(0, num_cases):
            if isinstance(self._body[i], Case):
                self._body[i].replace_refs(ref_to_expr_map)
            else:
                self._body[i] = substitute_refs(self._body[i], ref_to_expr_map)

    def getObjects(self, objType):
        objs = []
        for case in self._body:
            objs += case.collect(objType)
        for interval in self._varDomain:
            objs += interval.collect(objType)
        return list(set(objs))

    def hasBoundedIntegerDomain(self):
        boundedIntegerDomain = True
        for varDom in self._varDomain:
            if isinstance(varDom, Interval):
                if(not isAffine(varDom.lowerBound) or
                   not isAffine(varDom.upperBound)):
                    boundedIntegerDomain = False
                    break
            else:
                boundedIntegerDomain = False
                break

        return boundedIntegerDomain

    def clone(self):
        newBody = [ c.clone() for c in self._body ]
        varDom = ( [ v.clone() for v in self._variables],
                   [ d.clone() for d in self._varDomain] )
        _const = ""
        if self.is_const_func:
            _const = "const"
        newFunc = Function(varDom, self._typ, self._name, _const)
        newFunc.defn = newBody
        newFunc.is_mat_func = self.is_mat_func
        newFunc.dimensions = self.dimensions
        return newFunc

    def __str__(self):
        if (self._body):
            var_str = ", ".join([var.__str__() for var in self._variables])
            dom_str = ', '.join([self._variables[i].__str__() + \
                                 self._varDomain[i].__str__()\
                                   for i in range(len(self._varDomain))])
            case_str = "{ " + "\n ".join([case.__str__() \
                                            for case in self._body]) + " }"
            return "Domain: " + dom_str + '\n' + self._name + \
                   "(" + var_str + ") = " + case_str + '\n'
        else:
            return self._name

    def __mul__(self, other):
        mat1 = self
        mat2 = other

        assert (mat1.is_mat_func)
        if not isinstance(mat2, Matrix):
            assert(mat2.is_mat_func)

        assert (mat1.typ == mat2.typ)
        assert(len(mat1.variables) == len(mat2.variables))
        return Matrix.mat_multiplication(mat1, mat2)

    def set_variables_and_intervals(self, var, intr):
        self._variables = var
        self._varDomain = intr

class Image(Function):
    def __init__(self, _typ, _name, _dims):
        _dims = [ Value.numericToValue(dim) for dim in _dims ]
        # Have to evaluate if a  stronger constraint
        # can be imposed. Only AbstractExpression in parameters?
        for dim in _dims:
            assert(isinstance(dim, AbstractExpression))
        self._dims = _dims
        intervals = []
        variables = []
        i = 0
        for dim in self._dims:
            # Just assuming it will not be more that UInt
            intervals.append(Interval(UInt, 0, dim-1))
            variables.append(Variable(UInt, "_" + _name + str(i)))
            i = i + 1
        Function.__init__(self, (variables, intervals), _typ, _name)

    @property
    def dimensions(self):
        return tuple(self._dims)

    def __str__(self):
        dim_str = ", ".join([dim.__str__() for dim in self._dims])
        return self._name.__str__() + "(" + dim_str + ")"

class Reduction(Function):
    def __init__(self, _varDom, _redDom, _typ, _name):
        Function.__init__(self, _varDom, _typ, _name)
        # Gives the domain of the reduction. Reduction domain of each variable
        # is expected to be over integers. Reduction evaluation in the
        # lexicographic order of the domain is assumed to be valid.
        assert(len(_redDom[0]) == len(_redDom[1]))
        for i in range(0, len(_redDom[0])):
            assert(isinstance(_redDom[0][i], Variable))
            assert(isinstance(_redDom[1][i], Interval))
            assert(_redDom[0][i].typ ==  _redDom[1][i].typ)
        # add check to ensure that upper bound and lower bound
        # expressions for each variable are only defined in
        # terms of variables of the function and global parameters

        # Should bounds be restricted only to parameters or function
        # variables be allowed? No for now

        # Should the domain be restricted to the positive quadrant?
        # Can this be done automatically
        self._redVariables = _redDom[0]
        self._redDomain = _redDom[1]
        self._reductionDimensions = []
        self._reductionDimensions = []

        # Intial value of each accumulator cell. Default is set to zero of the
        # given type
        self._default   = Value(0, _typ)

    @property
    def default(self):
        return self._default
    @default.setter
    def default(self, _expr):
        _expr = Value.numericToValue(_expr)
        assert(isinstance(_expr, AbstractExpression))
        self._default = _expr

    @property
    def reductionDomain(self):
        return self._redDomain

    @property
    def reductionVariables(self):
        return self._redVariables

    @property
    def reductionDimensions(self):
        return self._reductionDimensions

    @reductionDimensions.setter
    def reductionDimensions(self, rednDims):
        self._reductionDimensions = rednDims

    @property
    def defn(self):
        return self._body

    @defn.setter
    def defn(self, _def):
        assert(self._body == [])
        for case in _def:
            case = Value.numericToValue(case)
            assert(isinstance(case, (Case, Reduce))),str(case)
            # check if the Case and Expression constructs only use
            # function variables and global parameters

            # Which way is better Case inside accumulate or accumulate inside
            # Case

            # MOD -> if _def is not a Case, shouldnt it be disallowed after
            # the first definition?
            self._body.append(case)

    def hasBoundedIntegerDomain(self):
        boundedIntegerDomain = True
        for varDom in self._varDomain:
            if isinstance(varDom, Interval):
                if(not isAffine(varDom.lowerBound) or
                   not isAffine(varDom.upperBound)):
                    boundedIntegerDomain = False
            else:
                boundedIntegerDomain = False

        for redDom in self._redDomain:
            if isinstance(redDom, Interval):
                if(not isAffine(redDom.lowerBound) or
                   not isAffine(redDom.upperBound)):
                    boundedIntegerDomain = False
            else:
                boundedIntegerDomain = False

        return boundedIntegerDomain

    def getObjects(self, objType):
        objs = []
        for case in self._body:
            objs += case.collect(objType)
        for interval in self._varDomain:
            objs += interval.collect(objType)
        for interval in self._redDomain:
            objs += interval.collect(objType)
        objs += self._default.collect(objType)
        return list(set(objs))

    def clone(self):
        newBody = [ r.clone() for r in self._body ]
        varDom = ( [ v.clone() for v in self._variables],
                   [ d.clone() for d in self._varDomain] )
        redDom = ( [ r.clone() for r in self._redVariables],
                   [ d.clone() for d in self._redDomain] )
        newRed = Reduction(varDom, redDom, self._typ, self._name)
        newRed.defn = newBody
        newRed.default = self._default.clone()
        newRed.is_mat_func = self.is_mat_func
        newRed.reductionDimensions = self.reductionDimensions
        newRed.dimensions = self.dimensions
        return newRed

    def __str__(self):
        if (self._body):
            varStr = ", ".join([var.__str__() for var in self._variables])
            domStr = ', '.join([self._variables[i].__str__() + \
                                self._varDomain[i].__str__()\
                                  for i in range(len(self._varDomain))])
            redDomStr = ', '.join([self._redVariables[i].__str__() + \
                                   self._redDomain[i].__str__()\
                                     for i in range(len(self._redDomain))])
            caseStr = "{ " + "\n ".join([case.__str__() \
                                           for case in self._body]) + " }"
            return "Domain: " + domStr + '\n' + \
                   "Reduction Domain: " + redDomStr + '\n' +\
                   self._name + "(" + varStr + ") = " +\
                    caseStr + '\n' + "Default: " + self._default.__str__()
        else:
            return self._name


class Matrix(Function):
    def __init__(self, _typ, _name, _dims, _var=None):
        _dims = [ Value.numericToValue(dim) for dim in _dims ]
        # Have to evaluate if a  stronger constraint
        # can be imposed. Only AbstractExpression in parameters?
        for dim in _dims:
            assert(isinstance(dim, AbstractExpression))
        self._dims = _dims
        self._typ = _typ
        self._name = _name
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
        Function.__init__(self,(variables, intervals),_typ,_name)

    @property
    def dimensions(self):
        return self._dims

    #TODO: change the name to be consistent with the rest of the code
    @property
    def isInput(self):
        if self.defn == []:
            return True
        return False

    @property
    def type(self):
        return self._type

    @property
    def variables(self):
        return self._variables

    @property
    def intervals(self):
        return self._intervals

    def __str__(self):
        dim_str = ", ".join([dim.__str__() for dim in self._dims])
        return self._name.__str__() #+ "(" + dim_str + ")"

    def clone(self, input=False):
        var = [v.clone() for v in self._variables]
        dimensions = self.dimensions.copy()
        newFunc = Matrix(self._typ, self._name, dimensions, var)
        if not self.isInput:
            newBody = [c.clone() for c in self._body]
            newFunc.defn = newBody
        return newFunc

    def convertReductionToMatrix(self, reduction):
        var = [v.clone() for v in reduction.variables]
        dimensions = reduction.variableDomain
        newFunc = Matrix(reduction._typ, reduction._name, dimensions, var)
        newBody = [c.clone() for c in reduction._body]
        newFunc.defn = newBody
        return newFunc

    def __mul__(self, other):
        mat1 = self
        mat2 = other
        # Initial checks to make sure that the parameters are only Matrices.
        if not isinstance(mat2, Matrix):
            assert(mat2.is_mat_func)
        assert (mat1.typ == mat2.typ)
        if isinstance(mat2, Matrix):
            assert (len(mat1.dimensions) == len(mat2.dimensions))
        else:
            assert(len(mat1.dimensions) == len(mat2.variables))
            assert(mat2.is_mat_func)

        return Matrix.mat_multiplication(mat1, mat2)

    @staticmethod
    def det(mat):
        # TODO: Add implementation
        return mat.dimensions[0]

    @staticmethod
    def mat_multiplication(mat1,mat2):
        variables = []
        intervals = []
        dimensions = []
        redn_dimensions = []

        if isinstance(mat1, Matrix):
            total_dimension_mat1 = mat1.dimensions.__len__()
            intervals = intervals.__add__(mat1.intervals[0:total_dimension_mat1 - 1])
        else:
            total_dimension_mat1 = mat1.variables.__len__()
            intervals = intervals.__add__(mat1.domain[0:total_dimension_mat1-1])

        variables = variables.__add__(mat1.variables[0:total_dimension_mat1 - 1])
        dimensions = dimensions.__add__(mat1.dimensions[0:total_dimension_mat1 - 1])
        redn_dimensions = redn_dimensions.__add__(mat1.dimensions)

        if isinstance(mat2, Matrix):
            total_dimension_mat2 = mat2.dimensions.__len__()
            intervals = intervals.__add__(mat2.intervals[1:total_dimension_mat2])
        else:
            total_dimension_mat2 = mat2.variables.__len__()
            intervals = intervals.__add__(mat2.domain[1:total_dimension_mat2])

        variables = variables.__add__(mat2.variables[1:total_dimension_mat2])
        dimensions = dimensions.__add__(mat2.dimensions[1:total_dimension_mat2])
        redn_dimensions = redn_dimensions.__add__(mat2.dimensions[1:total_dimension_mat2])

        var_dom = (variables, intervals)

        # Generating a random string of 3 as the variable name.
        z = Variable(UInt, random_string(3))

        reduction_variable = variables.copy()
        reduction_variable.append(z)

        reduction_interval = intervals.copy()
        if isinstance(mat2, Matrix):
            reduction_interval.append(mat2.intervals[0])
        else:
            reduction_interval.append(mat2.domain[0])

        red_dom = (reduction_variable, reduction_interval)
        name = 'redn_prod_' + mat1.name + '_' + mat2.name

        # NOTE: This is the constraint given to isl, as a promise, that
        # the parameters of the dimension in which matrices are reduced
        # are equal. The bounds check pass will fail if we don't supply
        # this information.
        if isinstance(mat2, Matrix) and isinstance(mat1, Matrix):
            cond = Condition(mat1.dimensions[1], "==", mat2.dimensions[0])
        elif isinstance(mat2, Function) and isinstance(mat1, Matrix):
            cond = Condition(mat1.intervals[1].upperBound, "==", mat2.domain[0].upperBound)
        elif isinstance(mat2, Matrix) and isinstance(mat1, Function):
            cond = Condition(mat2.intervals[1].upperBound, "==", mat1.domain[0].upperBound)
        elif isinstance(mat2, Function) and isinstance(mat1, Function):
            cond = Condition(mat2.domain[1].upperBound, "==", mat1.domain[0].upperBound)

        variables1 = []
        variables2 = []
        variables1 = variables1.__add__(variables[0:variables.__len__() - 1])
        variables1.append(z)
        variables2.append(z)
        variables2 = variables2.__add__(variables[1:variables.__len__()])

        matmul_as_reduction = Reduction(var_dom, red_dom, mat1.typ, name)
        matmul_as_reduction.defn = [Case(cond, Reduce(matmul_as_reduction(*variables),
                                                      mat1(*variables1) * mat2(*variables2),
                                                      Op.Sum))]
        matmul_as_reduction.is_mat_func = True
        matmul_as_reduction.dimensions = dimensions
        matmul_as_reduction.reductionDimensions = redn_dimensions

        return matmul_as_reduction

class Wave(Function):
    def __init__(self, _typ, _name, _len, _var=None):
        _len = Value.numericToValue(_len)
        assert(isinstance(_len, AbstractExpression))
        self._len = _len

        assert _typ in [Double, Complex]
        self._typ = _typ

        self._name = _name
        self._var = _var if _var is not None else Variable(UInt, "_" + _name + str(0))

        variables = [self._var]
        self._variables = variables
        intervals = [Interval(UInt, 0, _len - 1)]
        Function.__init__(self, (variables, intervals), _typ, _name)

    @property
    def length(self):
        return self._len

    __len__ = length

    @property
    def type(self):
        return self._typ

    @property
    def variables(self):
        return self._variables

    @property
    def isInput(self):
        return self.defn == []

    def __str__(self):
        return self._name.__str__() + "(" + self._len.__str__() + ", " \
               + "type = " + str(self._typ) + ")"

    def clone(self):
        var = [v.clone() for v in self._variables]
        length = self.length
        newFunc = Wave(self._typ, self._name, length, var[0])
        if not self.isInput:
            newBody = [c.clone() for c in self._body]
            newFunc.defn = newBody
        return newFunc

    def convolve(self, other, out_name):
        assert isinstance(other, Wave)
        assert self._typ == other._typ

        M = self._len
        N = other._len

        in_var = self._variables[0]
        out_var = Variable(Int, "_" + out_name + str(0))
        out_typ = self._typ

        interval1 = Interval(UInt, 0, M-1)
        interval2 = Interval(Int, 0, M+N-2)

        convolution = Reduction(([out_var], [interval2]), \
                        ([out_var, in_var], [interval2, interval1]), \
                        out_typ, out_name)
        c = Condition(out_var - in_var, '<', N) \
                                & Condition(out_var - in_var, '>=', 0)
        convolution.defn = [ Case(c, Reduce(convolution(out_var), \
                                self(in_var) * other(out_var - in_var), \
                                Op.Sum)) ]
        return convolution

    def correlate(self, other, out_name):
        assert isinstance(other, Wave)
        assert self._typ == other._typ

        M = self._len
        N = other._len

        in_var = self._variables[0]
        out_var = Variable(Int, "_" + out_name + str(0))
        out_typ = self._typ

        interval1 = Interval(UInt, 0, M-1)
        interval2 = Interval(Int, 0, M+N-2)

        correlation = Reduction(([out_var], [interval2]), \
                        ([out_var, in_var], [interval2, interval1]), \
                        out_typ, out_name)
        c = Condition(out_var - in_var, '<', N) \
                                & Condition(out_var - in_var, '>=', 0)
        if out_typ is Complex:
            correlation.defn = [ Case(c, Reduce(correlation(out_var), \
                                self(in_var) \
                                * Conj(other(in_var + N - 1 - out_var)), \
                                Op.Sum)) ]
        else:
            correlation.defn = [ Case(c, Reduce(correlation(out_var), \
                                self(in_var) \
                                * other(in_var + N - 1 - out_var), \
                                Op.Sum)) ]
        return correlation

    def fftconvolve(self, other, out_name):
        assert isinstance(other, Wave)
        assert self._typ == other._typ

        M = self._len
        N = other._len

        in_var = self._variables[0]
        in_var_oth = other._variables[0]
        out_var = Variable(UInt, "_" + out_name + str(0))
        out_typ = self._typ

        zp_name = "_" + self._name + "_zero_pad"
        self_zero_pad = Wave(out_typ, zp_name, M+N-1, in_var)
        cond1 = Condition(in_var, '<', M)
        cond2 = Condition(in_var, '>=', M)
        self_zero_pad.defn = [ Case(cond1, self(in_var)), \
                                                        Case(cond2, 0) ]

        zp_name_other = "_" + other._name + "_zero_pad"
        other_zero_pad = Wave(out_typ, zp_name_other, M+N-1, in_var_oth)
        cond3 = Condition(in_var_oth, '<', N)
        cond4 = Condition(in_var_oth, '>=', N)
        other_zero_pad.defn = [ Case(cond3, other(in_var_oth)), \
                                                        Case(cond4, 0) ]

        fft_name = zp_name + "_fft"
        self_zp_fft = self_zero_pad.fft(fft_name)

        fft_name_other = zp_name_other + "_fft"
        other_zp_fft = other_zero_pad.fft(fft_name_other)

        mult_name = fft_name + fft_name_other + "_mult"
        mult_interval = self_zp_fft.domain[0]
        mult_len = mult_interval.upperBound - mult_interval.lowerBound \
                                                                    + 1
        szf_ozf_mult = Wave(Complex, mult_name, mult_len, in_var)
        szf_ozf_mult.defn = [ self_zp_fft(in_var) * other_zp_fft(in_var) ]

        sc_name = "_" + out_name + "_scaled"
        ri = out_typ is not Complex
        scaled_convolution = szf_ozf_mult.ifft(sc_name, M+N-1, \
                                                        real_input = ri)

        convolution = Wave(out_typ, out_name, M+N-1, out_var)
        convolution.defn = [ scaled_convolution(out_var) \
                                            / Cast(Double, M + N - 1) ]
        return convolution

    def lfilter(self, b, a, out_name):
        assert isinstance(b, Wave)
        assert isinstance(a, Wave)
        assert b._typ is Double and a._typ is Double

        L = self._len
        M = b._len
        N = a._len

        in_var = self._variables[0]
        out_var = Variable(Int, "_" + out_name + str(0))
        out_typ = self._typ

        b_norm_name = "_" + b._name + "_norm_" + out_name
        b_var = b._variables[0]
        b_norm = Wave(Double, b_norm_name, M, b_var)
        b_norm.defn = [ Case(Condition(N, '>', 0), b(b_var) / a(0)) ]

        a_norm_name = "_" + a._name + "_norm_" + out_name
        a_var = a._variables[0]
        a_norm = Wave(Double, a_norm_name, N, a_var)
        a_norm.defn = [ a(a_var) / a(0) ]

        sig_interval = Interval(Int, 0, L-1)
        coeff_interval = Interval(UInt, 0, M+N-1)

        filtered_sig = Reduction(([out_var], [sig_interval]), \
                ([out_var, in_var], [sig_interval, coeff_interval]), \
                out_typ, out_name)
        cond1 = Condition(out_var - in_var, '>=', 0) \
                & Condition(in_var, '<', M)
        cond2 = Condition(in_var, '>', 0) \
                & Condition(out_var - in_var, '>=', 0) \
                & Condition(in_var, '<', N)
        filtered_sig.defn = [ Case(cond1, Reduce(filtered_sig(out_var), \
                                self(out_var - in_var) * b_norm(in_var), \
                                Op.Sum)), \
                              Case(cond2, Reduce(filtered_sig(out_var), \
                                filtered_sig(out_var - in_var) \
                                * -a_norm(in_var), \
                                Op.Sum)) ]
        return filtered_sig

    def hilbert(self, out_name):
        assert self._typ is Double

        N = self._len

        in_var = self._variables[0]

        sc_name = "_" + self._name + "_complex"
        sig_complex = Wave(Complex, sc_name, N, in_var)
        sig_complex.defn = [ Cast(Complex, self(in_var)) ]

        sc_fft_name = sc_name + "_fft"
        sig_complex_fft = sig_complex.fft(sc_fft_name)

        h_name = "_" + out_name + "_h"
        h = Wave(Double, h_name, N, in_var)
        cond1 = Condition(in_var, '==', 0)
        cond2 = Condition(in_var, '>', 0) & Condition(2*in_var, '<=', N)
        cond3 = Condition(2*in_var, '>', N) & Condition(in_var, '<', N)
        h.defn = [ Case(cond1, 1), \
                    Case(cond2, Min(2, Cast(Int, 1 + N - 2*in_var))), \
                    Case(cond3, 0) ]

        sc_fft_h_mult_name = sc_fft_name + h_name + "_mult"
        sc_fft_h_mult = Wave(Complex, sc_fft_h_mult_name, N, in_var)
        sc_fft_h_mult.defn = [ sig_complex_fft(in_var) * h(in_var) ]

        scaled_sig_a_name = "_" + out_name + "_scaled"
        scaled_sig_a = sc_fft_h_mult.ifft(scaled_sig_a_name, \
                                                    real_input=False)

        sig_a = Wave(Complex, out_name, N, in_var)
        sig_a.defn = [ scaled_sig_a(in_var) / Cast(Double, N) ]
        return sig_a

    def upfirdn(self, h, out_name, up=1, down=1):
        assert isinstance(h, Wave)
        assert h._typ is Double

        ut = getType(up)
        dt = getType(down)

        assert (ut is Int or ut is UInt) and (dt is Int or dt is UInt)

        M = h._len
        N = self._len

        in_var = self._variables[0]
        out_var = Variable(Int, "_" + out_name + str(0))
        out_typ = self._typ

        sig_up_name = "_" + self._name + "_up"
        sig_up = Wave(out_typ, sig_up_name, N * up, in_var)
        cond1 = Condition(in_var % up, '==', 0)
        cond2 = Condition(in_var % up, '!=', 0)
        sig_up.defn = [ Case(cond1, self(in_var / up)), Case(cond2, 0) ]

        suf_interval = Interval(Int, 0, N*up+M-2)
        coeff_interval = Interval(UInt, 0, M-1)

        su_fir_name = sig_up_name + "_fir"
        sig_up_fir = Reduction(([out_var], [suf_interval]), \
                    ([out_var, in_var], [suf_interval, coeff_interval]), \
                    out_typ, su_fir_name)
        if M == 1:
            to_mult = (sig_up_fir(out_var) + 1) // (sig_up_fir(out_var) + 1)
        else:
            to_mult = 1
        cond3 = Condition(out_var - in_var, '>=', 0) \
                & Condition(out_var - in_var, '<', N*up)
        sig_up_fir.defn = [ Case(cond3, Reduce(sig_up_fir(out_var), \
                                to_mult * sig_up(out_var - in_var) * h(in_var), \
                                Op.Sum)) ]

        suf_down = Wave(out_typ, out_name, (N*up+M+down-2)/down, in_var)
        suf_down.defn = [ sig_up_fir(in_var * down) ]
        return suf_down

    def low_pass(self, cutoff, out_name, factor=0):
        ct = getType(cutoff)
        assert ct is Double or ct is Float

        N = self._len

        in_var = self._variables[0]
        out_typ = self._typ

        hs_name = "_" + self._name + "_fft"
        hs = self.fft(hs_name)

        fs_name = hs_name + "freq"
        ri = out_typ is not Complex
        fs = Wave.fftfreq(N, fs_name, real_input=ri)

        hs_lp_name = hs_name + "_low_pass"
        hs_lp_interval = hs.domain[0]
        hs_lp_len = hs_lp_interval.upperBound \
                                        - hs_lp_interval.lowerBound + 1
        hs_lp = Wave(Complex, hs_lp_name, hs_lp_len, in_var)
        cond1 = Condition(Abs(fs(in_var)), '>', cutoff)
        cond2 = Condition(Abs(fs(in_var)), '<=', cutoff)
        hs_lp.defn = [ Case(cond1, hs(in_var) * factor), \
                                            Case(cond2, hs(in_var)) ]

        scaled_lp_name = "_" + out_name + "_scaled"
        scaled_lp = hs_lp.ifft(scaled_lp_name, N, real_input=ri)

        lp = Wave(out_typ, out_name, N, in_var)
        lp.defn = [ scaled_lp(in_var) / Cast(Double, N) ]
        return lp

    def high_pass(self, cutoff, out_name, factor=0):
        ct = getType(cutoff)
        assert ct is Double or ct is Float

        N = self._len

        in_var = self._variables[0]
        out_typ = self._typ

        hs_name = "_" + self._name + "_fft"
        hs = self.fft(hs_name)

        fs_name = hs_name + "freq"
        ri = out_typ is not Complex
        fs = Wave.fftfreq(N, fs_name, real_input=ri)

        hs_hp_name = hs_name + "_high_pass"
        hs_hp_interval = hs.domain[0]
        hs_hp_len = hs_hp_interval.upperBound \
                                        - hs_hp_interval.lowerBound + 1
        hs_hp = Wave(Complex, hs_hp_name, hs_hp_len, in_var)
        cond1 = Condition(Abs(fs(in_var)), '<', cutoff)
        cond2 = Condition(Abs(fs(in_var)), '>=', cutoff)
        hs_hp.defn = [ Case(cond1, hs(in_var) * factor), \
                                            Case(cond2, hs(in_var)) ]

        scaled_hp_name = "_" + out_name + "_scaled"
        scaled_hp = hs_hp.ifft(scaled_hp_name, N, real_input=ri)

        hp = Wave(out_typ, out_name, N, in_var)
        hp.defn = [ scaled_hp(in_var) / Cast(Double, N) ]
        return hp

    def band_stop(self, low_cutoff, high_cutoff, out_name, factor=0):
        lct = getType(low_cutoff)
        hct = getType(high_cutoff)
        assert (lct is Double or lct is Float) \
                                    and (hct is Double or hct is Float)

        N = self._len

        in_var = self._variables[0]
        out_typ = self._typ

        hs_name = "_" + self._name + "_fft"
        hs = self.fft(hs_name)

        fs_name = hs_name + "freq"
        ri = out_typ is not Complex
        fs = Wave.fftfreq(N, fs_name, real_input=ri)

        hs_bs_name = hs_name + "_band_stop"
        hs_bs_interval = hs.domain[0]
        hs_bs_len = hs_bs_interval.upperBound \
                                        - hs_bs_interval.lowerBound + 1
        hs_bs = Wave(Complex, hs_bs_name, hs_bs_len, in_var)
        cond1 = Condition(Abs(fs(in_var)), '>', low_cutoff) \
                        & Condition(Abs(fs(in_var)), '<', high_cutoff)
        cond2 = Condition(Abs(fs(in_var)), '<=', low_cutoff) \
                        | Condition(Abs(fs(in_var)), '>=', high_cutoff)
        hs_bs.defn = [ Case(cond1, hs(in_var) * factor), \
                                            Case(cond2, hs(in_var)) ]

        scaled_bs_name = "_" + out_name + "_scaled"
        scaled_bs = hs_bs.ifft(scaled_bs_name, N, real_input=ri)

        bs = Wave(out_typ, out_name, N, in_var)
        bs.defn = [ scaled_bs(in_var) / Cast(Double, N) ]
        return bs

    def freqz(self, out_names):
        assert self._typ is Double
        assert isinstance(out_names, tuple)
        assert len(out_names) == 2

        N = self._len
        in_var = self._variables[0]

        w_name = out_names[0]
        h_name = out_names[1]
        w_typ = Double
        h_typ = Complex

        out_var = Variable(UInt, "_" + w_name + "_" + h_name + str(0))
        out_len = 512

        w = Wave(w_typ, w_name, out_len, out_var)
        w.defn = [ Pi() / out_len * out_var ]

        freq_int = Interval(UInt, 0, out_len-1)
        coeff_int = Interval(UInt, 0, N-1)

        h = Reduction(([out_var], [freq_int]), \
                        ([out_var, in_var], [freq_int, coeff_int]), \
                        h_typ, h_name)
        h.defn = [ Reduce(h(out_var), \
                      self(in_var) \
                      * Exp(Cast(Complex, -1.0j * w(out_var) * in_var)), \
                      Op.Sum) ]

        return w, h

    def interp_fft(self, r, out_name):
        rt = getType(r)
        assert (rt is Int or rt is UInt)

        N = self._len

        in_var = self._variables[0]
        out_var = Variable(UInt, "_" + out_name + str(0))
        out_typ = self._typ
        out_len = N * r

        if self._typ is Complex:
            sig_complex = self
        else:
            sc_name = "_" + self._name + "_complex"
            sig_complex = Wave(Complex, sc_name, N, in_var)
            sig_complex.defn = [ Cast(Complex, self(in_var)) ]

        sc_fft_name = sc_name + "_fft"
        sig_complex_fft = sig_complex.fft(sc_fft_name)

        Y_name = sc_name + "_zero_inserted"
        Y = Wave(Complex, Y_name, out_len, out_var)
        cond1 = Condition(2 * out_var, '<', N)
        cond2 = Condition(out_var, '>=', (N+1)//2) \
                            & Condition(N - out_len + out_var, '<', (N+2)//2)
        cond3 = Condition(N - out_len + out_var, '>=', (N+1)//2)
        Y.defn = [ Case(cond1, sig_complex_fft(out_var)), \
                   Case(cond2, 0), \
                   Case(cond3, sig_complex_fft(N - out_len + out_var)) ]

        ys_name = "_" + out_name + "_scaled"
        y_scaled = Y.ifft(ys_name, out_len, real_input=False)

        y = Wave(out_typ, out_name, out_len, out_var)
        if out_typ is Complex:
            y.defn = [ y_scaled(out_var) / Cast(Double, N) ]
        else:
            y.defn = [ Real(y_scaled(out_var)) / Cast(Double, N) ]

        return y

    @classmethod
    def get_window(cls, window, N, out_name):
        if isinstance(window, tuple):
            assert len(window) == 2
            window, beta = window[0], window[1]
        assert isinstance(window, str)

        out_var = Variable(UInt, "_" + out_name + str(0))

        order = Cast(Double, N-1)
        alpha = 0.16
        win = Wave(Double, out_name, N, out_var)

        if window == 'hamming':
            win.defn = [ 0.54 - 0.46*Cos((2*Pi()*out_var)/order) ]
        elif window == 'hann' or window == 'hanning':
            win.defn = [ 0.5 - 0.5*Cos((2*Pi()*out_var)/order) ]
        elif window == 'bartlett':
            win.defn = [ 1.0 - Abs(2*out_var/order - 1) ]
        elif window == 'blackman':
            win.defn = [ (1-alpha)/2 - 0.50*Cos((2*Pi()*out_var)/order) \
                            + (alpha/2)*Cos((4*Pi()*out_var)/order) ]
        elif window == 'nuttall':
            win.defn = [ 0.355768 - 0.487396*Cos(2*Pi()*out_var/order) \
                                + 0.144232*Cos(4*Pi()*out_var/order) \
                                - 0.012604*Cos(6*Pi()*out_var/order) ]
        elif window == 'blackman-harris':
            win.defn = [ 0.35875 - 0.48829*Cos(2*Pi()*out_var/order) \
                                + 0.14128*Cos(4*Pi()*out_var/order) \
                                - 0.01168*Cos(6*Pi()*out_var/order) ]
        elif window == 'blackman-nuttall':
            win.defn = [ 0.3635819 - 0.4891775*Cos(2*Pi()*out_var/order) \
                                + 0.1365995*Cos(4*Pi()*out_var/order) \
                                - 0.0106411*Cos(6*Pi()*out_var/order) ]
        elif window == 'flat top':
            win.defn = [ 1 - 1.93*Cos(2*Pi()*out_var/order) \
                                    + 1.29*Cos(4*Pi()*out_var/order) \
                                    - 0.388*Cos(6*Pi()*out_var/order) \
                                    + 0.028*Cos(8*Pi()*out_var/order) ]
        elif window == 'rectangular' or window == 'dirichlet' \
                or window == 'boxcar':
            win.defn = [ 1 ]
        elif window == 'triang':
            win.defn = [ 1 - Abs((2*out_var - order) / (N + N % 2)) ]
        elif window == 'parzen':
            cond1 = Condition(out_var, '<=', (N)/4) \
                                    | Condition(out_var, '>=', 3*(N+2)/4-1)
            cond2 = Condition(4*out_var, '>', (N-3)) \
                                    & Condition(4*out_var, '<=', 3*(N-1)+1)
            win.defn = [ Case(cond1, 2 * (1 - Abs(order - 2.0*out_var) / N) \
                                    * (1 - Abs(order - 2.0*out_var) / N) \
                                    * (1 - Abs(order- 2.0*out_var) / N)), \
                         Case(cond2, 1 - 6 \
                                    * (Abs(order - 2.0*out_var) / N) \
                                    * (Abs(order - 2.0*out_var) / N) \
                                    + 6 \
                                    * (Abs(order - 2.0*out_var) / N) \
                                    * (Abs(order - 2.0*out_var) / N) \
                                    * (Abs(order - 2.0*out_var) / N)) ]
        elif window == 'bohman':
            win.defn = [ (1 - Abs(2*out_var/order - 1)) \
                                * Cos(Pi() * Abs(2*out_var/order - 1)) \
                                + 1 / Pi() \
                                * Sin(Pi() * Abs(2*out_var/order - 1)) ]
        elif window == 'barthann':
            win.defn = [ 0.62 - 0.48 * Abs(out_var / order - 0.5) \
                                - 0.38 * Cos(2*Pi()*out_var / order) ]
        elif window == 'kaiser':
            alpha = order / 2.0
            win.defn = [ cls.__i0(beta * Sqrt(1 \
                                        - ((out_var - alpha) / alpha) \
                                        * ((out_var - alpha) / alpha))) \
                                        / cls.__i0(beta) ]
        else:
            assert False,"get_window: unrecognized window type %s" % window

        return win

    @classmethod
    def __i0(cls, x):
        x = Abs(Cast(Double, x))
        y = x / 2.0 - 2.0
        return Select(Condition(x, '<=', 8.0), \
                    Exp(x) * ChbEvl(y, 0), \
                    Exp(x) * ChbEvl(32.0 / x - 2.0, 1) / Sqrt(x))

    @classmethod
    def firwin(cls, N, cutoff, out_name, window='hamming', pass_zero=True):
        out_typ = Double
        out_var = Variable(UInt, "_" + out_name + str(0))

        win_name = "_" + out_name + "_window"
        win = cls.get_window(window, N, win_name)
        win_var = win._variables[0]

        sc_name = "_" + out_name + "_scaled"
        scaled_coeffs = Wave(Double, sc_name, N, out_var)
        middle = (N - 1) // 2
        cond1 = Condition(out_var, '==', middle)

        scalar_int = Interval(UInt, 0, 0)
        coeffs_int = Interval(UInt, 0, N-1)

        cs_name = sc_name + "_sum"
        coeffs_sum = Reduction(([win_var], [scalar_int]), \
                        ([win_var, out_var], [scalar_int, coeffs_int]), \
                        Double, cs_name)

        if isinstance(cutoff, tuple):
            assert len(cutoff) == 2
            FL = cutoff[0]
            FH = cutoff[1]
            flt = getType(FL)
            fht = getType(FH)
            assert (flt is Double or flt is Float) \
                                    and (fht is Double or fht is Float)

            if pass_zero:
                scaled_coeffs.defn = [ Select(cond1, \
                                (1 - (FH - FL)) * win(out_var), \
                                (Sin((out_var - middle) * Pi() * FL) \
                                - Sin((out_var - middle) * Pi() * FH)) \
                                / ((out_var - middle) * Pi()) \
                                * win(out_var)) ]
                coeffs_sum.defn = [ Reduce(coeffs_sum(win_var), \
                                    scaled_coeffs(out_var), Op.Sum) ]
            else:
                scaled_coeffs.defn = [ Select(cond1,
                                (FH - FL) * win(out_var), \
                                (Sin((out_var - middle) * Pi() * FH) \
                                - Sin((out_var - middle) * Pi() * FL)) \
                                / ((out_var - middle) * Pi()) \
                                * win(out_var)) ]
                coeffs_sum.defn = [ Reduce(coeffs_sum(win_var), \
                        scaled_coeffs(out_var) * Cos((out_var - middle) \
                        * (Pi() * FH + Pi() * FL) * 0.5), Op.Sum) ]
        else:
            F = cutoff
            ft = getType(F)
            assert ft is Double or ft is Float

            if pass_zero:
                scaled_coeffs.defn = [ Select(cond1, \
                                F * win(out_var), \
                                Sin((out_var - middle) * Pi() * F) \
                                / ((out_var - middle) * Pi()) \
                                * win(out_var)) ]
                coeffs_sum.defn = [ Reduce(coeffs_sum(win_var), \
                                    scaled_coeffs(out_var), Op.Sum) ]
            else:
                scaled_coeffs.defn = [ Select(cond1,
                                (1 - F) * win(out_var), \
                                -Sin((out_var - middle) * Pi() * F) \
                                / ((out_var - middle) * Pi()) \
                                * win(out_var)) ]
                coeffs_sum.defn = [ Reduce(coeffs_sum(win_var), \
                        scaled_coeffs(out_var) * Cos((out_var - middle) \
                        * Pi()), Op.Sum) ]

        fir_coeffs = Wave(out_typ, out_name, N, out_var)
        fir_coeffs.defn = [ scaled_coeffs(out_var) / coeffs_sum(0) ]
        return fir_coeffs

    @classmethod
    def kaiserord(cls, ripple, width):
        rt = getType(ripple)
        wt = getType(width)
        assert (rt is Double or rt is Float) \
                                    and (wt is Double or wt is Float)

        A = Abs(ripple)
        beta = cls.kaiser_beta(A)

        numtaps = (A - 7.95) / 2.285 / (Pi() * width) + 1

        numtaps_as_int = Cast(UInt, numtaps)
        return Select(Condition(numtaps, '==', numtaps_as_int), \
                            numtaps_as_int, Cast(UInt, numtaps + 1)), \
                            beta

    @classmethod
    def kaiser_beta(cls, a):
        at = getType(a)
        assert (at is Double or at is Float)

        a = Cast(Double, a)
        cond1 = Condition(a, '>', 50)
        cond2 = Condition(a, '>', 21)
        beta = Select(cond1, 0.1102 * (a - 8.7), \
                            Select(cond2, 0.5842 * Pow((a - 21), 0.4) \
                            + 0.07886 * (a - 21), Cast(Double, 0.0)))
        return beta

    @classmethod
    def fftfreq(cls, n, out_name, real_input=True):
        nt = getType(n)
        assert nt is Int or nt is UInt

        if not real_input:
            return cls.__cfftfreq(n, out_name)

        out_typ = Double
        out_len = n // 2 + 1
        out_var = Variable(UInt, "_" + out_name + str(0))

        fs = Wave(out_typ, out_name, out_len, out_var)
        fs.defn = [ Cast(Double, out_var) / n ]
        return fs

    @classmethod
    def __cfftfreq(cls, n, out_name):
        out_typ = Double
        out_len = n
        out_var = Variable(UInt,  "_" + out_name + str(0))

        fs = Wave(out_typ, out_name, out_len, out_var)
        fs.defn = [ Select(Condition(n - out_var, '<=', n // 2), \
                    out_var - n, Cast(Int, out_var)) / Cast(Double, n) ]
        return fs

    def fft(self, out_name):
        if self._typ is Complex:
            return self.__cfft(out_name)

        out_type = Complex
        out_len = self._len // 2 + 1

        out_vars = [Variable(UInt, "_" + out_name + str(0))]
        in_vars = self._variables

        out_intervals = [Interval(UInt, 0, out_len - 1)]
        in_intervals = [Interval(UInt, 0, self._len - 1)]

        out_wave = Reduction((out_vars, out_intervals), ([*out_vars, *in_vars], [*out_intervals, *in_intervals]), out_type, out_name)
        out_wave.defn = [ Reduce(out_wave(*out_vars), \
                                 self(*in_vars) * Exp(Cast(Complex, -2 * Pi() * 1.0j * out_vars[0] * in_vars[0] / self._len)), \
                                 Op.Sum) ]
        out_wave.reductionDimensions = [self._len]

        return out_wave

    def __cfft(self, out_name):
        out_type = Complex
        out_len = self._len

        out_vars = [Variable(UInt, "_" + out_name + str(0))]
        in_vars = self._variables

        out_intervals = [Interval(UInt, 0, out_len - 1)]

        out_wave = Reduction((out_vars, out_intervals), ([*out_vars, *in_vars], [*out_intervals, *out_intervals]), out_type, out_name)
        out_wave.defn = [ Reduce(out_wave(*out_vars), \
                                 self(*in_vars) * Exp(Cast(Complex, -2 * Pi() * 1.0j * out_vars[0] * in_vars[0] / self._len)), \
                                 Op.Sum) ]
        out_wave.reductionDimensions = [out_len]

        return out_wave

    def ifft(self, out_name, _out_len=None, real_input=True):
        assert self._typ == Complex

        if not real_input:
            return self.__cifft(out_name)

        out_type = Double
        out_len = 2 * (self._len - 1) if _out_len is None else _out_len

        out_vars = [Variable(UInt, "_" + out_name + str(0))]
        in_vars = self._variables

        out_intervals = [Interval(UInt, 0, out_len - 1)]

        cond1 = Condition(2*in_vars[0], '<=', out_len)
        cond2 = Condition(2*in_vars[0], '>', out_len)

        out_wave = Reduction((out_vars, out_intervals), ([*out_vars, *in_vars], [*out_intervals, *out_intervals]), out_type, out_name)
        out_wave.defn = [ Case(cond1, Reduce(out_wave(*out_vars), \
                                 Real((Conj(self(*in_vars)) * Exp(Cast(Complex, -2 * Pi() * 1.0j * out_vars[0] * in_vars[0] / out_len)))), \
                                 Op.Sum)), \
                          Case(cond2, Reduce(out_wave(*out_vars), \
                                 Real(((self(out_len - in_vars[0])) * Exp(Cast(Complex, -2 * Pi() * 1.0j * out_vars[0] * in_vars[0] / out_len)))), \
                                 Op.Sum)) ]
        out_wave.reductionDimensions = [out_len, _out_len]

        return out_wave

    def __cifft(self, out_name):
        out_type = Complex
        out_len = self._len

        out_vars = [Variable(UInt, "_" + out_name + str(0))]
        in_vars = self._variables

        out_intervals = [Interval(UInt, 0, out_len - 1)]

        out_wave = Reduction((out_vars, out_intervals), ([*out_vars, *in_vars], [*out_intervals, *out_intervals]), out_type, out_name)
        out_wave.defn = [ Reduce(out_wave(*out_vars), \
                                 Conj((Conj(self(*in_vars)) * Exp(Cast(Complex, -2 * Pi() * 1.0j * out_vars[0] * in_vars[0] / out_len)))), \
                                 Op.Sum) ]
        out_wave.reductionDimensions = [out_len]

        return out_wave
