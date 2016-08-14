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
# poly.py : Polyhedral representation of pipeline functions.
#

from __future__ import absolute_import, division, print_function

import math
import time
import islpy as isl

from constructs import *
from expression import *
from utils import *
import pipe
import align_scale as aln_scl

# Static method 'alloc' for isl Id does not allow the user to be
# not None, as of now. We need an exclusive dictionary to map the
# users of an Id to that Id object.
isl_id_user_map = {}

def isl_set_id_user(id_, user):
    isl_id_user_map[id_] = user
    return

def isl_get_id_user(id_):
    return isl_id_user_map[id_]

def isl_alloc_id_for(ctx, name, user):
    name = name+"_"+str(id(user))
    # name = name
    id_ = isl.Id.alloc(ctx, name, None)

    return id_

def optimize_schedule(part_scheds, dependencies):
    # The pluto optimizer can be used to optimize the schedule for
    # comparision.
    pass

def add_constraints_from_list(obj, local_space, constraint_list,
                              constraint_alloc):
    for constr in constraint_list:
        c = constraint_alloc(local_space)

        # find the normalization factor
        m = 1
        for coeff in constr:
            if isinstance(constr[coeff], Fraction):
                den = int(gcd(abs(constr[coeff].denominator), m))
                m = (abs(constr[coeff].denominator) * m)//den
        assert m.denominator == 1
        m = m.numerator

        # normalize
        for coeff in constr:
            if isinstance(constr[coeff], Fraction):
               constr[coeff] = m * constr[coeff]
               assert constr[coeff].denominator == 1
               constr[coeff] = int(constr[coeff].numerator)
            else:
               constr[coeff] = int(m * constr[coeff])

        for coeff in constr:
            dim = coeff[1]
            try:
                if coeff[0] == 'param':
                    if (type(dim) == str):
                        dim = \
                            obj.find_dim_by_name(isl._isl.dim_type.param, dim)
                    c = c.set_coefficient_val(isl._isl.dim_type.param,
                                              dim, constr[coeff])
                elif coeff[0] == 'in':
                    if (type(dim) == str):
                        dim = obj.find_dim_by_name(isl._isl.dim_type.in_, dim)
                    c = c.set_coefficient_val(isl._isl.dim_type.in_,
                                              dim, constr[coeff])
                elif coeff[0] == 'out':
                    if (type(dim) == str):
                        dim = obj.find_dim_by_name(isl._isl.dim_type.out, dim)
                    c = c.set_coefficient_val(isl._isl.dim_type.out,
                                              dim, constr[coeff])
                elif coeff[0] == 'constant':
                    c = c.set_constant_val(constr[coeff])
                else:
                   assert False
            except isl.Error:
                # Ignore this constraint conjunct since the referred dimension
                # is not scheduled in the obj. This happens when we try to add
                # constraint for a dimension that is not at all used by a part.
                # FIXME: isl's find_dim_by_name throws exception on not finding
                # any scheduled dimension. It's better to replace the exception
                # handling with an isl function, if any, to test for the
                # existence of a dimension in that part.
                pass
        obj = obj.add_constraint(c)
    return obj

def add_constraints(obj, ineqs, eqs):

    def add_constraints_for_element(obj, local_space, ineqs, eqs):
        obj = add_constraints_from_list(obj, local_space, ineqs,
                                        isl.Constraint.inequality_alloc)
        obj = add_constraints_from_list(obj, local_space, eqs,
                                        isl.Constraint.equality_alloc)
        return obj

    space = obj.get_space()
    if (isinstance(obj, isl.Map)):
        for bmap in obj.get_basic_maps():
            local_space = bmap.get_local_space()
            obj = add_constraints_for_element(obj, local_space, ineqs, eqs)
    elif (isinstance(obj, isl.Set)):
        for bset in obj.get_basic_sets():
            local_space = bset.get_local_space()
            obj = add_constraints_for_element(obj, local_space, ineqs, eqs)
    elif (isinstance(obj, isl.BasicSet) or
          isinstance(obj, isl.BasicMap)):
        local_space = obj.get_local_space()
        obj = add_constraints_for_element(obj, local_space, ineqs, eqs)
    else:
        assert False

    return obj

def extract_value_dependence(part, ref, ref_poly_dom):
    # Dependencies are calculated between values. There is no storage
    # mapping done yet.
    assert(part.sched)
    deps = []
    access_region = isl.BasicSet.universe(ref_poly_dom.dom_set.get_space())
    part_dom = \
        part.sched.domain().align_params(ref_poly_dom.dom_set.get_space())
    access_region = access_region.align_params(part_dom.get_space())

    rel = isl.BasicMap.from_domain_and_range(part_dom, access_region)
    dim_out = rel.dim(isl._isl.dim_type.out)
    source_dims = [ ('out', i) for i in range(0, dim_out)]
    num_args = len(ref.arguments)

    for i in range(0, num_args):
        arg = ref.arguments[i]
        # If the argument is not affine the dependence reflects that
        # the computation may depend on any value of the referenced object
        if (isAffine(arg)):
            coeff = get_affine_var_and_param_coeff(arg)
            coeff = map_coeff_to_dim(coeff)

            coeff[('constant', 0)] = get_constant_from_expr(arg, affine=True)
            coeff[source_dims[i]] = -1
            rel = add_constraints(rel, [], [coeff])
    if not rel.is_empty():
        deps.append(PolyDep(ref.objectRef, part.comp.func, rel))
    return deps 

class PolyPart(object):
    def __init__(self, _sched, _expr, _pred, _comp,
                 _align, _scale, _level_no, _liveout = True):
        self.sched = _sched
        self.expr = _expr
        self.pred = _pred
        assert isinstance(_comp, pipe.ComputeObject)
        self.comp = _comp
        self.func = self.comp.func

        # Dependencies between values of computation objects
        self.deps = []
        # References made by self
        self._refs = self.collect_part_refs()
        # self dependence
        self._self_dep = self.check_self_dep()
        # Mapping between the input variables to the corresponding 
        # schedule dimension. A full affine schedule will need a 
        # transformation matrix. Currently we only shuffle the 
        # dimension order apart from tiling so a simple dimension
        # alignment vector suffices. This has to be changed to 
        # handle more general cases later.
        self._align = _align
        # Scaling factors for each schedule dimension
        self._scale = _scale
        # Default alignment and scaling factors are set while
        # constructing the polypart. These are changed by the
        # alignment and loop scaling passes. Both these passer
        # attempt to improve locality and uniformize dependencies.
        self._level_no = _level_no

        # tile shape, size, coordinate info
        self.dim_tile_info = {}

        # maps tiled dimensions to their respective scratchpad sizes
        self.dim_scratch_size = {}

        # dimensions marked as parallelizable/vectorizable
        self.parallel_sched_dims = []
        self.vector_sched_dim = []

        # liveness in the group containing the part
        self._is_liveout = _liveout

    @property
    def align(self):
        return list(self._align)
    @property
    def scale(self):
        return list(self._scale)
    @property
    def refs(self):
        return list(self._refs)
    @property
    def is_self_dependent(self):
        return self._self_dep
    @property
    def is_liveout(self):
        return self._is_liveout
    @property
    def level(self):
        return self._level_no

    def set_align(self, align):
        self._align = [i for i in align]
        return

    def set_scale(self, _scale):
        self._scale = [i for i in _scale]
        return

    def is_align_set(self):
        return self._align != [] and self._align != None

    def is_scale_set(self):
        return self._scale != [] and self._scale != None

    def check_self_dep(self):
        obj_refs = [ ref.objectRef for ref in self.refs \
                         if ref.objectRef == self.func ]
        if len(obj_refs) > 0:
            return True
        return False

    def get_size(self, param_estimates):
        # returns the size of the computation that contains this poly part
        size = None
        domain = self.func.domain
        if isinstance(self.func, Reduction):
            domain = self.func.reductionDomain
        for interval in domain:
            subs_size = get_dim_size(interval, param_estimates)
            if is_constant_expr(subs_size):
                if size is not None:
                    size = size * get_constant_from_expr(subs_size)
                else:
                    size = get_constant_from_expr(subs_size)
            else:
                size = '*'
                break

        assert size is not None
        return size

    def collect_part_refs(self):
        refs = self.expr.collect(Reference)
        if (self.pred):
            refs += self.pred.collect(Reference)

        return refs

    def compute_liveness(self):
        self._is_liveout = self.comp.is_liveout
        return

    def set_liveness(self, _is_liveout):
        self._is_liveout = _is_liveout

    def compute_dependence_vector(self, parent_part,
                                  ref, scale_map = None):
        def get_scale(s_map, p, i):
            if s_map is not None:
                return s_map[p][i]
            return p.scale[i]

        num_args = len(ref.arguments)
        dim_out = parent_part.sched.dim(isl._isl.dim_type.out)
        dep_vec = [ NULL for i in range(0, dim_out) ]

        if isinstance(parent_part.func, Reduction):
            for i in range(1, dim_out):
                dep_vec[i] = '*'
            dep_vec[0] = self.level - parent_part.level
            return (dep_vec, parent_part.level)

        # else
        for i in range(0, num_args):
            arg = ref.arguments[i]
            pvar_sched_dim = parent_part.align[i]
            if (isAffine(arg)):
                dom_dim_coeff = \
                    get_domain_dim_coeffs(self.sched, arg)
                param_coeff = \
                    get_param_coeffs(self.sched, arg)
                # Parameter coefficents can also be considered to
                # generate parametric shifts. Yet to be seen.

                # Indexed with multiple variables.
                if (len(dom_dim_coeff) > 1 or \
                    (len(dom_dim_coeff) == 1 and len(param_coeff) >=1)):
                    # Although there are multiple coefficients, if there is
                    # only one variable coefficient and other parametric
                    # coefficients, uniformization can be done with parametric
                    # shifts. Full affine scheduling might be able to find a
                    # way to uniformize dependencies. This has to be further
                    # explored.
                    #assert False
                    dep_vec[pvar_sched_dim] = '*'
                # Indexed with a single variable. This can either be an uniform
                # access or can be uniformized with scaling when possible
                elif len(dom_dim_coeff) == 1 and len(param_coeff) == 0:
                    dim = list(dom_dim_coeff.keys())[0]
                    cvar_sched_dim = self.align[dim]

                    pscale = get_scale(scale_map, parent_part, i)
                    cscale = get_scale(scale_map, self, dim)

                    assert Fraction(pscale).denominator == 1
                    assert Fraction(cscale).denominator == 1

                    if ((cvar_sched_dim == pvar_sched_dim) and \
                        (dom_dim_coeff[dim] * pscale == cscale)):
                        dep_vec[pvar_sched_dim] = \
                                -get_constant_from_expr(arg, affine=True)
                        access_scale = pscale
                        if dep_vec[pvar_sched_dim] > 0:
                            dep_vec[pvar_sched_dim] = \
                                (int(math.ceil(dep_vec[pvar_sched_dim] *
                                               access_scale)))
                        else:
                            dep_vec[pvar_sched_dim] = \
                               (int(math.floor(dep_vec[pvar_sched_dim] *
                                               access_scale)))
                    else:
                        dep_vec[pvar_sched_dim] = '*'
                elif len(dom_dim_coeff) == 0 and len(param_coeff) > 0:
                    #assert False
                    dep_vec[parentVarSchedDim] = '*'
                # Only parametric or Constant access. The schedule in this
                # dimension can be shifted to this point to uniformize the
                # dependence
                # In case the dimension in the parent has a constant size
                # an upper and lower bound on the dependence vector can
                # be computed.
                elif len(dom_dim_coeff) + len(param_coeff) == 0:
                    # offsets should be set here.
                    access_const = get_constant_from_expr(arg, affine = True)
                    p_lower_bound = parent_part.sched.domain().dim_min(i)
                    p_upper_bound = parent_part.sched.domain().dim_max(i)
                    if ((p_lower_bound.is_cst() and
                        p_lower_bound.n_piece() == 1) and
                        (p_upper_bound.is_cst() and
                        p_upper_bound.n_piece() == 1)):

                        pscale = get_scale(scale_map, parent_part, i)

                        low_vec_aff = (p_lower_bound.get_pieces())[0][1]
                        val = low_vec_aff.get_constant_val()
                        assert(val.get_den_val() == 1)
                        low_vec = \
                            int(math.floor((access_const - val.get_num_si()) *
                                           pscale))

                        high_vec_aff = (p_upper_bound.get_pieces())[0][1]
                        val = high_vec_aff.get_constant_val()
                        assert(val.get_den_val() == 1)
                        high_vec = \
                            int(math.ceil((access_const - val.get_num_si()) *
                                          pscale))

                        if high_vec == low_vec:
                            dep_vec[pvar_sched_dim] = high_vec
                        else:
                            # Unpack dependence vectors when this hits
                            #assert False
                            #dep_vec[pvar_sched_dim] = (low_vec, high_vec)
                            dep_vec[pvar_sched_dim] = '*'
                    else:
                        dep_vec[pvar_sched_dim] = '*'
                else:
                    assert False
            else:  # if not isAffine(arg)
                #assert(False)
                dep_vec[pvar_sched_dim] = '*'

        assert dep_vec[0] == NULL
        dep_vec[0] = self.level - parent_part.level
        for i in range(0, dim_out):
            if (dep_vec[i] == NULL):
                dep_vec[i] = 0
        #for i in range(0, dim_out):
        #    if (dep_vec[i] == NULL):
        #        dep_vec[i] = '*'
        #        p_lower_bound = parent_part.sched.range().dim_min(i)
        #        p_upper_bound = parent_part.sched.range().dim_max(i)

        #        c_lower_bound = self.sched.range().dim_min(i)
        #        c_upper_bound = self.sched.range().dim_max(i)

        #        if (c_lower_bound.is_equal(c_upper_bound) and
        #            p_lower_bound.is_equal(p_upper_bound)):
        #            dim_diff = c_upper_bound.sub(p_upper_bound)
        #            if (dim_diff.is_cst() and dim_diff.n_piece() == 1):
        #                aff = (dim_diff.get_pieces())[0][1]
        #                val = aff.get_constant_val()
        #                dep_vec[i] = (val.get_num_si())/(val.get_den_val())
        return (dep_vec, parent_part.level)

    def __str__(self):
        partStr = "Schedule: " + self.sched.__str__() + '\n'\
                  "Expression: " + self.expr.__str__() + '\n'\
                  "Predicate: " + self.pred.__str__() + '\n'
        depstr = ""
        for dep in self.deps:
            depstr = depstr + dep.__str__() + '\n'
        return partStr + depstr

class PolyDomain(object):
    def __init__(self, _dom_set, _comp):
        self._dom_set = _dom_set
        assert isinstance(_comp, pipe.ComputeObject)
        self._comp = _comp

    @property
    def dom_set(self):
        return self._dom_set
    @property
    def comp(self):
        return self._comp

    def set_tuple_id(self, _id):
        self._dom_set.set_tuple_id(_id)
        return

    def __str__(self):
        return "Domain: " + self.dom_set.__str__()

class PolyDep(object):
    def __init__(self, _producer, _consumer, _rel):
        self._producer = _producer
        self._consumer = _consumer
        self._rel = _rel

    @property
    def producer_obj(self):
        return self._producer
    @property
    def consumer_obj(self):
        return self._consumer
    @property
    def rel(self):
        return self._rel

    def __str__(self):
        return self.rel.__str__()

class PolyRep(object):
    """ The PolyRep class is the polyhedral representation of a 
        group. It gives piece-wise domain and schedule for each compute
        object in the group. Polyhedral transformations modify the 
        piece-wise domains as well as the schedules.
    """
    def __init__(self, _ctx, _group, _outputs,
                 _param_constraints):

        assert isinstance(_group, pipe.Group)
        self.group = _group
        self.outputs = _outputs
        self.param_constraints = _param_constraints
        self.ctx = _ctx

        self.poly_parts = {}
        self.poly_doms = {}
        self.polyast = []

        self._var_count = 0
        self._func_count = 0

        # TODO: move the following outside __init__()
        # For now, let this be. Compilation optimizations can come later.

        self.extract_polyrep_from_group(_param_constraints)

    def extract_polyrep_from_group(self, param_constraints):
        # dict: comp_obj -> level_no
        comp_map = self.group.get_ordered_comps
        num_objs = len(comp_map.items())

        # Comute the max dimensionality of the compute objects
        def max_dim(comps):
            dim = 0
            for comp in comps:
                if type(comp.func) == Reduction:
                    dim = max(dim, len(comp.func.reductionVariables))
                    dim = max(dim, len(comp.func.variables))
                elif type(comp.func) == Function or type(comp.func) == Image:
                    dim = max(dim, len(comp.func.variables))
                elif type(comp.func) == TStencil:
                    dim = max(dim, len(comp.func.variables))
            return dim

        dim = max_dim(comp_map)

        # Get all the parameters used in the group compute objects
        grp_params = []
        for comp in comp_map:
            grp_params = grp_params + comp.func.getObjects(Parameter)
        grp_params = list(set(grp_params))

        param_names = [param.name for param in grp_params]

        # Represent all the constraints specified on the parameters relevant
        # to the group.
        context_conds = \
            self.format_param_constraints(param_constraints, grp_params)

        # The [t] is for the stage dimension
        schedule_names = ['_t'] + \
                         [self.getVarName() for i in range(0, dim)]

        # a mapping between compute objects and the function
        # used on them to extract the polyhedral representation
        polyrep_extraction_fn_map = {
            Function: PolyRep.extract_polyrep_from_function,
            Image: PolyRep.extract_polyrep_from_function,
            Reduction: PolyRep.extract_polyrep_from_reduction,
            TStencil: PolyRep.extract_polyrep_from_tstencil

        }

        for comp in comp_map:
            # get the function needed to extract the polyhedral repr
            # for the compute object we have
            extraction_fn = polyrep_extraction_fn_map.get(type(comp.func))
            assert extraction_fn is not None, ("unable to find suitable "
                                               "function to extract "
                                               "polyhedral representation of "
                                               "object.\n"
                                               "Object: %s\n"
                                               "Type: %s" %
                                               (comp.func,
                                                type(comp.func).__name__))

            extraction_fn(self, comp, dim, schedule_names,
                          param_names, context_conds,
                          comp_map[comp] + 1,
                          param_constraints)

    def format_param_constraints(self, param_constraints, grp_params):
        context_conds = []
        grp_params_set = set(grp_params)
        for param_constr in param_constraints:
            # Only consider parameter constraints of parameters
            # given in params.
            params_in_constr = param_constr.collect(Parameter)
            context_add = set(params_in_constr).issubset(grp_params_set)

            # Only add the constraint if it is affine and has no conjunctions.
            # Handling conjunctions can be done but will require more care.
            if context_add and isAffine(param_constr):
                param_constr_conjunct = param_constr.split_to_conjuncts()
                if len(param_constr_conjunct) == 1:
                    context_conds.append(param_constr)
        return context_conds

    def extract_poly_dom_from_comp(self, comp, param_constraints):
        var_names = [ var.name for var in comp.func.variables ]
        dom_map_names = [ name +'\'' for name in var_names ]

        params = []
        for interval in comp.func.domain:
            params = params + interval.collect(Parameter)
        params = list(set(params))
        param_names = [ param.name for param in params ]

        space = isl.Space.create_from_names(self.ctx, in_ = var_names,
                                                      out = dom_map_names,
                                                      params = param_names)
        dom_map = isl.BasicMap.universe(space)
        # Adding the domain constraints
        [ineqs, eqs] = format_domain_constraints(comp.func.domain, var_names)
        dom_map = add_constraints(dom_map, ineqs, eqs)

        param_conds = self.format_param_constraints(param_constraints, params)
        [param_ineqs, param_eqs] = format_conjunct_constraints(param_conds)
        dom_map = add_constraints(dom_map, param_ineqs, param_eqs)

        poly_dom = PolyDomain(dom_map.domain(), comp)
        id_ = isl_alloc_id_for(self.ctx, comp.func.name, poly_dom)
        poly_dom.set_tuple_id(id_)
        isl_set_id_user(id_, poly_dom)

        return poly_dom

    def extract_polyrep_from_function(self, comp, max_dim,
                                      schedule_names, param_names,
                                      context_conds, level_no,
                                      param_constraints):
        self.poly_doms[comp] = \
            self.extract_poly_dom_from_comp(comp, param_constraints)
        sched_map = self.create_sched_space(comp.func.variables,
                                            comp.func.domain,
                                            schedule_names, param_names,
                                            context_conds)
        self.create_poly_parts_from_definition(comp, max_dim, sched_map,
                                               level_no, schedule_names,
                                               comp.func.domain)

    def extract_polyrep_from_reduction(self, comp, max_dim,
                                       schedule_names, param_names,
                                       context_conds, level_no,
                                       param_constraints):
        self.poly_doms[comp] = \
            self.extract_poly_dom_from_comp(comp, param_constraints)
        sched_map = self.create_sched_space(comp.func.reductionVariables,
                                            comp.func.reductionDomain,
                                            schedule_names, param_names,
                                            context_conds)
        self.create_poly_parts_from_definition(comp, max_dim,
                                               sched_map, level_no,
                                               schedule_names,
                                               comp.func.reductionDomain)
        dom_map = self.create_sched_space(comp.func.variables,
                                          comp.func.domain,
                                          schedule_names, param_names,
                                          context_conds)

        # Initializing the reduction earlier than any other function
        self.create_poly_parts_from_default(comp, max_dim, dom_map, level_no,
                                            schedule_names)


    @staticmethod
    def set_map_pluto_names(sched_map):
        """Configure a BasicMap to have PLUTO's naming convention for
        dimensions"""
        sched_map = sched_map.copy()
        sched_map = sched_map.set_tuple_name(isl._isl.dim_type.in_, "S_0")
        sched_map = sched_map.set_tuple_name(isl._isl.dim_type.out, "S_1")

        return sched_map

    @staticmethod
    def add_tstencil_kernel_constraints(isl_ctx, sched_domain, sched_map, comp):
        # Quick note on naming convention between domain and range:
        # The domain will have the input tuple as  [time, x, y, z, ...]
        # The range will have outputs as [_t, _i0, _i1]
        # _t is untouched by us, since it is used later in the pipeline to resolve
        # ordering during grouping.
        # We will associate:
        # time -> _i0 | x -> _i1 | y -> _i2 | ... | (nth_dim) -> _in
        # original_basic_map = sched_map.copy()
        

        if isinstance(sched_map, isl.BasicMap):
            sched_map = isl.Map.from_basic_map(sched_map)

        time_constraint_map = \
            isl.BasicMap.from_domain_and_range(sched_domain.copy(), 
                sched_domain.copy())

        # time_constraint_map is used by everyone else
        # to create relationships between t -> t + 1
        # add constraint corresponding to time = time + 1
        equalities = []
        equalities.append({
            ('constant', 0): -1,
            ('in', 'time'): -1,
            ('out', 'time'): 1,
        })


        time_constraint_map = add_constraints(time_constraint_map,
                                         ineqs=[],
                                         eqs=equalities)

        constraints_union = isl.UnionMap.empty(time_constraint_map.space)

        # build an indexed kernel
        kernel = comp.func._build_indexed_kernel()

        for (indexing_list, weight) in kernel:
            # do not generate constraints if the weight is 0
            if weight == 0:
                continue
            else:
                index_constraint_map = isl.BasicMap.copy(time_constraint_map)
                tstencil_eqs = []
                # for each indexing variable, generate a cone constraint
                # for time (t + 1), from the variable to its output
                for (i, (var_index, origin_dist)) in enumerate(indexing_list):
                    var_name = str(comp.func.variables[i])
                    tstencil_eqs.append({
                        ('constant', 0): -1 * origin_dist,
                        ('in', var_name): 1,
                        ('out', var_name): -1
                    })
                index_constraint_map = add_constraints(index_constraint_map, ineqs=[], eqs=tstencil_eqs)
                index_constraint_map = isl.UnionMap.from_basic_map(index_constraint_map)
                constraints_union = constraints_union.union(index_constraint_map)

        return constraints_union

    def extract_polyrep_from_tstencil(self, comp, max_dim,
                                      schedule_names, param_names,
                                      context_conds, level_no,
                                      param_constraints):



        # add the time dimension to the tstencil
        # schedule_names.append("time")

        # self.poly_doms[comp] = \
        #    self.extract_poly_dom_from_comp(comp, param_constraints)
        # ------
        # EXTRACT POLY DOM FROM COMP

        tstencil = comp.func
        tstencil_vars = [tstencil.time_var] + tstencil.variables
        tstencil_domains = [Interval(Int, 0, tstencil.timesteps)]+ tstencil.domain

        # HACK: we need to forcibly add a variable for our schedule name of "time"
        schedule_names.append(self.getVarName())

        var_names = [var.name for var in  tstencil_vars]
        dom_map_names = [ name +'\'' for name in var_names ]

        params = []
        for interval in tstencil_domains:
            params = params + interval.collect(Parameter)
        # add the TStencil timestep if it's of type parameter
        if isinstance(tstencil.timesteps, Parameter):
            params = params + [tstencil.timesteps]
        else:
            assert(isinstance(tstencil.timesteps, Int))

        params = list(set(params))
        param_names = [ param.name for param in params ]

        space = isl.Space.create_from_names(self.ctx, in_ = var_names,
                                                      out = dom_map_names,
                                                      params = param_names)
        dom_map = isl.BasicMap.universe(space)
        [ineqs, eqs] = format_domain_constraints(tstencil_domains, var_names)
        dom_map = add_constraints(dom_map, ineqs, eqs)

        param_conds = self.format_param_constraints(param_constraints, params)
        [param_ineqs, param_eqs] = format_conjunct_constraints(param_conds)
        dom_map = add_constraints(dom_map, param_ineqs, param_eqs) 
        poly_dom = PolyDomain(dom_map.domain(), comp)
        id_ = isl_alloc_id_for(self.ctx, comp.func.name, poly_dom)
        poly_dom.set_tuple_id(id_)
        isl_set_id_user(id_, poly_dom)

        self.poly_doms[comp] = poly_dom

        # -----
        # CREATE_SCHED_SPACE
        sched_map = self.create_sched_space(tstencil_vars,
                                            tstencil_domains,
                                            schedule_names, param_names,
                                            context_conds)


        # add Tstencil kernel constraints
        # sched_map = self.add_tstenil_kernel_constraints(sched_map, comp)

       # ------
       # CREATE POLY PARTS FOR T STENCIL
        sched_m = sched_map.copy()
        align, scale = \
            aln_scl.default_align_and_scale(sched_m, max_dim, shift=True)

        tstencil_expr = tstencil.get_indexing_expr()
        assert(isinstance(tstencil_expr, AbstractExpression))
        poly_part = PolyPart(sched_m, tstencil_expr,
                             None, comp,
                             align, scale, level_no-1)

        # Add names to domain and range
        id_domain = isl_alloc_id_for(self.ctx, comp.func.name, poly_part)
        isl_set_id_user(id_domain, poly_part)

        poly_part.sched = poly_part.sched.set_tuple_id(isl.dim_type.in_, id_domain)

        self.poly_parts[comp] = []
        self.poly_parts[comp].append(poly_part)

        return


    def create_sched_space(self, variables, domains,
                           schedule_names, param_names, context_conds):
        # Variable names for referring to dimensions
        var_names = [ var.name for var in variables ]
        space = isl.Space.create_from_names(self.ctx, in_ = var_names,
                                                      out = schedule_names,
                                                      params = param_names)

        sched_map = isl.BasicMap.universe(space)
        # Adding the domain constraints
        [ineqs, eqs] = format_domain_constraints(domains, var_names)
        sched_map = add_constraints(sched_map, ineqs, eqs)

        # Adding the parameter constraints
        [param_ineqs, param_eqs] = format_conjunct_constraints(context_conds)
        sched_map = add_constraints(sched_map, param_ineqs, param_eqs)

        return sched_map


    def create_poly_parts_from_definition(self, comp, max_dim,
                                          sched_map, level_no,
                                          schedule_names, domain):
        self.poly_parts[comp] = []
        for case in comp.func.defn:
            sched_m = sched_map.copy()

            # The basic schedule is an identity schedule appended with
            # a level dimension. The level dimension gives the ordering
            # of the compute objects within a group.

            align, scale = \
                aln_scl.default_align_and_scale(sched_m, max_dim, shift=True)

            if (isinstance(case, Case)):
                # Dealing with != and ||. != can be replaced with < || >.
                # and || splits the domain into two.
                split_conjuncts = case.condition.split_to_conjuncts()
                for conjunct in split_conjuncts:
                    # If the condition is non-affine it is stored as a
                    # predicate for the expression. An affine condition
                    # is added to the domain.
                    affine = True
                    for cond in conjunct:
                        affine = affine and \
                                 isAffine(cond.lhs) and isAffine(cond.rhs)
                    if(affine):
                        [conjunct_ineqs, conjunct_eqs] = \
                            format_conjunct_constraints(conjunct)
                        sched_m = add_constraints(sched_m,
                                                  conjunct_ineqs,
                                                  conjunct_eqs)
                        parts = self.make_poly_parts(sched_m, case.expression,
                                                     None, comp,
                                                     align, scale, level_no)
                        for part in parts:
                            self.poly_parts[comp].append(part)
                    else:
                        parts = self.make_poly_parts(sched_m, case.expression,
                                                     case.condition, comp,
                                                     align, scale, level_no)
                        for part in parts:
                            self.poly_parts[comp].append(part)
            else:
                assert(isinstance(case, AbstractExpression) or
                       isinstance(case, Reduce))
                parts = self.make_poly_parts(sched_m, case,
                                             None, comp,
                                             align, scale, level_no)
                # FIXME: Is a loop required here? make_poly_part
                # seems to return a list of one part
                for part in parts:
                    self.poly_parts[comp].append(part)

        # TODO adding a boundary padding and default to the function 
        # will help DSL usability. 

        # An attempt to subtract all the part domains to find the domain
        # where the default expression has to be applied. 

        #sched_m = isl.BasicMap.identity(self.polyspace)
        #sched_m = add_constraints(sched, ineqs, eqs)
        # Adding stage identity constraint
        #level_coeff = {}
        #level_coeff[varDims[0]] = -1
        #level_coeff[('constant', 0)] = compObjs[comp]
        #sched_m = add_constraints(sched_m, [], [level_coeff])
        #sched_m = add_constraints(sched_m, param_ineqs, param_eqs)

        #for part in self.poly_parts[comp]:
        #    sched_m = sched_m.subtract_range(part.sched.range())
        #    if (sched_m.is_empty()):
        #        break
        #if(not sched_m.fast_is_empty()):
        #    bmap_list = []
        #    if (isinstance(sched_m, isl.BasicMap)):
        #        bmap_list.append(sched_m)
        #    else:
        #        sched_m.foreach_basic_map(bmap_list.append)
        #    for bmap in bmap_list:
        #        poly_part = PolyPart(bmap, comp.func.default, None, comp)
        #        id_ = isl_alloc_id_for(self.ctx, comp.func.name, poly_part)
        #        poly_part.sched = poly_part.sched.set_tuple_id(
        #                                   isl._isl.dim_type.in_, id_)
        #        isl_set_id_user(id_, poly_part)
        #        self.poly_parts[comp].append(poly_part)

    def create_poly_parts_from_default(self, comp, max_dim, sched_map,
                                       level_no, schedule_names):
        sched_m = sched_map.copy()
        align, scale = \
            aln_scl.default_align_and_scale(sched_m, max_dim, shift=True)

        assert(isinstance(comp.func.default, AbstractExpression))
        poly_part = PolyPart(sched_m, comp.func.default,
                             None, comp,
                             align, scale, level_no-1)

        id_ = isl_alloc_id_for(self.ctx, comp.func.name, poly_part)
        poly_part.sched = \
                poly_part.sched.set_tuple_id(isl._isl.dim_type.in_, id_)
        isl_set_id_user(id_, poly_part)
        self.poly_parts[comp].append(poly_part)

    def make_poly_parts(self, sched_map, expr, pred, comp,
                        align, scale, level_no):
        # Detect selects with modulo constraints and split into 
        # multiple parts. This technique can also be applied to the
        # predicate but for now we focus on selects.
        poly_parts = []
        # This is very very temporary solution there should be a 
        # better way of doing this. Only targetting conditions 
        # of the form (affine)%constant == constant.
        broken_parts = []
        if isinstance(expr, Select):
            conjuncts = expr.condition.split_to_conjuncts()
            if len(conjuncts) == 1 and len(conjuncts[0]) == 1:
                cond = conjuncts[0][0]
                left_expr = cond.lhs
                right_expr = cond.rhs
                is_left_modulo = isAffine(left_expr, include_modulo=True) and \
                                 not isAffine(left_expr)
                is_right_constant = is_constant_expr(right_expr)
                break_select = False
                # check for 'affine % constant == constant'
                if is_left_modulo and is_right_constant and \
                    cond.conditional == '==' and \
                    isinstance(left_expr, AbstractBinaryOpNode)\
                    and left_expr.op == '%' and isAffine(left_expr.left)\
                    and is_constant_expr(left_expr.right):
                    break_select = True
                if break_select:
                    left_const = get_constant_from_expr(left_expr.left,
                                                        affine = True)
                    right_const = get_constant_from_expr(right_expr,
                                                         affine = True)
                    mod_const = get_constant_from_expr(left_expr.right,
                                                       affine = True)

                    left_coeff = get_affine_var_and_param_coeff(left_expr.left)
                    left_coeff = map_coeff_to_dim(left_coeff)

                    mul_name = '_Mul_'
                    rem_name = '_Rem_'

                    # true branch schedule
                    true_sched = sched_map.copy()
                    dim_in = true_sched.dim(isl._isl.dim_type.in_)
                    true_sched = \
                        true_sched.insert_dims(isl._isl.dim_type.in_,
                                               dim_in, 1)
                    true_sched = \
                        true_sched.set_dim_name(isl._isl.dim_type.in_,
                                                dim_in, mul_name)

                    eqs = []
                    left_coeff[('constant', 0)] = left_const - right_const
                    left_coeff[('in', dim_in)] = -mod_const
                    eqs.append(left_coeff)

                    true_sched = add_constraints(true_sched, [], eqs)
                    true_sched = true_sched.project_out(isl._isl.dim_type.in_,
                                                        dim_in, 1)
                    broken_parts.append((true_sched, expr.true_expression))

                    # false branch schedule
                    false_sched = sched_map.copy()
                    dim_in = false_sched.dim(isl._isl.dim_type.in_)
                    false_sched = \
                        false_sched.insert_dims(isl._isl.dim_type.in_,
                                                dim_in, 2)
                    false_sched = \
                        false_sched.set_dim_name(isl._isl.dim_type.in_,
                                                 dim_in, mul_name)
                    false_sched = \
                        false_sched.set_dim_name(isl._isl.dim_type.in_,
                                                 dim_in+1, rem_name)

                    eqs = []
                    left_coeff[('constant', 0)] = left_const - right_const
                    left_coeff[('in', dim_in)] = -mod_const
                    left_coeff[('in', dim_in+1)] = -1
                    eqs.append(left_coeff)

                    ineqs = []
                    coeff = {}
                    coeff[('in', dim_in+1)] = 1
                    coeff[('constant', 0)] = -1
                    ineqs.append(coeff)

                    coeff = {}
                    coeff[('in', dim_in+1)] = -1
                    coeff[('constant', 0)] = mod_const-1
                    ineqs.append(coeff)

                    false_sched = add_constraints(false_sched, ineqs, eqs)
                    false_sched = \
                        false_sched.project_out(isl._isl.dim_type.in_,
                                                dim_in, 2)
                    broken_parts.append((false_sched, expr.false_expression))

        # Note the align and scale lists are cloned otherwise all the parts
        # will be sharing the same alignment and scaling
        if not broken_parts:
            poly_part = PolyPart(sched_map, expr, pred, comp,
                                 list(align), list(scale), level_no)
            # Create a user pointer, tuple name and add it to the map
            id_ = isl_alloc_id_for(self.ctx, comp.func.name, poly_part)
            poly_part.sched = poly_part.sched.set_tuple_id(
                                          isl._isl.dim_type.in_, id_)
            isl_set_id_user(id_, poly_part)
            poly_parts.append(poly_part)
        else:
            for bsched_map, bexpr in broken_parts:
                poly_part = PolyPart(bsched_map, bexpr, pred, comp,
                                     list(align), list(scale), level_no)
                # Create a user pointer, tuple name and add it to the map
                id_ = isl_alloc_id_for(self.ctx, comp.func.name, poly_part)
                poly_part.sched = poly_part.sched.set_tuple_id( \
                                        isl._isl.dim_type.in_, id_)
                isl_set_id_user(id_, poly_part)
                poly_parts.append(poly_part)
        return poly_parts

    def generate_code(self):
        self.polyast = []
        if self.poly_parts:
            self.build_ast()

    def build_ast(self):
        #astbld =  isl.AstBuild.from_context( \
        #               isl.BasicSet("[C, R]->{: R>=1 and C>=1}", self.ctx))
        parts = []
        for plist in self.poly_parts.values():
            parts.extend(plist)

        # TODO figure out a way to create the correct parameter context
        # since the parameters for all the parts may not be the same
        astbld = isl.AstBuild.from_context(parts[0].sched.params())
        #astbld =  astbld.set_options(isl.UnionMap("{ }"))

        sched_map = None
        opt_map = None
        for part in parts:
            if sched_map is None:
                # initial map
                sched_map = isl.UnionMap.from_map(part.sched)
            else:
                part_map = isl.UnionMap.from_map(part.sched)
                sched_map = sched_map.union(part_map)

            srange = part.sched.range()
            unroll_union_set = \
                isl.UnionSet.from_set(isl.Set("{:}", self.ctx))
            dom_union_set = \
                isl.UnionSet.universe(isl.UnionSet.from_set(srange))
            if opt_map is None:
                opt_map = isl.UnionMap.from_domain_and_range(dom_union_set, \
                                                             unroll_union_set)
            else:
                opt_map = opt_map.union( \
                            isl.UnionMap.from_domain_and_range( \
                                dom_union_set, unroll_union_set) )
        astbld = astbld.set_options(opt_map)

        # All parts in the group will have the same schedule dimension
        # using the first part as the canonical one
        num_ids = parts[0].sched.dim(isl._isl.dim_type.out)
        ids = isl.IdList.alloc(self.ctx, num_ids)
        for i in range(0, num_ids):
            sched_name = parts[0].sched.get_dim_name(isl._isl.dim_type.out, i)
            id_ = isl.Id.alloc(self.ctx, sched_name, None)
            ids = ids.add(id_)
        astbld = astbld.set_iterators(ids)
        self.polyast.append(astbld.ast_from_schedule(sched_map))

    def getVarName(self):
        name = "_i" + str(self._var_count)
        self._var_count+=1
        return name

    def __str__(self):
        polystr = ""
        for comp in self.poly_parts:
            for part in self.poly_parts[comp]:
                polystr = polystr + part.__str__() + '\n'

        if (self.polyast != []):
            for ast in self.polyast:
                printer = isl.Printer.to_str(self.ctx)
                printer = printer.set_output_format(isl.format.C)
                printOpts = isl.AstPrintOptions.alloc(self.ctx) 
                printer = ast.print_(printer, printOpts)
                aststr = printer.get_str()
                polystr = polystr + '\n' + aststr
        return polystr


def get_dim_size(interval, param_estimates):
    param_val_map = {}
    for est in param_estimates:
        assert isinstance(est[0], Parameter)
        param_val_map[est[0]] = Value.numericToValue(est[1])

    dim_size = interval.upperBound - interval.lowerBound + 1
    return substitute_vars(dim_size, param_val_map)

def get_domain_dim_coeffs(sched, arg):
    dom_dim_coeff = {}
    if (isAffine(arg)):
        coeff = get_affine_var_and_param_coeff(arg)
        for item in coeff:
            if type(item) == Variable:
                dim = sched.find_dim_by_name(isl._isl.dim_type.in_,
                                             item.name)
                dom_dim_coeff[dim] = coeff[item]
    return dom_dim_coeff

def get_param_coeffs(sched, arg):
    param_coeff = {}
    if (isAffine(arg)):
        coeff = get_affine_var_and_param_coeff(arg)
        for item in coeff:
            if type(item) == Parameter:
                dim = sched.find_dim_by_name(isl._isl.dim_type.param,
                                             item.name)
                param_coeff[dim] == coeff[item]
    return param_coeff

def map_coeff_to_dim(coeff):
    variables = list(coeff.keys())
    for var in variables:
        coeffval = coeff[var]
        coeff.pop(var)
        if (isinstance(var, Parameter)):
            coeff[('param', var.name)] = coeffval
        elif (isinstance(var, Variable)):
            coeff[('in', var.name)] = coeffval
    return coeff

def format_domain_constraints(domain, var_names):
    ineq_coeff = []
    eq_coeff   = []
    dom_len = len(domain)
    for i in range(0, dom_len):
        coeff = {}
        interval = domain[i]

        lb_coeff = get_affine_var_and_param_coeff(interval.lowerBound)
        # Mapping from variable names to the corresponding dimension
        lb_coeff = map_coeff_to_dim(lb_coeff)
        lb_const = get_constant_from_expr(interval.lowerBound, affine = True)

        # Normalizing into >= format
        coeff = dict( (n, -lb_coeff.get(n)) for n in lb_coeff )
        coeff[('constant', 0)] = -lb_const
        coeff[('in', var_names[i])] = 1
        ineq_coeff.append(coeff)

        ub_coeff = get_affine_var_and_param_coeff(interval.upperBound)
        # Mapping from variable names to the corresponding dimension
        ub_coeff = map_coeff_to_dim(ub_coeff)
        ub_const = get_constant_from_expr(interval.upperBound, affine = True)

        # Normalizing into >= format
        coeff = ub_coeff
        coeff[('constant', 0)] = ub_const
        coeff[('in', var_names[i])] = -1
        ineq_coeff.append(coeff)

    return [ineq_coeff, eq_coeff]

def format_conjunct_constraints(conjunct):
    # TODO check if the condition is a conjunction
    ineq_coeff = []
    eq_coeff = []
    for cond in conjunct:
        coeff = {}
        left_coeff = get_affine_var_and_param_coeff(cond.lhs)
        right_coeff = get_affine_var_and_param_coeff(cond.rhs)
        left_const = get_constant_from_expr(cond.lhs, affine = True)
        right_const = get_constant_from_expr(cond.rhs, affine = True)

        # Mapping from variable names to the corresponding dimension
        left_coeff = map_coeff_to_dim(left_coeff)
        right_coeff = map_coeff_to_dim(right_coeff)
        
        def constant_div_factor(const):
            m = 1
            for coeff in const:
                if isinstance(const[coeff], Fraction):
                    m = (abs(const[coeff].denominator) * m) // \
                        gcd(abs(const[coeff].denominator), m)
            assert m.denominator == 1
            m = m.numerator
            return m

        # Normalizing >= format
        if (cond.conditional in ['<=','<']):
            coeff = dict( (n, -left_coeff.get(n, 0) + right_coeff.get(n, 0)) \
                          for n in set(left_coeff) | set(right_coeff) )
            d = constant_div_factor(coeff)
            coeff[('constant', 0)] = -left_const + right_const - \
                                     int(cond.conditional == '<') - \
                                     Fraction(d-1, d)
            ineq_coeff.append(coeff)
        elif(cond.conditional in ['>=','>']):
            coeff = dict( (n, left_coeff.get(n, 0) - right_coeff.get(n, 0)) \
                           for n in set(left_coeff) | set(right_coeff) )
            d = constant_div_factor(coeff)
            coeff[('constant', 0)] = left_const - right_const - \
                                     int(cond.conditional == '>') + \
                                     Fraction(d-1, d)
            ineq_coeff.append(coeff)
        else:
            # Weird
            assert(cond.conditional == '==')
            coeff = dict( (n, left_coeff.get(n, 0) - right_coeff.get(n, 0)) \
                          for n in set(left_coeff) | set(right_coeff) )
            coeff[('constant', 0)] = left_const - right_const
            eq_coeff.append(coeff)

    return [ineq_coeff, eq_coeff]
