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

MACHINE_TYPE = ['personal', 'mcastle1', 'mcastle2'][1]
    
if (MACHINE_TYPE == 'personal'):
    #global IMAGE_ELEMENT_SIZE, L2_CACHE_SIZE, N_CORES, TILING_THRESHOLD, VECTOR_WIDTH_THRESHOLD
    #For Dekstop/Laptop Machine
    IMAGE_ELEMENT_SIZE = 4
    L2_CACHE_SIZE = int(256*1024/IMAGE_ELEMENT_SIZE)
    N_CORES = 4
    TILING_THRESHOLD = 1
    VECTOR_WIDTH_THRESHOLD = 16
elif (MACHINE_TYPE == 'mcastle1'): #Intel Haswell machine
    #global IMAGE_ELEMENT_SIZE, L2_CACHE_SIZE, N_CORES, TILING_THRESHOLD, VECTOR_WIDTH_THRESHOLD
    #For mcastle
    IMAGE_ELEMENT_SIZE = 4
    L2_CACHE_SIZE = int(512*1024/IMAGE_ELEMENT_SIZE)
    N_CORES = 16
    TILING_THRESHOLD = 1
    VECTOR_WIDTH_THRESHOLD = 64 #TODO: 
    L2_INNER_MOST_DIM_SIZE = 256
    L1_INNER_MOST_DIM_SIZE = 256
    L1_CACHE_SIZE = int(32*1024/IMAGE_ELEMENT_SIZE)
    OUTER_DIM_TILING_THRESH = 4
    THRESHOLD_TILE_SIZE = 4
elif (MACHINE_TYPE == 'mcastle2'): #AMD Opteron machine
    #global IMAGE_ELEMENT_SIZE, L2_CACHE_SIZE, N_CORES, TILING_THRESHOLD, VECTOR_WIDTH_THRESHOLD
    #For mcastle
    IMAGE_ELEMENT_SIZE = 4
    L2_CACHE_SIZE = int(2*512*1024/IMAGE_ELEMENT_SIZE)
    N_CORES = 16
    TILING_THRESHOLD = 1
    VECTOR_WIDTH_THRESHOLD = 64 #TODO: 
    L2_INNER_MOST_DIM_SIZE = 256
    L1_INNER_MOST_DIM_SIZE = 128
    L1_CACHE_SIZE = int(16*1024/IMAGE_ELEMENT_SIZE)
    OUTER_DIM_TILING_THRESH = 4
    THRESHOLD_TILE_SIZE = 4

    
def get_next_power_of_2 (num):
    num -= 1
    num |= num >> 1
    num |= num >> 2
    num |= num >> 4
    num |= num >> 8
    num |= num >> 16
    num |= num >> 32
    num += 1
    
    return num

def is_power_of_2 (num):
    return (num & (num-1)) == 0
    
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


class ComputeTypes:
    FUNCTION = 1
    IMAGE = 2
    REDUCTION = 3
    TSTENCIL = 4


class ComputeObject:
    def __init__(self, _func, _is_output=False):

        self._set_type(_func)

        self._is_parents_set = False
        self._is_children_set = False
        self._is_group_set = False

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

    def clone (self):
        comp = ComputeObject (self._func, self._is_output)
        comp._parents = list(self.parents)
        comp._is_parents_set = self._is_parents_set
        comp._is_children_set = self._is_children_set
        comp._is_group_set = self._is_group_set
        comp._children = list(self.children)
        self._orig_storage_class = comp._orig_storage_class
        self._storage_class = comp._storage_class
        self._array = comp._array
        self._scratch_info = comp._scratch_info
        return comp
        
    def __str__ (self):
        return self._func.name
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
    def compute_type(self):
        return self._compute_type

    @property
    def is_func_type(self):
        return self._compute_type == ComputeTypes.FUNCTION
    @property
    def is_image_typ(self):
        return self._is_image_typ
    @property
    def is_reduction_typ(self):
        return self._compute_type == ComputeTypes.REDUCTION
    @property
    def is_tstencil_type(self):
        return self._compute_type == ComputeTypes.TSTENCIL

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

    def _set_type(self, _func):
        self._compute_type = None
        # NOTE: do NOT change this to if-elif-elif...else
        # since this is an _inheritance hierarchy. Somthing can be a
        # Function AND a reduction.
        if isinstance(_func, Function):
            self._compute_type = ComputeTypes.FUNCTION
        if isinstance(_func, Image):
            self._compute_type = ComputeTypes.IMAGE
        if isinstance(_func, Reduction):
            self._compute_type = ComputeTypes.REDUCTION
        if isinstance(_func, TStencil):
            self._compute_type = ComputeTypes.TSTENCIL

        if self._compute_type is None:
            raise TypeError("unknown compute object function type:\n"
                            "Given: %s\n"
                            "nType: %s" % (self._func, type(self.function)))
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
        if self.is_tstencil_type:
            assert isinstance(_array, tuple)
            assert len(_array) == 2
            assert isinstance(_array[0], genc.CArray)
            assert isinstance(_array[1], genc.CArray)
            self._array = _array
        else:
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
    # Adding _initialization_complete param, Decides if initialization for reduction matrix is required or not.
    def __init__(self, _ctx, _comp_objs, _param_constraints, _initialization_complete):

        self._id = IdGen.get_grp_id()

        log_level = logging.DEBUG

        # All the computation constructs in the language derive from the
        # Function class. Input images cannot be part of a group.
        self._is_image_typ = False
        for comp in _comp_objs:
            assert (isinstance(comp, ComputeObject))
            if comp.is_image_typ:
                self._is_image_typ = True
        self._comps = _comp_objs
        self._parents = []
        self._children = []

        self._set_type()
        self.set_comp_group()

        self._level_order_comps = self.order_compute_objs()
        self._comps = self.get_sorted_comps()
        self._inputs = self.find_root_comps()
        self._live_outs = None
        self._image_refs = self.collect_image_refs()

        self._children_map = None
        self._polyrep = None
        self._initialization_complete = _initialization_complete
        self._tile_sizes = {}

        # Create a polyhedral representation if possible.
        # Currently doing extraction only when all the compute_objs
        # domains are affine. This can be revisited later.
        if self.isPolyhedral():
            self._polyrep = PolyRep(_ctx, self, [], _param_constraints)

        self._comps_schedule = None
        self._liveness_map = None
        self._can_be_mapped_to_lib = False

        self._total_used_size = -1
    
    @property
    def tile_sizes(self):
        return self._tile_sizes
    @property
    def initialization_complete(self):
        return self._initialization_complete
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

    # NOTE: Current assumptions:
    # (1). A Reduction group, TStencil group, and Image group has only one
    # compute object of the respective kind.
    # (2). If a group is of pure function type, all its compute objects are
    # of Function type, and not one of the types listed in (1).
    @property
    def is_func_type(self):
        return self._group_type == ComputeTypes.FUNCTION
    @property
    def is_image_typ(self):
        return self._is_image_typ
    @property
    def is_reduction_typ(self):
        return self._group_type == ComputeTypes.REDUCTION
    @property
    def is_tstencil_type(self):
        return self._group_type == ComputeTypes.TSTENCIL

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

    def set_tile_size_for_dim(self, size, dim):
        self._tile_sizes [dim] = size
        
    def _set_type(self):
        '''
        Depends on how specifically the ComputeObject's type was set, since all
        types inherit from Function type.
        '''
        group_type = ComputeTypes.FUNCTION
        for comp in self._comps:
            group_type = comp.compute_type
            if not group_type == ComputeTypes.FUNCTION:
            # Ideally this case won't occur when the list of group's comps has
            # more than one compute object, since as of now, we group only a
            # bunch of pure compute objects. Images need no fusion since they
            # are program inputs. Fusion and/or tiling optimizations for
            # Reductions is not yet covered. TStencils will be standalone
            # groups if diamond tiling is enabled.
            # TODO: add flag to decide if TStencils are to be Diamond tiled or
            # Overlap tiled.
                break
        self._group_type = group_type
        return

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
            if self.polyRep is not None:
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

    def get_total_size(self, param_estimates):
        size = 0
        visitor = CountMemRefsExpVisitor ()
        get_size_visitor = GetSizeVisitor (param_estimates)
        
        for comp in self.comps:
            for ast_node in comp.func.defn:
                
                expr = None
                
                sizes = comp.compute_size ()
                dim_size = 1
                for _size in sizes:
                    dim_size = dim_size*_size[1].visit (get_size_visitor)
                    
                if (isinstance (ast_node, Case)):
                    expr = ast_node.expression
                elif (isinstance (ast_node, AbstractExpression)):
                    expr = ast_node
                elif (isinstance (ast_node, Reduce)):
                    expr = ast_node.expression
                    if (isinstance (expr, Reduce)):
                        expr = expr.expression
                
                size += dim_size*expr.visit (visitor)
        
        return size
    
    def get_max_live_size(self, param_estimates):
        '''Returns maximum live data size for the group.
        The return value is in terms of number of image elements.
        The return value has to be multiplied with the size of each 
        image element.
        '''
       
        max_size = 0
        visitor = CountMemRefsExpVisitor ()
        get_size_visitor = GetSizeVisitor (param_estimates)
        
        for comp in self.comps:
            size = 0
            sizes = comp.compute_size ()
            dim_size = 1
            for _size in sizes:
                dim_size = dim_size*_size[1].visit (get_size_visitor)
            
            
            size = dim_size*len(comp.parents)
            max_size = max (max_size, size)
        
        
        return max_size
        
    def get_dimensional_reuse2 (self, param_estimates):
        class Interval (object):
            def __init__ (self, lb, ub):
                self.lb = lb
                self.ub = ub
                
        source_comps = []
        for comp in self.comps:
            parent_in = False
            for _parent in comp.parents:
                if _parent in self.comps:
                    parent_in = True
                    break
            
            if (not parent_in):
                source_comps.append (comp)
        
        get_size_visitor = GetSizeVisitor (param_estimates)
        
        def dimensional_reuse (dim, interval1, interval2, 
                               param_estimates, get_size_visitor):
            if (dim >= len (interval1) or dim >= len (interval2)):
                return None
            lb1 = interval1[dim].lowerBound.visit (get_size_visitor)
            lb2 = interval2[dim].lowerBound.visit (get_size_visitor)
            ub1 = interval1[dim].upperBound.visit (get_size_visitor)
            ub2 = interval2[dim].upperBound.visit (get_size_visitor)
            
            if (lb1 <= ub2 and ub1 <= lb2):
                return Interval (ub1, lb2)
            
            return None
        
        max_dim = 0
        for comp in self.comps:
            max_dim = max (max_dim, comp.func.ndims)
        
        dim_interval = [-1 for i in range (0, max_dim)]
        
        for _dim in range (0, max_dim):
            stack = list (source_comps)
            
            while stack.size() != 0:
                
                s = stack.pop ()
                
                for child in s.children ():
                    pass
    
    def get_size_for_each_dim (self, param_estimates):
        max_dim = 0
        for comp in self.comps:
            max_dim = max (max_dim, comp.func.ndims)
            
        dim_sizes = [0 for i in range (0, max_dim)]
        
        get_size_visitor = GetSizeVisitor (param_estimates)
        
        for comp in self.comps:
            intervals = comp.func.domain
           
            for dim in range (comp.func.ndims):
                lb = intervals[dim].lowerBound
                
                lb = lb.visit (get_size_visitor)
               
                ub = intervals[dim].upperBound
              
                ub = ub.visit (get_size_visitor)
                
                size = ub - lb + 1
                
             
                
                dim_sizes [dim] = size

        return dim_sizes
        
    def get_dimensional_reuse (self, param_estimates):
        '''Returns the dimensional reuse in each dimension. 
        Reurns a list of dimensional reuse for each dimension.
        Dimensional Reuse is in terms of number of 4 Bytes.
        optgrouping multiplies the dimensional reuse with 4 Bytes.
        '''
       
        max_dim = 0
        for comp in self.comps:
            max_dim = max (max_dim, comp.func.ndims)
        
        dim_reuse = [0 for i in range (0, max_dim)]
        
        get_size_visitor = GetSizeVisitor (param_estimates)
        
        for comp in self.comps:
            intervals = comp.func.domain
           
            
            if isinstance(comp.func, Reduction):
                continue
                
            for dim in range (comp.func.ndims):
               
                lb = intervals[dim].lowerBound
                
                lb = lb.visit (get_size_visitor)
               
                ub = intervals[dim].upperBound
               
                ub = ub.visit (get_size_visitor)
               
                size = ub - lb + 1
                
                first_iter = lb + int((ub - lb)/2)
                second_iter = first_iter + 1
                first_iter_visitor = MemRefsAtIterationVisitor (dim, first_iter)
                second_iter_visitor = MemRefsAtIterationVisitor (dim, second_iter)
                mem_ref_at_second_iter = set()
                mem_ref_at_first_iter = set()
                
                for ast_node in comp.func.defn:
                    expr = None
                    if (isinstance (ast_node, Case)):
                        expr = ast_node.expression
                    elif (isinstance (ast_node, AbstractExpression)):
                        expr = ast_node
                    elif (isinstance (ast_node, Reduce)):
                        expr = ast_node.expression
                        if (isinstance (expr, Reduce)):
                            expr = expr.expression
                    expr.visit(first_iter_visitor)
                    
                    mem_ref_at_first_iter = mem_ref_at_first_iter.union (set(first_iter_visitor.dim_refs))
                    expr.visit(second_iter_visitor)
                    mem_ref_at_second_iter = mem_ref_at_second_iter.union (set(second_iter_visitor.dim_refs))
                
                dim_reuse_iters = mem_ref_at_second_iter.intersection (mem_ref_at_first_iter)
                dim_size = 1
                dim_reuse[dim] += len (dim_reuse_iters)*dim_size
        
        return dim_reuse
    
    def is_dim_tileable (self, dim, slope_min, dim_size):
        return slope_min [dim] != '*' and dim_size[dim] != 0

    def set_total_used_size (self, total_used_size):
        self._total_used_size = total_used_size
    def set_n_buffers (self, n_buffers):
        self._n_buffers = n_buffers
    def set_type_of_access (self, param_estimates):
        '''Returns and array of type of access
        Each type is "rectangular" if accesses are more rectangular i.e.
        f(x,y) = in(x, y-2)+in(x, y-1)+in(x,y)+in(x,y+1)+in(x,y+2)
        Or "sqaurer" if accesses are more squarer i.e.
        f(x,y) = img(x-1, y-1)*(-1.0/12) + img(x-1, y+1)*(1.0/12) + \
                           img(x, y-1)*(-2.0/12) + img(x, y+1)*(2.0/12) + \
                           img(x+1, y-1)*(-1.0/12) + img(x+1, y+1)*(1.0/12)
        '''
       
        max_dim = 0
        for comp in self.comps:
            max_dim = max (max_dim, comp.func.ndims)
        
        dim_reuse = [0 for i in range (0, max_dim)]
        access_types = []
        
        get_size_visitor = GetSizeVisitor (param_estimates)
        
        for comp in self.comps:
            intervals = comp.func.domain
            
            if isinstance(comp.func, Reduction):
                continue
            
            dims_lb = []
            
            for dim in range (comp.func.ndims):
                lb = intervals[dim].lowerBound
                lb = lb.visit (get_size_visitor)
                dims_lb.append (lb+1)
            
            access_type_visitor = AccessTypesVisitor (dims_lb, param_estimates)
            mem_refs = set()
                
            for ast_node in comp.func.defn:
                expr = None
                if (isinstance (ast_node, Case)):
                    expr = ast_node.expression
                elif (isinstance (ast_node, AbstractExpression)):
                    expr = ast_node
                elif (isinstance (ast_node, Reduce)):
                    expr = ast_node.expression
                    if (isinstance (expr, Reduce)):
                        expr = expr.expression
                        
                expr.visit(access_type_visitor)
                
                #mem_refs = mem_refs.union (set(access_type_visitor._refs))
        
            print (dims_lb, comp.func.name,)
            s = ""
            for d in access_type_visitor._refs:
                s += "["
                for g in d:
                    s += str(g) + ", "
                s += "] "
            print (s)
            
            references = access_type_visitor._refs
            for ref in references:
                ref_types = []
                __dim = 0
                for ref_dim in ref:
                    if (ref_dim is Variable):
                        ref_types += "variable"
                    elif (ref_dim is AbstractBinaryOpNode):
                        if (ref_dim.op == '+' or ref_dim == '-'):
                            if ((ref_dim.left is Variable or ref_dim.left is Value) and
                                (ref_dim.right is Variable or ref_dim.right is Value)):
                                pass#ref_types += 
                                
                    else:
                        raise Exception ("Case Not Handled for ref type")
                        
            
        self._access_types = access_types
        
        return access_types
        
    def get_tile_sizes2 (self, param_estimates, slope_min, group_parts):
        #self._tile_sizes = {1:8, 2:256}
        #print ("total_size ", self._total_used_size/IMAGE_ELEMENT_SIZE)
        #self._tile_sizes = {1:1, 2:256}
        #return
        if (self._total_used_size == -1):
            #print (self)
            assert (False)
            
        tileable_dims = set()
        
        dim_reuse = [i*IMAGE_ELEMENT_SIZE for i in self.get_dimensional_reuse (param_estimates)]
        
        dim_sizes = {}
        
        for i in range(1, len(slope_min) + 1):
            # Check if every part in the group has enough iteration
            # points in the dimension to benefit from tiling.
            tile = False
            for part in group_parts:
                lower_bound = part.sched.range().dim_min(i)
                upper_bound = part.sched.range().dim_max(i)
                size = upper_bound.sub(lower_bound)
                if (size.is_cst() and size.n_piece() == 1):
                    aff = (size.get_pieces())[0][1]
                    val = aff.get_constant_val()
                    #print (val, i)
                    if (val > TILING_THRESHOLD):
                        if i-1 in dim_sizes:
                            dim_sizes[i-1] = min (val.to_python(), dim_sizes[i-1])
                        else:
                            dim_sizes[i-1] = val.to_python()
                    else:
                        if i-1 not in dim_sizes:
                            dim_sizes [i-1] = 0
        

        total_used_size = self._total_used_size/IMAGE_ELEMENT_SIZE
        tile_size = total_used_size/N_CORES
        if (tile_size > L2_CACHE_SIZE):
            tile_size = L2_CACHE_SIZE
        tile_size = tile_size/self._n_buffers
        print ("tile_size is ", tile_size)
        input ("324342343423")
        input ("1111")
        if (is_power_of_2 (int(tile_size)) == False):
            tile_size = get_next_power_of_2 (int(tile_size))
        
        max_dim_reuse = 0
        max_dim = -1
        n_tileable_dims = 0
        
        for i in range (len(slope_min)):
            if self.is_dim_tileable (i, slope_min, dim_sizes):
                n_tileable_dims+=1
        
        if (n_tileable_dims == 0):
            self._tile_sizes = {}
            for dim in range (len(slope_min)):
                self._tile_sizes [dim] = int(get_next_power_of_2 (int(tile_size ** (1.0/len(slope_min))))/2)
            
            return 
            
        for i in range (len(slope_min)):
            if self.is_dim_tileable (i, slope_min, dim_sizes):
                if (max_dim_reuse < dim_reuse [i]):
                    max_dim_reuse = dim_reuse[i]
                    max_dim = i
        
        max_dim_tile_size = tile_size
        n_non_zero_dims = 0
        
        for i in range (len(slope_min)):
            if self.is_dim_tileable (i, slope_min, dim_sizes):
                if (dim_reuse [i] != 0):
                    n_non_zero_dims += 1
                    max_dim_tile_size = max_dim_tile_size * (max_dim_reuse/dim_reuse [i])
        
        tile_sizes_product = 1
        tile_sizes = {}
        
        if (n_non_zero_dims > 0):
            max_dim_tile_size = max_dim_tile_size ** (1.0/n_non_zero_dims)
                    
            for i in range (len(slope_min)):
                if self.is_dim_tileable (i, slope_min, dim_sizes):
                    if (dim_reuse[i] != 0):
                        tile_sizes [i] = int(max_dim_tile_size * dim_reuse[i]/max_dim_reuse)
                        
                        if (tile_sizes [i] > dim_sizes [i]):
                            tile_sizes [i] = dim_sizes [i]
                        
                        print (str(i)+": "+str(tile_sizes[i]))
                        tile_sizes_product *= tile_sizes [i]
        
        n_zero_dim_reuse = n_tileable_dims - n_non_zero_dims
            
        if (n_zero_dim_reuse > 0 and tile_sizes_product < tile_size):
            tile_size_for_zero_dim = (tile_size/tile_sizes_product)**(1.0/n_zero_dim_reuse)
            tile_size_for_zero_dim = int(tile_size_for_zero_dim)
            for i in range (len(slope_min)):
                if i not in tile_sizes and self.is_dim_tileable (i, slope_min, dim_sizes):
                    tile_sizes[i] = tile_size_for_zero_dim
        
        tile_sizes_product = 1
        for k in tile_sizes.keys():
            if tile_sizes [k] != 0 and (tile_sizes [k] & (tile_sizes [k] - 1)) != 0:
                new_tile_size = get_next_power_of_2 (tile_sizes [k])
                tile_sizes [k] = new_tile_size
                
            tile_sizes_product *= tile_sizes [k]
                
        if (tile_sizes_product > tile_size):
            times = tile_sizes_product/tile_size
            
            max_dim = 0
            max_tile_size = 0
            for k in tile_sizes.keys():
                if (max_tile_size < tile_sizes[k]):
                    max_tile_size = tile_sizes[k]
                    max_dim = k
                    
            tile_sizes[max_dim] = int(tile_sizes[max_dim]/times)
            
        if (tile_sizes_product < tile_size):
            remaining_tile_size = int((tile_size/tile_sizes_product)**(1.0/n_tileable_dims))
            if (remaining_tile_size & (remaining_tile_size - 1) != 0):
                remaining_tile_size = get_next_power_of_2 (remaining_tile_size)/2
                remaining_tile_size = int(remaining_tile_size)
            
            for k in tile_sizes.keys():
                tile_sizes[k] *= remaining_tile_size
        
        vec_dim = max(tile_sizes)
        if (tile_sizes [vec_dim] < VECTOR_WIDTH_THRESHOLD):
            tile_sizes[vec_dim] = int(get_next_power_of_2 (int(dim_sizes[vec_dim])))
        
        print ("tile_sizes ", tile_sizes)
        par_dim = min(tile_sizes)
        _tile_sizes = dict (tile_sizes)
        while (dim_sizes[par_dim]/N_CORES < N_CORES):
            _tile_sizes.pop (par_dim)
            if (_tile_sizes != {}):
                par_dim = min (_tile_sizes)
            else:
                par_dim = -1
                break
            
        print ("tile_sizes ", tile_sizes, "par_dim ", par_dim)
        #par_dim = -1
        if (par_dim != -1):
            n_threads = dim_sizes[par_dim]/tile_sizes[par_dim]
            if (n_threads < N_CORES):
                #If number of threads to be created are less than number of cores then, 
                #set the tile size such that number of threads are greater than cores
                tile_sizes[par_dim] = int(get_next_power_of_2 (int(dim_sizes[par_dim]/N_CORES))/2)
            elif (n_threads >= N_CORES):
                #Since, n_threads > N_CORES, all can still be executed in parallel.
                #Hence, it is fine
                #tile_sizes [par_dim] = 1
                pass       
        print ("tile_sizes3333", tile_sizes, " dim_sizes[par_dim] = ") 
        if (par_dim != -1 and tile_sizes [par_dim] == 0):
            tile_sizes [par_dim] = 1
            
        for k in tile_sizes.keys ():
            if (k != par_dim and k != vec_dim and tile_sizes [k] > dim_sizes[k]):
                tile_sizes[k] = int(get_next_power_of_2 (int(dim_sizes[k]))/2)
       
        print ("tile_sizes222", tile_sizes) 
        to_remove = []
        for k in tile_sizes.keys():
            if (tile_sizes [k] == 0):
                to_remove.append (k)
        
        for k in to_remove:
            tile_sizes.pop (k)
            
        self._tile_sizes = tile_sizes
        
        for k in tile_sizes.keys():
            pass #assert (is_power_of_2 (tile_sizes [k]))
        
        tile_sizes_product = 1
        for k in tile_sizes.keys():
            tile_sizes_product *= tile_sizes[k]

    def get_tile_sizes_for_cache_size (self, param_estimates, slope_min,
                                       slope_max, group_parts, dim_reuse, 
                                       dim_sizes, CACHE_SIZE, LAST_DIM_SIZE,
                                       tile_size = -1):
        '''Returns the tile size found
        '''
        tile_sizes = {}
        if (tile_size == -1):
            total_used_size = self._total_used_size/IMAGE_ELEMENT_SIZE
            tile_size = total_used_size/N_CORES
            if (tile_size > CACHE_SIZE):
                tile_size = CACHE_SIZE
            tile_size = tile_size/self._n_buffers
            
        print ("tileable dims:",)
        for i in range (len(slope_min)):
            if (self.is_dim_tileable (i, slope_min, dim_sizes)):
                print (i,)

        print ("tile_size ", tile_size)
        print ("dim_reuse ", dim_reuse)
        if (is_power_of_2 (int(tile_size)) == False):
            pass#tile_size = get_next_power_of_2 (int(tile_size))/2
            
        print ("tile_size power of two ", tile_size)
        print ("dim_sizes ", dim_sizes)
        last_tileable_dim = None
        n_tileable_dims = 0
        max_dim_reuse = 0
        n_non_zero_dims = 0
        n_zero_dims = 0
        outer_tileable_dim = -1
        
        for i in range (len(slope_min)):
            if self.is_dim_tileable (i, slope_min, dim_sizes):
                n_tileable_dims+=1
                last_tileable_dim = i
                if (outer_tileable_dim == -1 and 
                    dim_sizes[i] < OUTER_DIM_TILING_THRESH):
                    outer_tileable_dim = i
            else:
                outer_tileable_dim = i

        #zero_dim_reuse_size = []
        #for i in range (len(slope_min)):
            #if self.is_dim_tileable (i, slope_min, dim_sizes) and i != last_tileable_dim:
                #if (dim_reuse [i] == 0):
                    #max_val = -1
                    #for part in group_parts:
                        #lower_bound = part.sched.range().dim_min(i+1)
                        #upper_bound = part.sched.range().dim_max(i+1)
                        #size = upper_bound.sub(lower_bound)
                        #if (size.is_cst() and size.n_piece() == 1):
                            #aff = (size.get_pieces())[0][1]
                            #val = aff.get_constant_val()
                            #max_val = max(max_val, val.to_python())
                    
                    #zero_dim_reuse_size.append (max_val)
                        
        if (n_tileable_dims == 0):
            self._tile_sizes = {}
            for dim in range (len(slope_min)):
                tile_sizes [dim] = int(get_next_power_of_2 (int(tile_size ** (1.0/len(slope_min))))/2)
            
            tile_sizes [max(tile_sizes)] = INNER_MOST_DIM_SIZE
            
            return tile_sizes
        
        print ('last_tileable_dim ', last_tileable_dim)
        print ('outer_tileable_dim ', outer_tileable_dim)
        tile_sizes [last_tileable_dim] = min (dim_sizes[last_tileable_dim], LAST_DIM_SIZE)
        remaining_tile_size = tile_size/tile_sizes [last_tileable_dim]
        #for s in zero_dim_reuse_size:
            #remaining_tile_size = remaining_tile_size/s
        
        if (outer_tileable_dim != -1 and dim_sizes[outer_tileable_dim] != 0):
            remaining_tile_size = remaining_tile_size/dim_sizes[outer_tileable_dim]
            
        for i in range (len(slope_min)):
            if (self.is_dim_tileable (i, slope_min, dim_sizes) and 
                i != last_tileable_dim and i != outer_tileable_dim):
                if (max_dim_reuse < dim_reuse [i]):
                    max_dim_reuse = dim_reuse[i]
                    max_dim = i
        
        max_dim_tile_size = remaining_tile_size
        for i in range (len(slope_min)):
            if (self.is_dim_tileable (i, slope_min, dim_sizes) and 
                i != last_tileable_dim and i != outer_tileable_dim):
                if (dim_reuse [i] != 0):
                    n_non_zero_dims += 1
                    max_dim_tile_size = max_dim_tile_size * (max_dim_reuse/dim_reuse [i])
                else:
                    n_zero_dims +=1
                    
        if (n_non_zero_dims > 0):
            max_dim_tile_size = max_dim_tile_size ** (1.0/n_non_zero_dims)
                    
            for i in range (len(slope_min)):
                if (self.is_dim_tileable (i, slope_min, dim_sizes) and 
                    i != last_tileable_dim and i != outer_tileable_dim):
                    if (dim_reuse[i] != 0):
                        tile_sizes [i] = int(max_dim_tile_size * dim_reuse[i]/max_dim_reuse)
                        
                        if (tile_sizes [i] > dim_sizes [i]):
                            tile_sizes [i] = dim_sizes [i]
        
        if (n_non_zero_dims == 0):
            max_dim_tile_size = max_dim_tile_size ** (1.0/n_zero_dims)
            
            for i in range (len(slope_min)):
                if (self.is_dim_tileable (i, slope_min, dim_sizes) and i != last_tileable_dim
                    and i != outer_tileable_dim):
                    if (max_dim_tile_size > dim_sizes [i]):
                        n_zero_dims -= 1
                        max_dim_tile_size = max_dim_tile_size ** (1.0/n_zero_dims)
            
            for i in range (len(slope_min)):
                if (self.is_dim_tileable (i, slope_min, dim_sizes) and i != last_tileable_dim
                    and i != outer_tileable_dim):
                    tile_sizes [i] = int (max_dim_tile_size)
        
        _tile_sizes = dict(tile_sizes)
        
        for k in tile_sizes.keys():
            if (tile_sizes[k] == 0):
                _tile_sizes.pop (k)
            
        return _tile_sizes
            
    def get_tile_sizes (self, param_estimates, slope_min, slope_max, group_parts, 
                        h, use_only_l2 = False, tile_size = -1):
        print ("get_tile_sizes for ", self)
        #self._tile_sizes = {1:8, 2:256}
        #print ("total_size ", self._total_used_size/IMAGE_ELEMENT_SIZE)
        #self._tile_sizes = {1:32, 2:256}
        #return
        if (str(self) == "[1Dx_1_img2, Dy_1_img2, Ux_0_img2, Dx_2_img2]"):
            self._tile_sizes = {1:32, 2:256}
            return
        if (self._total_used_size == -1):
            #print (self)
            assert (False)
            
        tileable_dims = set()
        
        dim_reuse = [i*IMAGE_ELEMENT_SIZE for i in self.get_dimensional_reuse (param_estimates)]
        
        dim_sizes = {}
        
        for i in range(1, len(slope_min) + 1):
            # Check if every part in the group has enough iteration
            # points in the dimension to benefit from tiling.
            tile = False
            for part in group_parts:
                lower_bound = part.sched.range().dim_min(i)
                upper_bound = part.sched.range().dim_max(i)
                size = upper_bound.sub(lower_bound)
                if (size.is_cst() and size.n_piece() == 1):
                    aff = (size.get_pieces())[0][1]
                    val = aff.get_constant_val()
                    print (val, i-1)
                    if (val > TILING_THRESHOLD):
                        if i-1 in dim_sizes:
                            dim_sizes[i-1] = max (val.to_python(), dim_sizes[i-1])
                        else:
                            dim_sizes[i-1] = val.to_python()
                    else:
                        if i-1 not in dim_sizes:
                            dim_sizes [i-1] = 0
        
        self._dim_sizes_part = dim_sizes
        
        if (not use_only_l2):
            #try with L1 Cache
            tile_sizes = self.get_tile_sizes_for_cache_size (param_estimates, 
                slope_min, slope_max, group_parts, dim_reuse, dim_sizes, L1_CACHE_SIZE, L1_INNER_MOST_DIM_SIZE)
            
            overlap_shift_greater = False
            
            for i in tile_sizes.keys ():
                right = int(math.floor(Fraction(slope_min[i][0],
                                                slope_min[i][1])))
                left = int(math.ceil(Fraction(slope_max[i][0],
                                            slope_max[i][1])))
                # Compute the overlap shift
                overlap_shift = abs(left * (h)) + abs(right * (h))
                    
                if (overlap_shift + 0 > tile_sizes[i]):
                    overlap_shift_greater = True
                    break
            
            threshold_tile_size_met = True
            for i in tile_sizes.keys ():
                pass#if tile_sizes[i] < THRESHOLD_TILE_SIZE:
                    #threshold_tile_size_met = False
                    #break
                    
            print ("tile_sizes from L1 ", tile_sizes)
            
            if (not overlap_shift_greater and threshold_tile_size_met):
                self._tile_sizes = tile_sizes
                return 

        tile_sizes = self.get_tile_sizes_for_cache_size (param_estimates, 
            slope_min, slope_max, group_parts, dim_reuse, dim_sizes, 
            L2_CACHE_SIZE, L2_INNER_MOST_DIM_SIZE, tile_size)
        
        print ("tile_sizes from L2 ", tile_sizes)
        self._tile_sizes = tile_sizes
        
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

        if 'pluto' in self.options:
            self._pluto_sched_required = True
        else:
            self._pluto_sched_required = False

        self._dim_reuse = {}

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
            group = Group(self._ctx, comps, self._param_constraints, self._pluto_sched_required)
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
                self.initialize_storage()
                auto_group(self)
                pass
            self._level_order_groups = self.order_group_objs()

        
        ''' GRAPH UPDATES '''
        # level order traversal of groups

        self._groups = self.get_sorted_groups()

        #TESTING HERE
        if (False):
            self.get_overlapping_size_for_groups ([self.groups[0], self.groups[1], self.groups[2], self.groups[3]])
            
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
                if g.polyRep is None:
                    continue
                # alignment and scaling
                align_and_scale(self, g)
                # base schedule
                base_schedule(g)
                # grouping and tiling
                fused_schedule(self, self._ctx, g, self._param_estimates)
                # idiom matching algorithm
                idiom_recognition(self, g)
                # tile reductions
                #~ self.reduction_tiling(g)

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

    def get_overlapping_size_for_groups (self, groups, tile_size):
        print ("get_overlapping_size_for_groups for ", [g.comps[0].func.name for g in groups])
        g = self.create_group (groups)
        g.set_total_used_size (tile_size)
        #print ("create_group = ", [comp.func.name for comp in g.comps])
        #print ("LEVEL ORDER COMPS", g._level_order_comps)
        #g.get_total_size (self._param_estimates)
        #g.get_dimensional_reuse (self._param_estimates)
        #sys.exit (0)
        # update liveness of compute objects in each new group
        #g.compute_liveness()
        # children map for comps within the group
        #g.collect_comps_children()
        orig_func_map = self.func_map
        _func_map = dict(orig_func_map)
        for comp in g.comps:
            _func_map[comp.func] = comp
        self._func_map = _func_map
        # alignment and scaling
        try:
            align_and_scale(self, g)
        except AssertionError:
            return 1<<30
        base_schedule(g)
        # grouping and tiling
        #print ("fused_schedule232323 ", g)
        g_all_parts = []
        for comp in g.polyRep.poly_parts:
            #print ("poly_parts comp ", hex(id(comp)))
            g_all_parts.extend(g.polyRep.poly_parts[comp])
        #print (g_all_parts)
        # get dependence vectors between each part of the group and each of its
        # parents' part
        comp_deps = get_group_dep_vecs(self, g, g_all_parts, func_map = _func_map)
        #print (comp_deps)
        # No point in tiling a group that has no dependencies
        self._func_map = orig_func_map
        if len(comp_deps) > 0 and len(g_all_parts) > 1:
            hmax = max( [ p.level for p in g_all_parts ] )
            #hmin = min( [ p.level for p in g_all_parts ] )
            slope_min, slope_max = compute_tile_slope(comp_deps, hmax)
            g.get_tile_sizes (self.param_estimates, slope_min, slope_max, 
                              g_all_parts, hmax, True, tile_size)
            tile_sizes = g._tile_sizes
            print ("slope_min, slope_max", slope_min, slope_max)
            overlap_shifts = [0 for i in range(0, len(slope_min))]
            for i in range(2, len(slope_min)+1):
                if (slope_min[i-1] == '*'):
                    continue
                right = int(math.floor(Fraction(slope_min[i-1][0],
                                                slope_min[i-1][1])))
                left = int(math.ceil(Fraction(slope_max[i-1][0],
                                              slope_max[i-1][1])))
                for h in range(1, get_group_height (g_all_parts)+1):
                    overlap_shifts [i-1] += abs(left * (h)) + abs(right * (h))
                #print (_overlap_shift, i)
                #if (_overlap_shift != 0):
                #    overlap_shift *= _overlap_shift
            print ("overlap_shifts ", overlap_shifts)
            overlap_shift = 1
            for i in tile_sizes:
                if (overlap_shifts[i] != 0 and tile_sizes[i] < g._dim_sizes_part[i]):
                    if ((i-1) in tile_sizes):
                        overlap_shift *= overlap_shifts[i]*(tile_sizes[i-1] + overlap_shifts[i-1])
                    else:
                        overlap_shift *= overlap_shifts[i]*1
            #overlap_shift *= IMAGE_ELEMENT_SIZE
            #print ("overlap_shift ", overlap_shift)
            return overlap_shift
        
        if len (comp_deps) <= 0:
            return 1 << 30
            
        print ("Getting Overlap for non stencil? Not Good")
        assert (False)
        
    @property
    def dim_reuse (self):
        return self._dim_reuse
    @property
    def param_estimates (self):
        return self._param_estimates
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
    def input_groups(self):
        return self._inp_groups
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

    def get_tile_sizes_for_group (self, group):
        dim_reuse = {}
        
    def dim_reuse_for_each_group (self):
        for group in self.groups:
            self._dim_reuse [group.comps[0]] = group.get_dimensional_reuse (self.param_estimates)
        
    def create_group(self, args):
        groups = args
        comps = []
        for g in groups:
            comps += g.comps
        
        comp_to_clone = dict ()
        for i in range(len(comps)):
            #print ("comps [i] ", hex(id(comps[i])),)
            cloneComp = comps[i].clone()
            comp_to_clone [comps[i]] = cloneComp
            comps[i] = cloneComp
            #print ("clone comps [i] ", hex(id(comps[i])))
        
        for i in range(len(comps)):
            for j in range(len(comps[i].parents)):
                if (comps[i].parents[j] in comp_to_clone):
                    comps[i].parents[j] = comp_to_clone[comps[i].parents[j]]
            for j in range(len(comps[i].children)):
                if (comps[i].children[j] in comp_to_clone):
                    comps[i].children[j] = comp_to_clone[comps[i].children[j]]
                
        print (comps)
        return Group (self._ctx, comps, self._param_constraints)

    def get_size_for_group (self, group):
        size = group.get_total_size ()
        
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
            # Generate inital Schedule.
            # Required for generating dependencies
            base_schedule_for_matrix_ops(group)
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
            deps_union_map = isl.UnionMap.read_from_str(self._ctx, '{}')

        # Pluto call
        pluto = LibPluto()
        pluto_options = pluto.create_options()
        # Returns transformed schedule and parallael loops for each statement
        out_schedule,parallel_loops = pluto.schedule(self._ctx, domain_union_set, deps_union_map, pluto_options)

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
            else:
                for i, var in enumerate(poly_part.func.variables):
                    new_sched = new_sched.set_dim_name(isl.dim_type.in_, i, var.name)
            poly_part.sched = new_sched

            num_out_dims = poly_part.sched.dim(isl.dim_type.out)
            num_in_dims = poly_part.sched.dim(isl.dim_type.in_)

            stmt_num = poly_part.stmt_no

            inv_map = np.array(pluto.remapping.inv_matrices[stmt_num], dtype=object)

            # inv_map = inv_map[0:num_in_dims, 0:num_out_dims]
            # inv_map = inv_map.transpose()
            # for dim in range(num_out_dims):
            #     poly_part.scalar[dim] = np.sum(inv_map[dim])
            divs = pluto.remapping.divs[stmt_num] #[0:num_in_dims]

            poly_part.set_pluto_inv_and_div_matrix(inv_map,divs)

            # Tiled check
            if num_out_dims >= (2 * num_in_dims):
                poly_part.tiled = True
            else:
                poly_part.tiled = False

            # Mark parallel and vector loops
            # TODO: Check if vector loop is being set correctly
            mark_par_and_vec_for_pluto_sched(poly_part, parallel_loops[stmt_num])


        return

    def reduction_tiling(self, group):
        self.pluto_to_polymage_fname_map = {}

        domain_union_set = None
        deps_union_map = None
        sched_union_map = None
        read_map = None
        write_map = None
        i = 0

        main_poly_part = []
        for comp in group.comps:
            if not isinstance(comp.func, Reduction):
                return
            poly_parts = group.polyRep.poly_parts[comp]
            if len(poly_parts) == 1: # FFT or IFFT (don't tile in this case)
                return
            for poly_part in poly_parts:
                main_poly_part.append(poly_part)

        LOG(log_level, "Tiling " + group.__str__())

        for poly_part in main_poly_part:
            in_schedule = poly_part.sched.copy()
            domain = in_schedule.domain()
            # Create Pluto compatible statement names
            domain = self.get_updated_pluto_domain(self, i, domain)
            poly_part.stmt_no = i
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
        LOG(log_level, "Initial Schedule:    " + str(sched_union_map))

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
            deps_union_map = isl.UnionMap.read_from_str(self._ctx, '{}')

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
            LOG(log_level, "Original Schedule")
            LOG(log_level, in_schedule)
            in_domain = in_schedule.domain()
            func_sched_name = in_schedule.get_tuple_name(isl._isl.dim_type.in_)
            new_sched = self.function_schedule_map[func_sched_name]

            # Removes any scalar dimensions
            new_sched = new_sched.copy().get_basic_maps()[0]
            num_out_dim = new_sched.range().n_dim()
            # Assigning dimension name for out dimension. Required for building ast
            new_sched = new_sched.set_dim_name(isl.dim_type.out, 0, '_t')
            for i in range(1, num_out_dim):
                new_sched = new_sched.set_dim_name(isl.dim_type.out, i, 'o' + i.__str__())

            # Intersect with domain in order to bound the schedule to the required space
            new_sched = new_sched.intersect_domain(in_domain)

            # Replace in dimensions with variable names
            if isinstance(poly_part.comp.func, Reduction) and not (poly_part.is_default_part):
                for i, var in enumerate(poly_part.func.reductionVariables):
                    new_sched = new_sched.set_dim_name(isl.dim_type.in_, i, var.name)
            else:
                for i, var in enumerate(poly_part.func.variables):
                    new_sched = new_sched.set_dim_name(isl.dim_type.in_, i, var.name)
            LOG(log_level, "Updated Schedule")
            LOG(log_level, new_sched)
            poly_part.sched = new_sched

            num_out_dims = poly_part.sched.dim(isl.dim_type.out)
            num_in_dims = poly_part.sched.dim(isl.dim_type.in_)

            # TODO: Check if statement numbers are retrieved correctly (ordered by polypart or by statment num)
            stmt_num = poly_part.stmt_no

            inv_map = np.array(remapping.inv_matrices[stmt_num], dtype=object)

            # inv_map = inv_map[0:num_in_dims, 0:num_out_dims]
            # inv_map = inv_map.transpose()
            # for dim in range(num_out_dims):
            #     poly_part.scalar[dim] = np.sum(inv_map[dim])
            divs = remapping.divs[stmt_num] #[0:num_in_dims]

            poly_part.set_pluto_inv_and_div_matrix(inv_map,divs)

            # Tiled check
            if num_out_dims >= (2 * num_in_dims):
                poly_part.tiled = True
            else:
                poly_part.tiled = False

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

    def get_weights (self):
        for g in self.groups():
            g_size = g.get_size_for_each_dim (self._param_estimates)
            children_size = []
            
            for child in g.children ():
                children_size.append (g.get_size_for_each_dim (self._param_estimates))
            
        
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

        # initial groups for inputs
        inp_groups = {}
        for inp_func in self.inputs:
            inp_comp = self.func_map[inp_func]
            inp_groups[inp_func] = \
                pipe.Group(self._ctx, [inp_comp], self._param_constraints, self.pluto_sched_required)
            # do not add input groups to the list of pipeline groups
        self._inp_groups = inp_groups

        # initial groups for functions
        comps = self.comps
        groups = []
        for comp in comps:
            group = Group(self._ctx, [comp], self._param_constraints, self.pluto_sched_required)
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
                colour_index = self.storage_map[comp]
                # comp's array mapping
                if comp.is_tstencil_type:
                    node_colour = X11Colours.colour(colour_index[1]) + ";0.5:" + \
                        X11Colours.colour(colour_index[0])
                else:
                    node_colour = X11Colours.colour(colour_index)

                # liveout or not
                node_style = 'rounded,'
                if comp.is_liveout:
                    node_style += 'bold,'
                    node_style += 'filled,'
                    node_shape = 'doublecircle'
                    node_fillcolor = node_colour
                    node_colour = ''
                else:
                    node_style += 'filled,'
                    node_shape = 'box'
                    node_fillcolor = ''

                gr.add_node(comp.func.name,
                    fillcolor=node_fillcolor,
                    color=node_colour,
                    style=node_style,
                    gradientangle=90,
                    shape=node_shape)

            # add group boundary
            gr.add_subgraph(nbunch = sub_graph_nodes,
                            name = "cluster_" + str(i),
                            label=str(self.group_schedule[self.groups[i]]),
                            style="dashed,rounded,")

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
                       self._param_constraints, self.pluto_sched_required)

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
            part_map = {} if comp.group.polyRep is None else comp.group.polyRep.poly_parts
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
#HERE: no element of is_scratch is set to true
            comp.set_scratch_info(is_scratch)

            storage = Storage(typ, ndims, interval_sizes)
            comp.set_orig_storage_class(storage)

            # ***
            LOG(log_level, "  "+comp.func.name)
            LOG(log_level, "    "+str(storage))

        return


# Function to recognize computations which can be mapped to library calls
def idiom_recognition(pipeline, group):
    blas = 'openblas' in pipeline.options or 'mkl' in pipeline.options
    fft = 'fft' in pipeline.options
    if not blas and not fft:
        return
    g_poly_parts = group.polyRep.poly_parts
    for comp in g_poly_parts:
        g_all_comp_parts = []
        g_all_comp_parts.extend(g_poly_parts[comp])
        matrix_mul_found = match_idiom_matrix_mul(g_all_comp_parts)
        sig_fft_found = match_idiom_sig_fft(g_all_comp_parts)
        sig_ifft_found = match_idiom_sig_ifft(g_all_comp_parts)
        if matrix_mul_found:
            if 'pluto' in pipeline.options:
                isPlutoSchedule = True
            else:
                isPlutoSchedule = False
            replace_sched_expr_with_matched_idiom(g_all_comp_parts, isPlutoSchedule, Idiom_type.mat_mat_mul, pipeline._ctx)
            LOG(log_level,"Idiom Match Found for comp: " + comp.func.name)
        elif sig_fft_found:
            zero_part = replace_sched_expr_with_matched_idiom(g_all_comp_parts, False, Idiom_type.sig_fft)
            group.polyRep.poly_parts[comp].remove(zero_part)
            LOG(log_level,"Idiom Match Found for comp: " + comp.func.name)
        elif sig_ifft_found:
            zero_part = replace_sched_expr_with_matched_idiom(g_all_comp_parts, False, Idiom_type.sig_ifft)
            group.polyRep.poly_parts[comp].remove(zero_part)
            LOG(log_level,"Idiom Match Found for comp: " + comp.func.name)
        else:
            LOG(log_level,"No match found for comp: " + comp.func.name)
    return

# Replace schedule and expr of identified computation with lib calls
def replace_sched_expr_with_matched_idiom(g_all_parts, isPlutoSchedule, idiom, ctx=None):
    if idiom == Idiom_type.mat_mat_mul:
        if g_all_parts[0].expr == 0:
            poly_part = g_all_parts[1]
        else:
            poly_part = g_all_parts[0]

        poly_part.is_idiom = True
        tuple_in = poly_part.sched.get_tuple_id(isl._isl.dim_type.in_)
        eqs = []
        ineqs = []
        import pudb; pudb.set_trace();
        if isPlutoSchedule and poly_part.tiled:
            #TODO: Assuming the code is tiled. Need to add a condition to check that
            n_dims = poly_part.sched.dim(isl._isl.dim_type.out)
            if not n_dims >= 3:
                log_level = logging.ERROR
                LOG(log_level, "Wrong number of dimensions found for Idiom Match")
                raise RuntimeError("Number of dimensions did not match with the Idiom")
            # n_dims = n_dims - 3 #(Removing the input dimensions)
            start_dim = n_dims - 3
            log_level = logging.INFO
            LOG(log_level, "Idiom Matching for Pluto Schedule")
            poly_part.sched = poly_part.sched.project_out(isl._isl.dim_type.out,start_dim,3)
        else:
            # When Tiling is not performed or when Pluto schedule is not invoked.
            n_dims = poly_part.sched.dim(isl._isl.dim_type.out)
            if not n_dims >= 3:
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
    elif idiom == Idiom_type.sig_fft:
        if g_all_parts[0].expr == 0:
            poly_part = g_all_parts[1]
            zero_part = g_all_parts[0]
        else:
            poly_part = g_all_parts[0]
            zero_part = g_all_parts[1]

        poly_part.is_idiom = True
        tuple_in = poly_part.sched.get_tuple_id(isl._isl.dim_type.in_)
        eqs = []
        ineqs = []

        n_dims = poly_part.sched.dim(isl._isl.dim_type.out)
        start_dim = n_dims - 2

        for i in range(start_dim, n_dims):
            name = poly_part.sched.get_dim_name(isl._isl.dim_type.out, i)
            coeff = {}
            coeff[('out', name)] = 1
            eqs.append(coeff)

        poly_part.sched = add_constraints(poly_part.sched, ineqs, eqs)
        poly_part.sched = poly_part.sched.set_tuple_id(isl._isl.dim_type.in_, tuple_in)

        return zero_part
    elif idiom == Idiom_type.sig_ifft:
        for poly_part in g_all_parts:
            if poly_part.expr == 0:
                zero_part = poly_part
                continue

            poly_part.is_idiom = True
            tuple_in = poly_part.sched.get_tuple_id(isl._isl.dim_type.in_)
            eqs = []
            ineqs = []

            n_dims = poly_part.sched.dim(isl._isl.dim_type.out)
            start_dim = n_dims - 2

            for i in range(start_dim, n_dims):
                name = poly_part.sched.get_dim_name(isl._isl.dim_type.out, i)
                coeff = {}
                coeff[('out', name)] = 1
                eqs.append(coeff)

            poly_part.sched = add_constraints(poly_part.sched, ineqs, eqs)
            poly_part.sched = poly_part.sched.set_tuple_id(isl._isl.dim_type.in_, tuple_in)

        return zero_part
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
