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
# expression.py : Manipulation, evaluation and other operations on
#                 Expression ast
#

from __future__ import absolute_import, division, print_function

from expr_ast import *
import constructs
import targetc

def get_affine_var_and_param_coeff(expr, include_params=False):
    expr = Value.numericToValue(expr)

    if (not isAffine(expr, True, False, include_params) or \
            isinstance(expr, Value) or \
            is_constant_expr(expr)):
        return {}
    elif (isinstance(expr, constructs.Variable)):
        return {expr: 1}
    elif (isinstance(expr, AbstractBinaryOpNode)):
        coeff = {}
        left_coeff = get_affine_var_and_param_coeff(expr.left, include_params)
        right_coeff = get_affine_var_and_param_coeff(expr.right, include_params)
        if (expr.op == '+'):
            coeff = dict((n, left_coeff.get(n, 0) + right_coeff.get(n, 0)) \
                             for n in set(left_coeff) | set(right_coeff))
        elif (expr.op == '-'):
            coeff = dict((n, left_coeff.get(n, 0) - right_coeff.get(n, 0)) \
                             for n in set(left_coeff) | set(right_coeff))
        elif (expr.op == '*'):
            left_is_constant = is_constant_expr(expr.left, affine=True)
            right_is_constant = is_constant_expr(expr.right, affine=True)
            #sanity check should be true if the expression is affine
            assert(not (left_is_constant and right_is_constant))

            if (left_is_constant and not right_is_constant):
                coeff = dict((n, get_constant_from_expr(expr.left, \
                                                        affine=True) \
                                 * right_coeff.get(n, 0)) \
                                 for n in set(right_coeff))
            elif(right_is_constant and not left_is_constant):
                coeff = dict((n, get_constant_from_expr(expr.right, \
                                                        affine=True) \
                                 * left_coeff.get(n, 0))
                                 for n in set(left_coeff))
            elif include_params:
                coeff = dict((n, get_constant_from_expr(expr.right, \
                                                        affine=True, include_params=True) \
                                 * left_coeff.get(n, 0))
                                 for n in set(left_coeff) | set(right_coeff))
        elif (expr.op == '/'):
            right_is_constant = is_constant_expr(expr.right, affine=True)
            #sanity check should be true if the expression is affine
            #~ assert(right_is_constant)

            if right_is_constant:
                coeff = dict((n, Fraction(1, get_constant_from_expr(expr.right, \
                                                                affine=True)) \
                                            * left_coeff.get(n, 0)) \
                                            for n in set(left_coeff))
            elif include_params:
                coeff = dict((n, left_coeff.get(n, 0) \
                                    / get_constant_from_expr(expr.right, \
                                                             affine=True, \
                                                             include_params=True)) \
                                            for n in set(left_coeff))
        return coeff
    elif (isinstance(expr, AbstractUnaryOpNode)):
        child_coeff = get_affine_var_and_param_coeff(expr.child, include_params)
        if (expr.op == '-'):
            child_coeff = dict((n, -child_coeff.get(n)) for n in child_coeff)
        return child_coeff
    raise TypeError(type(expr))

def evaluateBinaryOp(leftVal, rightVal, op, affine):
    if op == '/':
        if affine:
            return Fraction(leftVal, rightVal)
        else:
            return leftVal/rightVal
    elif op == '+':
        return leftVal + rightVal
    elif op == '*':
        return leftVal * rightVal
    elif op == '-':
        return leftVal - rightVal
    elif op == '%':
        return leftVal % rightVal
    elif op == '>>':
        return leftVal >> rightVal
    elif op == '<<':
        return leftVal << rightVal
    elif op == '|':
        return leftVal | rightVal
    elif op == '^':
        return leftVal ^ rightVal
    elif op == '&':
        return leftVal & rightVal
    raise TypeError(type(op))

def evaluateUnaryOp(val, op):
    if op == '-':
        return -val
    elif op == '+':
        return val
    raise TypeError(type(val))

def get_constant_from_expr(expr, affine=False, include_params = False, with_div = False):
    expr = Value.numericToValue(expr)
    assert(isinstance(expr, AbstractExpression))
    if (isinstance(expr, Value)):
        if affine:
            assert (expr.typ is Int) or (expr.typ is Rational)
        return expr.value
    elif (isinstance(expr, constructs.Variable)):
        if include_params:
            if isinstance(expr, constructs.Parameter):
                if affine:
                    assert (expr.typ is Int) or (expr.typ is Rational)
                return expr.clone()
        return 0
    elif (isinstance(expr, constructs.Reference)):
        return 0    
    elif (isinstance(expr, AbstractBinaryOpNode)):
        if expr.op == '/' and with_div:
            leftConst = get_constant_from_expr(expr.left, affine, False, with_div)
            rightConst = get_constant_from_expr(expr.right, affine, True, with_div)
        else:
            leftConst = get_constant_from_expr(expr.left, affine, include_params, with_div)
            rightConst = get_constant_from_expr(expr.right, affine, include_params, with_div)
        return evaluateBinaryOp(leftConst, rightConst, expr.op, affine)
    elif (isinstance(expr, AbstractUnaryOpNode)):
        childConst = get_constant_from_expr(expr.child, affine, include_params, with_div)
        return evaluateUnaryOp(childConst, expr.op)
    elif (isinstance(expr,
                     (constructs.Select, constructs.Cast, InbuiltFunction))):
        return 0
    raise TypeError(type(expr))

def is_constant_expr(expr, affine = False):
    expr = Value.numericToValue(expr)
    assert(isinstance(expr, AbstractExpression))
    if (isinstance(expr, Value)):
        if affine:
            return (expr.typ is Int) or (expr.typ is Rational)
        return True 
    elif (isinstance(expr, constructs.Variable)):
        return False
    elif (isinstance(expr, constructs.Reference)):
        return False    
    elif (isinstance(expr, AbstractBinaryOpNode)):
        return (is_constant_expr(expr.left, affine) and 
                is_constant_expr(expr.right, affine))
    elif (isinstance(expr, AbstractUnaryOpNode)):
        return is_constant_expr(expr.child, affine)
    elif (isinstance(expr,
                    (constructs.Select, InbuiltFunction, constructs.Cast))):
        return False
    raise TypeError(type(expr))

def simplify_expr(expr):
    expr = Value.numericToValue(expr)
    assert(isinstance(expr, AbstractExpression))
    if (isinstance(expr, Value)):
        return expr.clone()
    elif (isinstance(expr, constructs.Variable)):
        return expr.clone()
    elif (isinstance(expr, constructs.Reference)):
        simple_args = []
        for arg in expr.arguments:
            simple_args.append(simplify_expr(arg))
        # Equivalent to cloning
        return expr.objectRef(*simple_args)
    elif (isinstance(expr, AbstractBinaryOpNode) or
          isinstance(expr, AbstractUnaryOpNode)):
        if (isAffine(expr, include_div=False)):
            coeff = get_affine_var_and_param_coeff(expr)
            variables = list(set(expr.collect(constructs.Variable)))
            params = list(set(expr.collect(constructs.Parameter)))
            simple_expr = get_constant_from_expr(expr)
            for var in variables:
                if (coeff[var] == 1):
                    simple_expr = simple_expr + var
                elif (coeff[var] == -1):
                    simple_expr = simple_expr - var
                else:
                    simple_expr = simple_expr + coeff[var] * var
            for param in params:
                if (coeff[param] == 1):
                    simple_expr = simple_expr + param
                elif (coeff[param] == -1):
                    simple_expr = simple_expr - param
                else:
                    simple_expr = simple_expr + coeff[param] * param
            return Value.numericToValue(simple_expr)
        else:
            return expr.clone()
    elif (isinstance(expr,
                     (constructs.Select, constructs.Cast, InbuiltFunction))):
        # Some simplification can be done but ignoring for now
        return expr.clone()
    raise TypeError(type(expr))

def substitute_refs(expr, ref_to_expr_map):
    expr = Value.numericToValue(expr)
    assert(isinstance(expr, AbstractExpression))
    if (isinstance(expr, Value)):
        return expr.clone()
    elif (isinstance(expr, constructs.Variable)):
        return expr.clone()
    elif (isinstance(expr, constructs.Reference)):
        if (expr in ref_to_expr_map):
            ref_vars = expr.objectRef.variables
            var_to_expr_map = {}
            assert len(expr.arguments) == len(ref_vars)
            for i in range(0, len(ref_vars)):
                var_to_expr_map[ref_vars[i]] = expr.arguments[i]
            # Equivalent to cloning
            return substitute_vars(ref_to_expr_map[expr], var_to_expr_map)
        else:
            return expr.clone()
    elif (isinstance(expr, AbstractBinaryOpNode)):
        left = substitute_refs(expr.left, ref_to_expr_map)
        right = substitute_refs(expr.right, ref_to_expr_map)
        op = expr.op
        new_expr = AbstractBinaryOpNode(left, right, op)
        return simplify_expr(new_expr)
    elif (isinstance(expr, AbstractUnaryOpNode)):
        child = substitute_refs(expr.child, ref_to_expr_map)
        op = expr.op
        new_expr = AbstractUnaryOpNode(child, op)
        return simplify_expr(new_expr)
    elif (isinstance(expr, InbuiltFunction)):
        expr = expr.clone()
        expr.inline_refs(ref_to_expr_map)
        return expr
    elif (isinstance(expr, (constructs.Select, constructs.Cast))):
        expr = expr.clone()
        expr.inline_refs(ref_to_expr_map)
        return expr
    raise TypeError(type(expr))

def hasReference(expr, ref):
    expr = Value.numericToValue(expr)
    assert(isinstance(expr, AbstractExpression))
    if isinstance(expr, Value):
        return False
    elif isinstance(expr, constructs.Variable):
        return False
    elif isinstance(expr, constructs.Reference):
        return expr.objectRef.name == ref.objectRef.name
    elif isinstance(expr, AbstractBinaryOpNode):
        return hasReference(expr.left, ref) \
            or hasReference(expr.right, ref)
    elif isinstance(expr, AbstractUnaryOpNode):
        return hasReference(expr.child, ref)
    elif isinstance(expr, InbuiltFunction):
        return any([hasReference(arg, ref) for arg in expr.arguments])
    elif isinstance(expr, constructs.Select):
        return hasReference(expr.condition, ref) \
            or hasReference(expr.trueExpression, ref) \
            or hasReference(expr.falseExpression, ref)
    elif isinstance(expr, constructs.Cast):
        return hasReference(expr.expression, ref)
    raise TypeError(type(expr))

def substitute_vars(expr, var_to_expr_map):
    expr = Value.numericToValue(expr)
    assert(isinstance(expr, AbstractExpression))
    if (isinstance(expr, Value)):
        return expr.clone()
    elif (isinstance(expr, constructs.Variable)):
        if expr in var_to_expr_map:
            return var_to_expr_map[expr].clone()
        return expr.clone()
    elif (isinstance(expr, constructs.Reference)):
        num_args = len(expr.arguments)
        args = []
        for i in range(0, num_args):
            args.append(substitute_vars(expr.arguments[i], var_to_expr_map))
        # Equivalent to cloning
        return expr.objectRef(*args)
    elif (isinstance(expr, AbstractBinaryOpNode)):
        left = substitute_vars(expr.left, var_to_expr_map)
        right = substitute_vars(expr.right, var_to_expr_map)
        op = expr.op
        new_expr = AbstractBinaryOpNode(left, right, op)
        return simplify_expr(new_expr)
    elif (isinstance(expr, AbstractUnaryOpNode)):
        child = substitute_vars(expr.child, var_to_expr_map)
        op = expr.op
        new_expr = AbstractUnaryOpNode(child, op)
        return simplify_expr(new_expr)
    elif (isinstance(expr, constructs.Cast)):
        typ = expr.typ
        return \
            constructs.Cast(typ,
                            substitute_vars(expr.expression, var_to_expr_map))
    elif (isinstance(expr, constructs.Select)):
        new_cond = substitute_vars(expr.condition, var_to_expr_map)
        new_true = substitute_vars(expr.trueExpression, var_to_expr_map)
        new_false = substitute_vars(expr.falseExpression, var_to_expr_map)
        return constructs.Select(new_cond, new_true, new_false)
    elif (isinstance(expr, InbuiltFunction)):
        expr = expr.clone()
        expr.substitute_vars(var_to_expr_map)
        return expr
    raise TypeError(type(expr))

def isAffine(expr, include_div = True, include_modulo = False, include_params = False):
    """
    Function to determine if an expression is affine or not. The input is a
    binary expression tree. It recursively checks if the left and right sub
    expressions are affine. Determines if the entire expression is affine
    using the following rules:

    affine +,-,* constant = affine
    constant +,-,* affine = affine
    affine +,- affine  = affine
    affine *,/ affine = non-affine
    non-affine operand always results in a non-affine expression

    Divisions and modulo operators are considered affine if the appropriate
    option is specified.

    This function is meant to work on straight forward expressions it can be
    easily tricked into conservatively saying that the expression is not
    affine. For example -x^3 + x^3 will be non affine.

    Making the expression anaylsis more robust will require integration with
    a symbolic math package.
    """
    expr = Value.numericToValue(expr)
    assert(isinstance(expr, AbstractExpression)
           or isinstance(expr, constructs.Condition))
    if (isinstance(expr, Value)):
        return (expr.typ is Int) or (include_div and (expr.typ is Rational))
    elif (isinstance(expr, constructs.Variable)):
        return True
    elif (isinstance(expr, constructs.Reference)):
        return False
    elif (isinstance(expr, AbstractBinaryOpNode)):
        left_check = isAffine(expr.left, include_div, include_modulo, include_params)
        right_check = isAffine(expr.right, include_div, include_modulo, include_params)
        if (left_check and right_check):
            if (expr.op in ['+','-']):
                return True
            elif(expr.op in ['*']):
                if include_params:
                    return not expr.left.has(constructs.Variable) \
                        or not expr.right.has(constructs.Variable)
                if(not (expr.left.has(constructs.Variable) or \
                        expr.left.has(constructs.Parameter)) or \
                   not (expr.right.has(constructs.Variable) or \
                        expr.right.has(constructs.Parameter))):
                    return True
                else:
                    return False
            elif(include_div and expr.op in ['/']):
                if include_params:
                    return not expr.right.has(constructs.Variable)
                if (not (expr.right.has(constructs.Variable)) and \
                    not (expr.right.has(constructs.Parameter))):
                    return True
                else:
                    return False
            elif(include_modulo and expr.op in ['%']):
                if (not (expr.right.has(constructs.Variable)) and \
                    not (expr.right.has(constructs.Parameter))):
                    return isAffine(expr.left, include_div, False, include_params)
                else:
                    return False
            else:
                return False
        else:
            return False
    elif (isinstance(expr, AbstractUnaryOpNode)):
        return isAffine(expr.child, include_div, include_modulo, include_params)
    elif (isinstance(expr, constructs.Condition)):
        return isAffine(expr.lhs, include_div, include_modulo, include_params) and \
               isAffine(expr.rhs, include_div, include_modulo, include_params)
    elif (isinstance(expr,
                     (constructs.Select, constructs.Cast, InbuiltFunction))):
        return False
    raise TypeError(type(expr))

def getType(expr):
    expr = Value.numericToValue(expr)
    assert(isinstance(expr, AbstractExpression))
    if (isinstance(expr, Value)):
        return expr.typ
    elif (isinstance(expr, constructs.Variable)):
        return expr.typ
    elif (isinstance(expr, constructs.Reference)):
        return expr.objectRef.typ
    elif (isinstance(expr, AbstractBinaryOpNode)):
        left_type = getType(expr.left)
        right_type = getType(expr.right)
        return result_type(left_type, right_type)
    elif (isinstance(expr, AbstractUnaryOpNode)):
        return getType(expr.child)
    elif (isinstance(expr, constructs.Cast)):
        return expr.typ
    elif (isinstance(expr, constructs.Select)):
        true_type = getType(expr.trueExpression)
        false_type = getType(expr.falseExpression)
        assert true_type == false_type
        return true_type
    elif (isinstance(expr, InbuiltFunction)):
        return expr.getType()
    elif (isinstance(expr, targetc.CArrayAccess)):
        return targetc.TypeMap.convert_reverse(expr.array.typ)
    raise TypeError(type(expr))

def cast_ints_to_floats(expr):
    expr = Value.numericToValue(expr)
    assert(isinstance(expr, AbstractExpression))
    if isinstance(expr, Value):
        valType = getType(expr)
        if valType is not Float and valType is not Double \
                                and valType is not Complex:
            return Value.numericToValue(float(expr.value))
        return expr.clone()
    elif isinstance(expr, constructs.Reference):
        cast_args = []
        for arg in expr.arguments:
            cast_args.append(cast_ints_to_floats(arg))
        # Equivalent to cloning
        return expr.objectRef(*cast_args)
    elif isinstance(expr, AbstractBinaryOpNode):
        left = cast_ints_to_floats(expr.left)
        right = cast_ints_to_floats(expr.right)
        op = expr.op
        return AbstractBinaryOpNode(left, right, op)
    elif isinstance(expr, AbstractUnaryOpNode):
        child = cast_ints_to_floats(expr.child)
        op = expr.op
        return AbstractUnaryOpNode(child, op)
    elif isinstance(expr, constructs.Cast):
        typ = expr.typ
        return constructs.Cast(typ, \
                               cast_ints_to_floats(expr.expression))
    elif isinstance(expr, constructs.Select):
        new_cond = cast_ints_to_floats(expr.condition)
        new_true = cast_ints_to_floats(expr.trueExpression)
        new_false = cast_ints_to_floats(expr.falseExpression)
        return constructs.Select(new_cond, new_true, new_false)
    elif isinstance(expr, InbuiltFunction) \
      or isinstance(expr, constructs.Variable):
        exprType = getType(expr)
        if exprType is not Float and exprType is not Double \
                                 and exprType is not Complex:
            return constructs.Cast(Double, expr)
        return expr.clone()
    raise TypeError(type(expr))
