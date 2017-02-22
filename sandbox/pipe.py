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
# pipe.py : Intermediate representation of pipeline specification and driving
#           the optimization processes at a high level.
#

from __future__ import absolute_import, division, print_function

# More Python 3 vs 2 mojo

try:
    import queue
except ImportError:
    import Queue as queue

import pygraphviz as pgv
import targetc as genc

from grouping import *

from constructs import *
from expression import *
from codegen import *
from schedule import *
from poly_schedule import *
from align_scale import *
from poly import *
from bounds import *
from inline import *
from liveness import *
from libpluto import *
from storage_mapping import *
import islpy as isl

# LOG CONFIG #
pipe_logger = logging.getLogger("pipe.py")
pipe_logger.setLevel(logging.DEBUG)
log_level = logging.INFO
LOG = pipe_logger.log

def get_parents_from_func(func, non_image=True):
    refs = func.getObjects(Reference)
    # Filter out self and image references
    if non_image:
        refs = [ ref for ref in refs if not ref.objectRef == func and \
                                     not (isinstance(ref.objectRef, Image) or (isinstance(ref.objectRef, Matrix) and ref.objectRef.isInput) \
                                     or (isinstance(ref.objectRef, Wave) and ref.objectRef.isInput)) ]
    else:
        refs = [ ref for ref in refs if not ref.objectRef == func ]
    return list(set([ref.objectRef for ref in refs]))

def get_funcs_and_dep_maps(outputs):
    """
    Find all the compute objects required for the outputs and
    also builds parent and children maps for the compute objects
    """
    funcs = []
    funcs_parents = {}
    funcs_children = {}
    # queue of compute objects
    q = queue.Queue()
    for func in outputs:
        q.put(func)
    while not q.empty():
        obj = q.get()
        parent_objs = get_parents_from_func(obj)
        if obj not in funcs:
            funcs.append(obj)
            funcs_parents[obj] = parent_objs
            for parobj in parent_objs:
                if parobj in funcs_children:
                    if obj not in funcs_children[parobj]:
                        funcs_children[parobj].append(obj)
                else:
                    funcs_children[parobj] = [obj]
            if len(parent_objs) != 0:
                for r in parent_objs:
                    q.put(r)

    for func in funcs:
        if func not in funcs_parents:
            funcs_parents[func] = []
        if func not in funcs_children:
            funcs_children[func] = []

    return funcs, funcs_parents, funcs_children

def get_funcs(outputs):
    """
    Find all the compute objects required for the outputs and
    also builds parent and children maps for the compute objects
    """
    funcs = []
    # queue of compute objects
    q = queue.Queue()
    for func in outputs:
        q.put(func)
    while not q.empty():
        obj = q.get()
        parent_objs = get_parents_from_func(obj, non_image=False)
        if obj not in funcs:
            funcs.append(obj)
            if len(parent_objs) != 0:
                for r in parent_objs:
                    q.put(r)

    return funcs


class ComputeObject:
    def __init__(self, _func, _is_output=False):
        assert isinstance(_func, Function)
        self._func = _func
        self._parents = []
        self._children = []
        self._size = self.compute_size()

        self._group = None

        self._is_output = _is_output
        self._is_liveout = True
        self.set_flags()

        self._level_no = 0
        self._group_level_no = 0

        # storage info
        self._orig_storage_class = None
        self._storage_class = None
        self._array = None
        self._scratch_info = []

    @property
    def func(self):
        return self._func

    @property
    def is_parents_set(self):
        return self._is_parents_set
    @property
    def is_children_set(self):
        return self._is_children_set
    @property
    def is_group_set(self):
        return self._is_group_set
    @property
    def is_image_typ(self):
        return self._is_image_typ
    @property
    def is_reduction_typ(self):
        return self._is_reduction_typ

    @property
    def parents(self):
        assert self.is_parents_set
        return self._parents
    @property
    def children(self):
        assert self.is_children_set
        return self._children
    @property
    def size(self):
        return self._size
    @property
    def group(self):
        assert self.is_group_set
        return self._group

    @property
    def level(self):
        return self._level_no
    @property
    def group_level(self):
        return self._group_level_no
    @property
    def is_output(self):
        return self._is_output
    @property
    def is_liveout(self):
        return self._is_liveout

    @property
    def orig_storage_class(self):
        return self._orig_storage_class
    @property
    def storage_class(self):
        return self._storage_class
    @property
    def array(self):
        return self._array
    @property
    def scratch(self):
        return self._scratch_info

    def set_flags(self):
        self._is_parents_set = False
        self._is_children_set = False
        self._is_group_set = False
        self._is_image_typ = isinstance(self.func, Image) or (isinstance(self.func, Matrix) and self.func.isInput) \
                             or (isinstance(self.func, Wave) and self.func.isInput)
        self._is_reduction_typ = isinstance(self.func, Reduction)
        return

    def add_child(self, comp):
        assert isinstance(comp, ComputeObject)
        self._children.append(comp)
        self._children = list(set(self._children))
        self._is_children_set = True
        return
    def add_parent(self, comp):
        assert isinstance(comp, ComputeObject)
        self._parents.append(comp)
        self._parents = list(set(self._parents))
        self._is_parents_set = True
        return

    def remove_child(self, comp):
        if comp in self._children:
            self._children.remove(comp)
        return
    def remove_parent(self, comp):
        if comp in self._parents:
            self._parents.remove(comp)
        return

    def set_parents(self, parents):
        # empty list of parents => root level comp
        if not parents:
            self._is_parents_set = True
            return
        for p in parents:
            assert isinstance(p, ComputeObject)
        self._parents = parents
        self._is_parents_set = True
        return

    def set_children(self, children):
        # empty list of children => leaf level comp
        if not children:
            self._is_children_set = True
            return
        for p in children:
            assert isinstance(p, ComputeObject)
        self._children = children
        self._is_children_set = True
        return

    def set_group(self, group):
        assert isinstance(group, Group)
        self._group = group
        self._is_group_set = True
        return

    def unset_group(self):
        self._group = None
        return

    # within the group
    def compute_liveness(self):
        assert self.is_group_set

        if self.is_output:
            self._is_liveout = True
            return

        # if there any children
        if not self.children:
            # no child => live_out
            self._is_liveout = True
            return

        self._is_liveout = False
        for child in self.children:
            # if any child is in another group
            if child.group != self.group:
                self._is_liveout = True
                break

        return

    # New method for matrix. TODO: Currently sets all to liveout
    def compute_liveness_for_matrix(self):
        self._is_liveout = True;
        return

    def compute_size(self, sizes=None):
        '''
        For each dimension of the compute object, find the interval size and
        the Parameter associated with the dimension
        '''
        # list 'interval_sizes' : [ interval_size[dim] for dim in (0..ndims) ]
        # tuple 'interval_size' : (param, size_expr)
        interval_sizes = []
        intervals = self.func.domain
        dims = self.func.ndims

        def compute_size_tuple(dim, intervals, sizes, funcname):
            if sizes and sizes[dim] != -1:
                param = []  # const
                size = sizes[dim]
            else:
                params = intervals[dim].collect(Parameter)
                #~ assert not len(params) > 1, funcname+", \
					#~ ("+str(dim)+"/"+str(len(params))+'),'+', \
					#~ '.join([par.name for par in params])
                #~ if len(params) == 1:
                    #~ param = params[0]
                #~ elif len(params) == 0:  # const
                    #~ param = 0
                param = params
                size = intervals[dim].upperBound - \
                       intervals[dim].lowerBound + 1
            size = simplify_expr(size)

            return (param, size)

        # if sizes are given, ensure it contains sizes of all dims
        if sizes:
            assert len(sizes) == dims

        # for each dimension
        for dim in range(0, dims):
            dim_size_tuple = \
				compute_size_tuple(dim, intervals, sizes, self._func.name)
            interval_sizes.append(dim_size_tuple)

        return interval_sizes

    def set_level(self, _level_no):
        self._level_no = _level_no
    def set_grp_level(self, _level_no):
        self._group_level_no = _level_no

    def set_orig_storage_class(self, _storage_class):
        assert isinstance(_storage_class, Storage)
        self._orig_storage_class = _storage_class
    def set_storage_class(self, _storage_class):
        assert isinstance(_storage_class, Storage)
        self._storage_class = _storage_class

    def set_storage_object(self, _array):
        assert isinstance(_array, genc.CArray)
        self._array = _array
    def set_scratch_info(self, _scratch_info):
        self._scratch_info = _scratch_info

class Group:
    """ 
        Group is a part of the pipeline which realizes a set of computation
        objects. Scheduling and storage allocation is done at the level of a 
        group. A group also maintains a polyhedral representation of the 
        computation objects when possible.
    """
    # Construct a group from a set of language functions / reductions
    def __init__(self, _ctx, _comp_objs, \
                 _param_constraints):

        self._id = IdGen.get_grp_id()

        log_level = logging.DEBUG

        # All the computation constructs in the language derive from the
        # Function class. Input images cannot be part of a group.
        self._is_image_typ = False
        for comp in _comp_objs:
            assert(isinstance(comp, ComputeObject))
            if comp.is_image_typ:
                self._is_image_typ = True
        self._comps  = _comp_objs
        self._parents = []
        self._children = []

        self.set_comp_group()

        self._level_order_comps = self.order_compute_objs()
        self._comps = self.get_sorted_comps()
        self._inputs = self.find_root_comps()
        self._live_outs = None
        self._image_refs = self.collect_image_refs()

        self._children_map = None
        self._polyrep = None

        # Create a polyhedral representation if possible.
        # Currently doing extraction only when all the compute_objs
        # domains are affine. This can be revisited later.
        if self.isPolyhedral():
            self._polyrep = PolyRep(_ctx, self, [], _param_constraints)

        self._comps_schedule = None
        self._liveness_map = None
        self._can_be_mapped_to_lib = False

    @property
    def id_(self):
        return self._id
    @property
    def comps(self):
        return self._comps
    @property
    def parents(self):
        return self._parents
    @property
    def children(self):
        return self._children

    @property
    def is_image_typ(self):
        return self._is_image_typ

    @property
    def polyRep(self):
        return self._polyrep
    @property
    def inputs(self):
        return self._inputs
    @property
    def liveouts(self):
        return self._live_outs
    @property
    def image_refs(self):
        return self._image_refs
    @property
    def name(self):
        return str([comp.func.name for comp in self.comps])

    @property
    def children_map(self):
        return self._children_map

    @property
    def get_ordered_comps(self):  # <- cant have such a name for property
        return self._level_order_comps
    @property
    def root_comps(self):
        return self._inputs

    @property
    def can_be_mapped_to_lib(self):
        return self._can_be_mapped_to_lib

    @property
    def comps_schedule(self):
        return self._comps_schedule
    @property
    def liveness_map(self):
        return self._liveness_map

    def set_comp_group(self):
        for comp in self.comps:
            comp.set_group(self)
        return

    def find_and_set_parents(self):
        parents = []
        for comp in self.comps:
            comp_parent_groups = [p_comp.group for p_comp in comp.parents]
            parents.extend(comp_parent_groups)
        parents = list(set(parents))
        if self in parents:
            parents.remove(self)
        self.set_parents(parents)
        return parents
    def find_and_set_children(self):
        children = []
        for comp in self.comps:
            comp_children_groups = [c_comp.group for c_comp in comp.children]
            children.extend(comp_children_groups)
        children = list(set(children))
        if self in children:
            children.remove(self)
        self.set_children(children)
        return children

    def add_child(self, group):
        assert isinstance(group, Group)
        self._children.append(group)
        self._children = list(set(self._children))
        return
    def add_parent(self, group):
        assert isinstance(group, Group)
        self._parents.append(group)
        self._parents = list(set(self._parents))
        return

    def remove_child(self, group):
        if group in self._children:
            self._children.remove(group)
        return
    def remove_parent(self, group):
        if group in self._parents:
            self._parents.remove(group)
        return

    def set_parents(self, parents):
        for group in parents:
            assert isinstance(group, Group)
        self._parents = parents
        return
    def set_children(self, children):
        for group in children:
            assert isinstance(group, Group)
        self._children = children
        return

    def compute_liveness(self):
        liveouts = []
        for comp in self.comps:
            comp.compute_liveness()
            parts = self.polyRep.poly_parts[comp]
            for part in parts:
                part.compute_liveness()
            if comp.is_liveout:
                liveouts.append(comp)

        self._live_outs = liveouts
        return

    #TODO: Currently all the functions in Matrix are liveouts.
    def compute_liveness_for_matrix(self):
        liveouts = []
        for comp in self.comps:
            comp.compute_liveness_for_matrix()
            if comp.is_liveout:
                liveouts.append(comp)

        self._live_outs = liveouts
        return

    def is_fused(self):
        return len(self.comps) > 1

    def getParameters(self):
        params = []
        for comp in self.comps:
            params = params + comp.func.getObjects(Parameter)
        return list(set(params))

    def isPolyhedral(self):
        polyhedral = True
        for comp in self.comps:
            if (not comp.func.hasBoundedIntegerDomain()):
                polyhedral = False
                LOG(log_level,"no bounded integer domain for: "+comp.func.name)
        return polyhedral

    def order_compute_objs(self):
        parents = {}
        for comp in self.comps:
            parents[comp] = comp.parents
        order = level_order(self.comps, parents)
        for comp in order:
            comp.set_grp_level(order[comp])
        return order

    def find_root_comps(self):
        root_comps = [comp for comp in self.comps \
                             if self._level_order_comps[comp] == 0]
        return root_comps

    def collect_image_refs(self):
        refs = []
        for comp in self.comps:
            refs += comp.func.getObjects(Reference)
        image_refs = [ref.objectRef for ref in refs \
                      if isinstance(ref.objectRef, Image) or (isinstance(ref.objectRef, Matrix) and ref.objectRef.isInput) \
                      or (isinstance(ref.objectRef, Wave) and ref.objectRef.isInput)]
        image_refs = list(set(image_refs))
        return image_refs

    def collect_comps_children(self):
        children_map = {}
        for comp in self.comps:
            comp_children = \
                [child for child in comp.children \
                         if child.group == self]
            if comp_children:
                children_map[comp] = comp_children
        self._children_map = children_map
        return

    def get_sorted_comps(self):
        sorted_comps = sorted(self._level_order_comps.items(),
                              key=lambda x: x[1])
        sorted_comps = [c[0] for c in sorted_comps]
        return sorted_comps

    def set_comp_and_parts_sched(self):
        self._comps_schedule = schedule_within_group(self)
        return

    def set_can_be_mapped_to_lib(self,lib_call):
        self._can_be_mapped_to_lib = lib_call
        return

    def set_liveness_map(self, _liveness_map):
        self._liveness_map = _liveness_map
        return

    def __str__(self):
        comp_str  = '[' + \
                    ', '.join([comp.func.name \
                        for comp in self.comps]) + \
                    ']'
        return comp_str


class Pipeline:
    def __init__(self, _ctx, _outputs,
                 _param_estimates, _param_constraints,
                 _grouping, _group_size, _inline_directives,
                 _tile_sizes, _size_threshold,
                 _options, _name = None):
        # Name of the pipleline is a concatenation of the names of the 
        # pipeline outputs, unless it is explicitly named.
        if _name is None:
            _name = ''.join([out.name for out in _outputs])

        self._name = _name

        self._ctx = _ctx
        self._orig_outputs = _outputs
        self._param_estimates = _param_estimates
        self._param_constraints = _param_constraints
        self._grouping = _grouping
        self._group_size = _group_size
        self._inline_directives = _inline_directives
        self._options = _options
        self._size_threshold = _size_threshold
        self._tile_sizes = _tile_sizes
        # Adding this variable in order to save the dependencies and pass them on to Pluto
        self.dependencies = []
        # Adding new dictionary inorder to maintain the mapping between Pluto and
        # Polymage function name
        self.polymage_to_pluto_fname_map = {}
        self.pluto_to_polymage_fname_map = {}
        self.function_schedule_map = {}

        if 'matrix' in self.options:
            self._pluto_sched_required = True
        else:
            self._pluto_sched_required = False

        ''' CONSTRUCT DAG '''
        # Maps from a compute object to its parents and children by
        # backtracing starting from given live-out functions.
        # TODO: see if there is a cyclic dependency between the compute
        # objects. Self references are not treated as cycles.
        self._orig_funcs = get_funcs(self._orig_outputs)

        self._inputs = []

        ''' CLONING '''
        # Clone the functions and reductions
        self._clone_map = {}
        for func in self._orig_funcs:
            if isinstance(func, Image) or (isinstance(func, Matrix) and func.isInput) \
               or (isinstance(func, Wave) and func.isInput):
                self._clone_map[func] = func
                self._inputs.append(func)
            else:
                self._clone_map[func] = func.clone()
        self._outputs = [self._clone_map[obj] for obj in self._orig_outputs]
        # Modify the references in the cloned objects (which refer to
        # the original objects)
        for func in self._orig_funcs:
            cln = self._clone_map[func]
            refs = cln.getObjects(Reference)
            for ref in refs:
                if not (isinstance(ref.objectRef, Image) or (isinstance(ref.objectRef, Matrix)
                                                             and ref.objectRef.isInput)
                                                         or (isinstance(ref.objectRef, Wave)
                                                             and ref.objectRef.isInput)):
                    ref._replace_ref_object(self._clone_map[ref.objectRef])

        ''' DAG OF CLONES '''
        self._func_map, self._comps = \
            self.create_compute_objects()



        self._level_order_comps = self.order_compute_objs()
        self._comps = self.get_sorted_comps()

        ''' INITIAL GROUPING '''
        # Create a group for each pipeline function / reduction and compute
        # maps for parent and child relations between the groups
        if self.pluto_sched_required:
            # If Matrix optimization. Group all compute objects into one group
            # Pluto schedule will take care of fusion
            comps = self.comps
            group = Group(self._ctx, comps, self._param_constraints)
            self._groups = [group]
        else:
            self._groups = self.build_initial_groups()

        # Store the initial pipeline graph. The compiler can modify 
        # the pipeline by inlining functions.
        # self._initial_graph = self.draw_pipeline_graph()

        # Checking bounds
        bounds_check_pass(self)



        if self.pluto_sched_required:
            # Generate Schedule
            log_level = logging.INFO
            LOG(log_level, "Identified as Matrix Operation")
            LOG(log_level, "Using Matrix pipeline")

            self.matrix_pipeline_schedule()
            self._level_order_groups = self.order_group_objs()
            self._grp_schedule = schedule_groups(self)
            for group in self._grp_schedule:
                group._comps_schedule = naive_sched_comps(group)

            #Perform Idiom Recognition
            for group in self._groups:
                idiom_recognition(self,group)

        else:
            # inline pass
            inline_pass(self)

            # make sure the set of functions to be inlined and those to be grouped
            # are disjoint
            if self._inline_directives and self._grouping:
                group_comps = []
                for g in self._grouping:
                    group_funcs += g
                a = set(self._inline_directives)
                b = set(group_funcs)
                assert a.isdisjoint(b)

            ''' GROUPING '''
            # TODO check grouping validity
            if self._grouping and False:
                # for each group
                for g in self._grouping:
                    # get clones of all functions
                    clones = [self._clone_map[f] for f in g]
                    comps = [self.func_map[f] for f in clones]
                    # list of group objects to be grouped
                    merge_group_list = \
                        [comp.group for comp in comps]
                    if len(merge_group_list) > 1:
                        merged = merge_group_list[0]
                        for i in range(1, len(merge_group_list)):
                            merged = self.merge_groups(merged, merge_group_list[i])
            else:
                # Run the grouping algorithm
                auto_group(self)
                pass
            self._level_order_groups = self.order_group_objs()

        ''' GRAPH UPDATES '''
        # level order traversal of groups

        self._groups = self.get_sorted_groups()

        for group in self.groups:
            # update liveness of compute objects in each new group
            if self.pluto_sched_required:
                group.compute_liveness_for_matrix()
            else:
                group.compute_liveness()
            # children map for comps within the group
            group.collect_comps_children()
        self._liveouts = self.collect_liveouts()
        self._liveouts_children_map = self.build_liveout_graph()

        # ***
        log_level = logging.INFO
        LOG(log_level, "\n\n")
        LOG(log_level, "Grouped compute objects:")
        for g in self.groups:
            LOG(log_level, g.name+" ")
        # ***

        ''' SCHEDULING '''

        if not self.pluto_sched_required:
            for g in self.groups:
                # alignment and scaling
                align_and_scale(self, g)
                # base schedule
                base_schedule(g)
                # grouping and tiling
                fused_schedule(self, g, self._param_estimates)
                # idiom matching algorithm
                idiom_recognition(self, g)

            # group
            self._grp_schedule = schedule_groups(self)
            # comps and poly parts
            for group in self._grp_schedule:
                group.set_comp_and_parts_sched()

        self._liveouts_schedule = schedule_liveouts(self)

        ''' COMPUTE LIVENESS '''
        # liveouts
        self._liveness_map = liveness_for_pipe_outputs(self)
        # groups
        for group in self.groups:
            liveness_for_group_comps(group, group.children_map,
                                 group.comps_schedule)


        ''' STORAGE '''
        # MAPPING
        self.initialize_storage()

        # OPTIMIZATION
        # classify the storage based on type, dimensionality and size
        self._storage_class_map = classify_storage(self)
        # remap logical storage

        self._storage_map = remap_storage(self)

        # ALLOCATION
        self._array_writers_map = create_physical_arrays(self)
        self._free_arrays = create_array_freelist(self)

        # use graphviz to create pipeline graph
        self._pipeline_graph = self.draw_pipeline_graph()

    @property
    def pluto_sched_required(self):
        return self._pluto_sched_required
    @property
    def func_map(self):
        return self._func_map
    @property
    def comps(self):
        return self._comps
    @property
    def groups(self):
        return self._groups
    @property
    def name(self):
        return self._name
    @property
    def options(self):
        return self._options
    @property
    def inputs(self):
        return self._inputs
    @property
    def outputs(self):
        return self._outputs
    @property
    def original_graph(self):
        return self._initial_graph
    @property
    def pipeline_graph(self):
        return self._pipeline_graph
    @property
    def get_ordered_comps(self):
        return self._level_order_comps
    @property
    def get_ordered_groups(self):  # <- naming
        return self._level_order_groups
    @property
    def liveouts(self):
        return self._liveouts
    @property
    def liveouts_children_map(self):
        return self._liveouts_children_map
    @property
    def group_schedule(self):
        return self._grp_schedule
    @property
    def liveouts_schedule(self):
        return self._liveouts_schedule
    @property
    def storage_class_map(self):
        return self._storage_class_map
    @property
    def storage_map(self):
        return self._storage_map
    @property
    def liveness_map(self):
        return self._liveness_map
    @property
    def array_writers(self):
        return self._array_writers_map
    @property
    def free_arrays(self):
        return self._free_arrays

    def get_parameters(self):
        params=[]
        for group in self.groups:
            params = params + group.getParameters()
        return list(set(params))

    # Accepts new function number, domain in polymage and creates or returns existing
    # domain in Pluto compatible format. Maintains a mapping between the actual function
    # name and the generated one
    @staticmethod
    def get_updated_pluto_domain(pipeline, i, domain):
        function_name = domain.get_tuple_name()
        if function_name in pipeline.polymage_to_pluto_fname_map:
            statement_name = pipeline.polymage_to_pluto_fname_map[function_name]
        else:
            statement_name = "S_"+ i.__str__()
            pipeline.polymage_to_pluto_fname_map[function_name] = statement_name
        domain = domain.set_tuple_name(statement_name)
        if statement_name not in pipeline.pluto_to_polymage_fname_map:
            pipeline.pluto_to_polymage_fname_map[statement_name] = function_name
        return domain

    # Accepts a map in Pluto format and returns schedule in
    # Polymage function names
    def get_polymage_from_pluto_schedule(self, maps):
        map_copy = maps.copy()
        polymage_schedule = None
        for map in map_copy:
            pluto_function_name = map.get_tuple_name(isl._isl.dim_type.in_)
            function_name = self.pluto_to_polymage_fname_map[pluto_function_name]
            map = map.set_tuple_name(isl._isl.dim_type.in_, function_name)
            # Adding into function schedule map, so we can identify the correct polypart
            self.function_schedule_map[function_name] = map
            if polymage_schedule is None:
                polymage_schedule = isl.UnionMap.from_map(map)
            else:
                polymage_schedule = polymage_schedule.add_map(map)
        return polymage_schedule

    # Accepts a map in Polymage format and returns schedule in
    # Pluto compatible statement names
    # domain_and_range parameter specifies if the name conversion needs to be done only
    # for domain or for both domaina and range
    def get_pluto_format_from_polymage_union_map(self, union_map, domain_and_range):
        maps = self.split_unionmaps_to_maps(union_map)
        map_copy = maps.copy()
        polymage_schedule = None
        for map in map_copy:
            polymage_stmnt_name = map.get_tuple_name(isl._isl.dim_type.in_)
            if self.polymage_to_pluto_fname_map[polymage_stmnt_name]:
                function_name = self.polymage_to_pluto_fname_map[polymage_stmnt_name]
            else:
                log_level = logging.ERROR
                LOG(log_level, "Matrix functions in the specification")
                assert (False)
            map = map.set_tuple_name(isl._isl.dim_type.in_, function_name)
            if domain_and_range:
                polymage_stmnt_name = map.get_tuple_name(isl._isl.dim_type.out)
                if self.polymage_to_pluto_fname_map[polymage_stmnt_name]:
                    function_name = self.polymage_to_pluto_fname_map[polymage_stmnt_name]
                    map = map.set_tuple_name(isl._isl.dim_type.out, function_name)
            if polymage_schedule is None:
                polymage_schedule = isl.UnionMap.from_map(map)
            else:
                polymage_schedule = polymage_schedule.add_map(map)
        return polymage_schedule

    # Extract dependencies.
    # Accepts Reads, Writes and Initial Schedule
    # Returns Union Map of Dependencies (RAW, WAW and WAR)
    def getDependencies(self, read_map, write_map, initial_schedule):
        # initial_schedule << initial_schedule
        initial_schedule = initial_schedule.lex_lt_union_map(initial_schedule)
        # Read^-1
        read_inverse = read_map.fixed_power_val(-1)
        # (Write . (Read^-1)) * Before
        RAW_deps = (write_map.apply_range(read_inverse)).intersect(initial_schedule)

        write_inverse = write_map.fixed_power_val(-1)
        WAW_deps = (write_map.apply_range(write_inverse)).intersect(initial_schedule)

        WAR_deps = (read_map.apply_range(write_inverse)).intersect(initial_schedule)

        dependencies = (RAW_deps.union(WAW_deps)).union(WAR_deps)
        # dependencies = RAW_deps.union(WAR_deps)
        # dependencies = RAW_deps
        return dependencies

    # Pipeline for Matrix functions
    # TODO: Modularize
    def matrix_pipeline_schedule(self):
        LOG(log_level, "Matrix functions in the specification")

        domain_union_set = None
        deps_union_map = None
        sched_union_map = None
        read_map = None
        write_map = None
        i = 0;

        main_poly_part = []
        for group in self._groups:
            # Align and scale and generate inital Schedule.
            # Required for generating dependencies
            align_and_scale(self, group)
            base_schedule(group)

            for comp in group.comps:
                poly_parts = group.polyRep.poly_parts[comp]
                main_poly_part.extend(poly_parts)

            for poly_part in main_poly_part:
                in_schedule = poly_part.sched.copy()
                domain = in_schedule.domain()
                # Create Pluto compatible statement names
                domain = self.get_updated_pluto_domain(self, i, domain)
                poly_part.stmt_no = i;
                i = i + 1

                # Collect Domain for all statements
                if domain_union_set is None:
                    domain_union_set = isl.UnionSet.from_basic_set(domain)
                else:
                    set = isl.Set.from_basic_set(domain)
                    domain_union_set = domain_union_set.add_set(set)

                # Collect Read access for all statements
                if group.polyRep.read_union_map[poly_part]:
                    if read_map is None:
                        read_map = group.polyRep.read_union_map[poly_part]
                    else:
                        read_map = read_map.union(group.polyRep.read_union_map[poly_part])

                # Collect Write access for all statements
                if group.polyRep.write_union_map[poly_part]:
                    if write_map is None:
                        write_map = group.polyRep.write_union_map[poly_part]
                    else:
                        write_map = write_map.union(group.polyRep.write_union_map[poly_part])

                # Collect Initial Schedule for all statements
                if sched_union_map is None:
                    sched_union_map = isl.UnionMap.from_basic_map(in_schedule)
                else:
                    map = isl.Map.from_basic_map(in_schedule)
                    sched_union_map = sched_union_map.add_map(map)


        LOG(log_level, "Read Access:   " + str(read_map))
        LOG(log_level, "Write Access:    " + str(write_map))

        deps_union_map = self.getDependencies(read_map, write_map, sched_union_map)

        # Convert to Pluto compatible format
        read_map = self.get_pluto_format_from_polymage_union_map(read_map, False)
        write_map = self.get_pluto_format_from_polymage_union_map(write_map, False)
        deps_union_map = self.get_pluto_format_from_polymage_union_map(deps_union_map, True)

        LOG(log_level, "Statements converted to Pluto (S0, S1 ......)")
        LOG(log_level, "Domain for all statements")
        LOG(log_level, domain_union_set.to_str())

        if deps_union_map:
            LOG(log_level,"Dependencies across statements")
            LOG(log_level,deps_union_map.to_str())
        else:
            # If no dependencies found, then send empty UnionMap to Pluto
            LOG(log_level, "No dependencies found")
            # str1 = '[R, C] -> { S_0[x, y, prod_var_mat1_mat2] -> S_4[x, y] : R = 128 and C = 128 and 0 <= x <= 127 and 0 <= y <= 127 and 0 <= prod_var_mat1_mat2 <= 127; S_2[x, y, prod_var_mat1_mat3] -> S_2[x, y, prod_var_mat1_mat3_1] : C = 128 and R = 128 and 0 <= x <= 127 and 0 <= y <= 127 and 0 <= prod_var_mat1_mat3 <= 127 and prod_var_mat1_mat3 < prod_var_mat1_mat3_1 <= 127; S_0[x, y, prod_var_mat1_mat2] -> S_0[x, y, prod_var_mat1_mat2_1] : C = 128 and R = 128 and 0 <= x <= 127 and 0 <= y <= 127 and 0 <= prod_var_mat1_mat2 <= 127 and prod_var_mat1_mat2 < prod_var_mat1_mat2_1 <= 127; S_2[x, y, prod_var_mat1_mat3] -> S_4[x, y] : R = 128 and C = 128 and 0 <= x <= 127 and 0 <= y <= 127 and 0 <= prod_var_mat1_mat3 <= 127; }'
            # deps_union_map = isl.UnionMap.read_from_str(self._ctx, str1)
            # LOG(log_level, deps_union_map.to_str())
            # deps_union_map = isl.UnionMap.read_from_str(self._ctx, '{}')

        # Pluto call
        pluto = LibPluto()
        pluto_options = pluto.create_options()
        out_schedule = pluto.schedule(self._ctx, domain_union_set, deps_union_map, pluto_options)

        # Making the remapping call to figure out which dims are scalar
        # and the tile information
        remapping = pluto.get_remapping(self._ctx, domain_union_set, deps_union_map, pluto_options)


        LOG(log_level,"Schedule recieved from Pluto:")
        LOG(log_level,out_schedule)

        # Extract basic maps from UnionMap
        if out_schedule.n_map() > 0:
            maps = self.split_unionmaps_to_maps(out_schedule)

        # Replace the schedule with the correct function names
        polymage_schedules = self.get_polymage_from_pluto_schedule(maps)
        LOG(log_level, "Schedule after converting to Polymage:")
        LOG(log_level,polymage_schedules)


        # Append these schedules to the corresponding polyparts
        for poly_part in main_poly_part:
            in_schedule = poly_part.sched
            in_domain = in_schedule.domain()
            func_sched_name = in_schedule.get_tuple_name(isl._isl.dim_type.in_)
            new_sched = self.function_schedule_map[func_sched_name]

            # Removes any scalar dimensions
            new_sched = new_sched.copy().get_basic_maps()[0]
            num_out_dim = new_sched.range().n_dim()
            # Assigning dimension name for out dimension. Required for building ast
            for i in range(0, num_out_dim):
                new_sched = new_sched.set_dim_name(isl.dim_type.out, i, 'o' + i.__str__())

            # Intersect with domain in order to bound the schedule to the required space
            new_sched = new_sched.intersect_domain(in_domain)

            # Replace in dimensions with variable names
            if isinstance(poly_part.comp.func, Reduction) and not (poly_part.is_default_part):
                for i, var in enumerate(poly_part.func.reductionVariables):
                    new_sched = new_sched.set_dim_name(isl.dim_type.in_, i, var.name)
                num_vars = len(poly_part.func.reductionVariables)
            else:
                for i, var in enumerate(poly_part.func.variables):
                    new_sched = new_sched.set_dim_name(isl.dim_type.in_, i, var.name)
                num_vars = len(poly_part.func.variables)
            poly_part.sched = new_sched

            #TODO: Retrieve the correct elements from inverse matrix
            # time_index = num_vars
            # stmt_num = poly_part.stmt_no
            # inv_map = remapping.inv_matrices[stmt_num][time_index][time_index:time_index + num_vars + 1]
            # divs = remapping.divs[stmt_num][time_index]

            # time_indexing_coeff = (inv_map, divs)
            # Mark parallel and vector loops
            # TODO: Needs seperate implemetation for Pluto Schedule
            #TODO: Add mar_par_for_tiled_loops

        return

    # Accepts union map and returns a list of BasicMap
    def split_unionmaps_to_maps(self,union_map):
        basic_maps = []

        def map_callback(m):
            basic_maps.append(m.copy())

        union_map.foreach_map(map_callback)
        return basic_maps

    def create_compute_objects(self):
        funcs, parents, children = \
            get_funcs_and_dep_maps(self.outputs)
        comps = []
        func_map = {}
        for func in funcs:
            output = False
            if func in self.outputs:
                output = True
            comp = ComputeObject(func, output)
            func_map[func] = comp
            comps.append(comp)

        # set parents, children information
        for func in func_map:
            comp = func_map[func]
            # set parents
            comp_parents = [func_map[p_func] for p_func in parents[func]]
            comp.set_parents(comp_parents)
            # set children
            comp_children = [func_map[c_func] for c_func in children[func]]
            comp.set_children(comp_children)

        for inp in self._inputs:
            inp_comp = ComputeObject(inp)
            inp_comp.set_parents([])
            inp_comp.set_children([])
            func_map[inp] = inp_comp
        return func_map, comps

    def order_compute_objs(self):
        parent_map = {}
        for comp in self.comps:
            parent_map[comp] = comp.parents
        order = level_order(self.comps, parent_map)
        for comp in order:
            comp.set_level(order[comp])
        return order

    def order_group_objs(self):
        parent_map = {}
        for group in self.groups:
            parent_map[group] = group.parents
        order = level_order(self.groups, parent_map)
        return order

    def get_sorted_comps(self):
        sorted_comps = get_sorted_objs(self._level_order_comps, True)
        return sorted_comps

    def get_sorted_groups(self):
        sorted_groups = get_sorted_objs(self._level_order_groups)
        return sorted_groups

    def build_initial_groups(self):
        """
        Place each compute object of the pipeline in its own Group, and set the
        dependence relations between the created Group objects.
        """
        comps = self.comps
        groups = []
        for comp in comps:
            group = Group(self._ctx, [comp], self._param_constraints)
            groups.append(group)

        for group in groups:
            group.find_and_set_parents()
            group.find_and_set_children()

        return groups

    def draw_pipeline_graph(self):
        gr = pgv.AGraph(strict=False, directed=True)

        # TODO add input nodes to the graph
        for i in range(0, len(self.groups)):
            sub_graph_nodes = [comp.func.name for comp in self.groups[i].comps]
            for comp in self.groups[i].comps:
                # liveout or not
                style = 'rounded'
                if comp.is_liveout:
                    style += ', bold'
                else:
                    style += ', filled'
                # comp's array mapping
                color_index = self.storage_map[comp]
                gr.add_node(comp.func.name,
                            color=X11Colours.colour(color_index),
                            style=style,
                            shape="box")

            # add group boundary
            gr.add_subgraph(nbunch = sub_graph_nodes,
                            name = "cluster_" + str(i),
                            label=str(self.group_schedule[self.groups[i]]),
                            style="dashed, rounded")

        for comp in self.comps:
            for p_comp in comp.parents:
                gr.add_edge(p_comp.func.name, comp.func.name)

        gr.layout(prog='dot')
        return gr

    def generate_code(self, is_extern_c_func=False,
                            are_io_void_ptrs=False):

        """
        Code generation for the entire pipeline starts here.

        Flags:

        1. "is_extern_c_func"
        (*) True => function declaration generated with ' extern "C" ' string
                    (used when dynamic libs are needed for python wrapping)
        (*) False => normal C function declaration


        2. "are_io_void_ptrs"
        (*) True => all inputs and outputs of the pipeline are expected, by the
                    C function declaration, to be passed as 'void *'
                    (used when dynamic libs are needed for python wrapping)
        (*) False => inputs and outputs are to be passed as pointers of their
                     data type. E.g: 'float *'
        """

        return generate_code_for_pipeline(self,
                                          is_extern_c_func,
                                          are_io_void_ptrs)

    '''
    Pipelne graph operations
    '''

    def drop_comp(self, comp):
        # if the compute object is a child of any other
        if comp.parents:
            for p_comp in comp.parents:
                p_comp.remove_child(comp)
        # if the compute object is a parent of any other
        if comp.children:
            for c_comp in comp.children:
                c_comp.remove_parent(comp)
        # remove comp_obj
        self._comps.remove(comp)
        func = comp.func
        self._func_map.pop(func)

        return

    def add_group(self, group):
        """
        add a new group to the pipeline
        """
        if not group.comps:
            return

        self._groups.append(group)

        group.find_and_set_parents()
        group.find_and_set_children()

        # add group as child for all its parents
        for p_group in group.parents:
            p_group.add_child(group)
        # add group as parent for all its children
        for c_group in group.children:
            c_group.add_parent(group)

        return

    def drop_group(self, group):
        """
        drop the group from the pipeline
        """
        # if group is a child of any other group
        if group.parents:
            for p_group in group.parents:
                p_group.remove_child(group)
        # if group is a parent of any other group
        if group.children:
            for c_group in group.children:
                c_group.remove_parent(group)
        for comp in group.comps:
            comp.unset_group()
        self._groups.remove(group)

        return

    def merge_groups(self, g1, g2):
        # Get comp objects from both groups
        comps = g1.comps + g2.comps
        comps = list(set(comps))

        self.drop_group(g1)
        self.drop_group(g2)

        # Create a new group
        merged = Group(self._ctx, comps,
                       self._param_constraints)

        self.add_group(merged)

        return merged

    def replace_group(self, old_group, new_group):
        # if old_group has any child
        if old_group.children:
            for child in old_group.children:
                child.add_parent(new_group)
                new_group.add_child(child)
        # if old_group has any parent
        if old_group.parents:
            for parent in old_group.parents:
                parent.add_child(new_group)
                new_group.add_parent(parent)

        # replace old_group with new_group in groups list
        comp = old_group.comps[0]
        self.drop_group(old_group)
        comp.set_group(new_group)

        self._groups.append(new_group)

        return

    def make_func_independent(self, func_a, func_b):
        """
        makes func_b independent of func_b and updates parent children
        relations in the graph structure
        [ assumes that func_b is a child of func_a, and that func_a is inlined
        into func_b ]
        """
        comp_a = self.func_map[func_a]
        comp_b = self.func_map[func_b]
        group_a = comp_a.group
        group_b = comp_b.group
        # if parent_comp has any parent
        if comp_a.parents:
            parents_of_a = comp_a.parents
            parents_of_b = comp_b.parents
            parents_of_grp_a = group_a.parents
            parents_of_grp_b = group_b.parents

            # remove relation between a and b
            comp_a.remove_child(comp_b)
            group_a.remove_child(group_b)

            parents_of_b.remove(comp_a)
            parents_of_grp_b.remove(group_a)

            # new parents list for b
            # compute object
            parents_of_b.extend(parents_of_a)
            parents_of_b = list(set(parents_of_b))
            # group object
            parents_of_grp_b.extend(parents_of_grp_a)
            parents_of_grp_b = list(set(parents_of_grp_b))

            comp_b.set_parents(parents_of_b)
            group_b.set_parents(parents_of_grp_b)

            # new children list for parents_of_b
            for p_comp in parents_of_b:
                p_comp.add_child(comp_b)
            for p_group in parents_of_grp_b:
                p_group.add_child(group_b)

        return

    def __str__(self):
        return_str = "Final Group: " + self._name + "\n"
        for s in self._groups:
            return_str = return_str + s.__str__() + "\n"
        return return_str

    def collect_liveouts(self):
        liveouts = [comp for group in self.groups \
                           for comp in group.liveouts]
        return liveouts

    def build_liveout_graph(self):
        liveouts = self.liveouts
        children_map = {}
        for comp in liveouts:
            g_liveouts = []
            if comp.children:
                # collect groups where comp is livein
                livein_groups = [child.group for child in comp.children]
                # collect liveouts of these groups
                for g in livein_groups:
                    g_liveouts += g.liveouts
            if g_liveouts:
                children_map[comp] = g_liveouts
        return children_map

    def initialize_storage(self):
        # ***
        log_level = logging.DEBUG-1
        LOG(log_level, "Initializing Storage ...")

        for func in self.func_map:
            comp = self.func_map[func]
            typ = comp.func.typ
            ndims = comp.func.ndims
            part_map = comp.group.polyRep.poly_parts
            dim_sizes = []
            # 1. Input Images
            # 2. Group Live-Outs
            # 3. Not a scratchpad  (maybe Reduction)
            reduced_dims = [ -1 for i in range(0, ndims) ]
            is_scratch = [ False for i in range(0, ndims) ]
            if comp.is_image_typ or comp.is_liveout or comp not in part_map:
                interval_sizes = comp.size
            # 4. Scratchpads
            else:
                for part in part_map[comp]:
                    for i in range(0, ndims):
                        if i in part.dim_scratch_size:  # as a key
                            reduced_dims[i] = max(reduced_dims[i],
                                                  part.dim_scratch_size[i])
                            is_scratch[i] = True

                for i in range(0, ndims):
                    dim_sizes.append(reduced_dims[i])

                interval_sizes = comp.compute_size(dim_sizes)

            comp.set_scratch_info(is_scratch)

            storage = Storage(typ, ndims, interval_sizes)
            comp.set_orig_storage_class(storage)

            # ***
            LOG(log_level, "  "+comp.func.name)
            LOG(log_level, "    "+str(storage))

        return


# Function to recognize computations which can be mapped to library calls
def idiom_recognition(pipeline, group):
    blas = 'blas' in pipeline.options
    if not blas:
        return
    g_poly_parts = group.polyRep.poly_parts
    for comp in g_poly_parts:
        g_all_comp_parts = []
        g_all_comp_parts.extend(g_poly_parts[comp])
        matrix_mul_found = match_idiom_matrix_mul(g_all_comp_parts)
        if matrix_mul_found:
            if 'matrix' in pipeline.options:
                isPlutoSchedule = True
            else:
                isPlutoSchedule = False
            replace_sched_expr_with_matched_idiom(g_all_comp_parts, isPlutoSchedule, Idiom_type.mat_mat_mul)
            LOG(log_level,"Idiom Match Found for comp: " + comp.func.name)
        else:
            LOG(log_level,"No match found for comp: " + comp.func.name)
    return

# Replace schedule and expr of identified computation with lib calls
def replace_sched_expr_with_matched_idiom(g_all_parts, isPlutoSchedule, idiom):
    if idiom == Idiom_type.mat_mat_mul:
        if g_all_parts[0].expr == 0:
            poly_part = g_all_parts[1]
        else:
            poly_part = g_all_parts[0]

        poly_part.is_idiom = True
        tuple_in = poly_part.sched.get_tuple_id(isl._isl.dim_type.in_)
        eqs = []
        ineqs = []

        if isPlutoSchedule:
            #TODO: Assuming the code is tiled. Need to add a condition to check that
            n_dims = poly_part.sched.dim(isl._isl.dim_type.out)
            if not n_dims >= 4:
                log_level = logging.ERROR
                LOG(log_level, "Wrong number of dimensions found for Idiom Match")
                raise RuntimeError("Number of dimensions did not match with the Idiom")
            n_dims = n_dims - 3
            start_dim = n_dims - 3
            log_level = logging.INFO
            LOG(log_level, "Idiom Matching for Pluto Schedule")
        else:
            # When Tiling is not performed or when Pluto schedule is not invoked.
            n_dims = poly_part.sched.dim(isl._isl.dim_type.out)
            if not n_dims >= 4:
                log_level = logging.ERROR
                LOG(log_level, "Wrong number of dimensions found for Idiom Match")
                raise RuntimeError("Number of dimensions did not match with the Idiom")
            start_dim = n_dims - 3

        for i in range(start_dim, n_dims):
            name = poly_part.sched.get_dim_name(isl._isl.dim_type.out, i)
            coeff = {}
            coeff[('out', name)] = 1
            eqs.append(coeff)

        poly_part.sched = add_constraints(poly_part.sched, ineqs, eqs)
        poly_part.sched = poly_part.sched.set_tuple_id(isl._isl.dim_type.in_, tuple_in)
    return

# def replace_with_lib_call(group,g_all_parts):
    # comp_map = group.get_ordered_comps
    # comps = group.comps
    # dim = 0 # changing the schedule and the polypart of the space
    # schedule_names = ['_t']
    # grp_params = []
    # for comp in comps:
    #     grp_params = grp_params + comp.func.getObjects(Parameter)
    # grp_params = list(set(grp_params))

    # transformed_func = Function(([],[]), Float, comp.func.name + "_mul")
    # transformed_func.defn = [0]
    #
    # comp._func = transformed_func

    # new_comp_object = ComputeObject(transformed_func)
    #
    # for parent in comp.parents:
    #     new_comp_object.add_parent(parent)
    # for child in comp.children:
    #     new_comp_object.add_child(child)
    # new_comp_object.set_group(group)
    # new_comp_object.set_grp_level(comp.group_level)
    # new_comp_object.set_level(comp.level)
    # if comp.orig_storage_class:
    #     new_comp_object.set_orig_storage_class(comp.orig_storage_class)
    # if comp.storage_class:
    #     new_comp_object.set_storage_class(comp.storage_class)
    # if comp.array:
    #     new_comp_object.set_storage_object(comp.array)
    #
    # group._comps = [new_comp_object]

    # param_names = [param.name for param in grp_params]
    #
    # context_conds = \
    #     group.polyRep.format_param_constraints(group.polyRep.param_constraints, grp_params)
    #
    # group.polyRep.extract_polyrep_from_function(comp, dim, schedule_names,
    #                                    param_names, context_conds,
    #                                    comp_map[comp] + 1,
    #                                    group.polyRep.param_constraints)
    # return
