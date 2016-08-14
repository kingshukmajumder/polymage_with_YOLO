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
# storage_mapping.py : Mapping from logical functions to physical arrays,
#                      exploration of reuse opportunities.
#

from __future__ import absolute_import, division, print_function

import logging
import targetc as genc
from expression import *
from pipe import *
from liveness import *

# LOG CONFIG #
storage_logger = logging.getLogger("storage_mapping.py")
storage_logger.setLevel(logging.INFO)
LOG = storage_logger.log

class TypeSizeMap(object):
    _type_size_map = { "void":1,
                       "int8":1, "uint8":1,
                       "int16":2, "uint16":2,
                       "int32":4, "uint32":4,
                       "int64":8, "uint64":8,
                       "float":4, "double":8 }

    @classmethod
    def getsize(cls, typ):
        typ_name = typ.c_type_name()
        assert typ_name in cls._type_size_map
        return cls._type_size_map[typ_name]

def get_dim_size(dim_storage, const=None):
    if const == None:
        const = dim_storage.const
    if isinstance(dim_storage.coeff, Fraction):
        numr = dim_storage.coeff.numerator
        denr = dim_storage.coeff.denominator
        param_part = numr * dim_storage.orig_param // denr
    else:
        param_part = dim_storage.coeff * dim_storage.orig_param
    size = param_part + const
    size = simplify_expr(size)

    return size

class Dimension:
    def __init__(self, size_map):
        _param = size_map[0]
        self._orig_param = _param

        if _param == 0:  # constant
            self._param = '0'
        else:  # Parameter
            self._param = _param.name

        self._size_expr = size_map[1]

        coeff_map = get_affine_var_and_param_coeff(self._size_expr)
        self._const = int(get_constant_from_expr(self._size_expr))
        self._coeff = 1
        if not self.is_constant:
            self._coeff = coeff_map[_param]
        else:
            self._coeff = self._const

    @property
    def orig_param(self):
        return self._orig_param
    @property
    def param(self):
        return self._param
    @property
    def size(self):
        return self._size_expr
    @property
    def coeff(self):
        return self._coeff
    @property
    def const(self):
        return self._const
    @property
    def is_constant(self):
        return self._param == '0'

    def __str__(self):
        '''
        const = str(self.const)
        if self.param == '0':
            return '['+const+']'
        coeff = str(self.coeff)
        '''
        dim_str = '['+str(get_dim_size(self))+']'
        return dim_str

class Storage:
    def __init__(self, _typ, _dims, _dim_sizes):
        self._typ = _typ
        self._dims = _dims
        self._dim_sizes = _dim_sizes

        self._id = None

        self._dimension = []
        for dim in range(0, self._dims):
            self._dimension.append(Dimension(self._dim_sizes[dim]))

        self._lookup_key = self.generate_key()
        self._offsets = self.gen_param_offsets()

    @property
    def typ(self):
        return self._typ
    @property
    def dims(self):
        return self._dims
    @property
    def dim_sizes(self):
        return self._dim_sizes
    @property
    def id_(self):
        return self._id
    @property
    def lookup_key(self):
        return self._lookup_key
    @property
    def offsets(self):
        return self._offsets

    def get_dim(self, dim):
        assert dim < self._dims
        return self._dimension[dim]

    def generate_key(self):
        '''
        To create class mapping, we generate keys this way -
        - Field 0 : size, in bytes, of data type of the compute object
        - Field 1 : dimensionality 'dim' of the compute object
        - Following 'dim' fields are tuples of Parameter names with their
          respective coefficents. The fields are sorted using the parameter
          names.
        '''

        key = [TypeSizeMap.getsize(self.typ), self.dims]

        # get (param, coeff) key from each dim
        param_keys = []
        for dim in range(0, self.dims):
            storage_dim = self.get_dim(dim)
            param_keys.append((storage_dim.param, storage_dim.coeff))
        param_keys = sorted(param_keys, key=lambda x:x[0])

        key.extend(param_keys)
        # convert to string because list as a dict key is not allowed
        key = str(key)

        return key

    def gen_param_offsets(self):
        # get (param, const) from each dim
        param_offsets = []
        for dim in range(0, self.dims):
            storage_dim = self.get_dim(dim)
            offset_tuple = (storage_dim.param, storage_dim.const)
            param_offsets.append(offset_tuple)

        return param_offsets

    def compute_total_size(self):
        total_size = 1
        for size in self.dim_sizes:
            total_size *= size

        return total_size

    def generate_id(self):
        self._id = IdGen.get_stg_id()

    def __str__(self):
        typ_str = str(self.typ.c_type_name())
        ndims_str = str(self.dims)
        dims_str = ''
        for i in range(0, self.dims):
            dim = self.get_dim(i)
            dims_str += str(dim)
            if i < self.dims-1:
                dims_str += ' :: '
        stg_str = '{'+typ_str+', '+ndims_str+', '+dims_str+'}'
        return stg_str

def classify_storage(pipeline):
    '''
    Classifies the compute objects into separate groups based on their storage
    sizes.
    '''

    def find_storage_equivalence(comps):
        '''
        Create a mapping to the compute object from it's size properties.
        The classification can be further improved with the knowledge of param
        constraints or estimates, by not differentiating b/w dimensions of
        equal sizes.
        NOTE: This module is unaware of whether the pipeline outputs must be
        excluded from classification with other compute objects.
        '''
        storage_class_map = {}
        for comp in comps:
            storage = comp.orig_storage_class
            key = storage.lookup_key
            if key not in storage_class_map:
                storage_class_map[key] = [comp]
            else:
                storage_class_map[key].append(comp)

        return storage_class_map

    def maximal_storage(comps, storage_class_map):
        '''
        Compute the maximal storage needed at each dimension individually and
        over approximate the total storage to be the product of maximal storage
        of all dimensions. This can further be improved with the knowledge of
        param constraints (or estimates) which suggests an exact (or
        approximate) measure of the size of each dimension.
        '''
        # ***
        log_level = logging.DEBUG
        LOG(log_level, "_______")
        LOG(log_level, "Storage classes:")
        # ***
        new_storage_class_map = {}
        for key in storage_class_map:
            class_comps = storage_class_map[key]  # a list

            # pick a dummy comp to get the total number of dimensions and the
            # original parameter associated with each dimension
            helper_comp = class_comps[0]
            typ = helper_comp.func.typ
            dims = helper_comp.func.ndims
            helper_storage = helper_comp.orig_storage_class
            offsets = helper_storage.offsets

            # this list holds the maximal offset value for each dimension
            max_offset = [offsets[dim][1] for dim in range(0, dims)]

            for comp in class_comps:
                storage = comp.orig_storage_class
                offsets = storage.offsets
                for dim in range(0, dims):
                    dim_off = offsets[dim][1]  # its a tuple
                    max_offset[dim] = int(max(max_offset[dim], dim_off))

            # collect the dim storage info and update with the new maximal
            # offset
            dim_sizes = []
            for dim in range(0, dims):
                dim_storage = helper_storage.get_dim(dim)
                new_size = get_dim_size(dim_storage, max_offset[dim])
                dim_sizes.append((dim_storage.orig_param, new_size))

            # final maximal storage for this class
            max_storage = Storage(typ, dims, dim_sizes)
            max_storage.generate_id()

            # all comps of this class now have identical storage
            new_storage_class_map[max_storage] = []
            for comp in class_comps:
                comp.set_storage_class(max_storage)
                new_storage_class_map[max_storage].append(comp)

            # ***
            log_level = logging.DEBUG
            LOG(log_level, key)
            LOG(log_level, "\t%-*s" % \
                (15, [comp.func.name for comp in class_comps]))
            LOG(log_level, "\t%-*s" % (15, str(max_storage)))
            # ***

        # clear the temporary mappings
        storage_class_map.clear()

        return new_storage_class_map

    def naive_classification(comps):
        '''
        For each comp, use it's original storage class to set it's storage
        class.
        '''
        storage_class_map = {}
        for comp in comps:
            storage_class = comp.orig_storage_class
            storage_class.generate_id()
            storage_class_map[comp] = storage_class
            comp.set_storage_class(storage_class)
        return storage_class_map

    def set_input_objects_storage(pipeline):
        '''
        Collect compute objects of functions of type input, and return a naive
        classification map for them.
        '''
        inp_comps = [pipeline.func_map[inp] for inp in pipeline.inputs]
        storage_class_map = \
            naive_classification(inp_comps)
        return storage_class_map

    def classify_storage_for_comps(comps, opt=False):
        '''
        If storage optimization is enabled, classify storage based on certain
        equivalence criteria.
        '''
        if opt:
            # find equivalence in size between storage objects and create
            # classes of storage objects
            storage_class_map = find_storage_equivalence(comps)

            # compute the maximal offsets in each dimension of the compute
            # objects, and compute the total_size of the storage for each
            # storage class
            storage_class_map = maximal_storage(comps, storage_class_map)
        else:
            storage_class_map = naive_classification(comps)

        return storage_class_map

    # ''' main '''
    opt = 'optimize_storage' in pipeline.options
    storage_class_map = {}

    # storage classification for pipeline inputs
    storage_class_map['inputs'] = set_input_objects_storage(pipeline)

    # storage classification for group compute objects
    for group in pipeline.groups:
        g_comps = [comp for comp in group.comps if not comp.is_liveout]
        storage_class_map[group] = classify_storage_for_comps(g_comps, opt)

    # storage classification for outputs
    out_comps = [pipeline.func_map[func] for func in pipeline.outputs]
    storage_class_map['liveouts'] = classify_storage_for_comps(out_comps,
                                    opt=False)

    # storage classification for other liveouts
    live_comps = list(set(pipeline.liveouts).difference(set(out_comps)))
    liveout_stg_class_map = classify_storage_for_comps(live_comps,
                            opt)
    storage_class_map['liveouts'].update(liveout_stg_class_map)

    return storage_class_map


def log_schedule(comps, schedule):
    log_level = logging.DEBUG-2
    LOG(log_level, "\n=======")
    LOG(log_level, "Schedules:")
    for comp in comps:
        LOG(log_level, "\t%-*s" % (15, comp.func.name) + \
            ": "+str(schedule[comp]))
    return

def log_storage_mapping(comps, storage_map):
    log_level = logging.DEBUG-1
    LOG(log_level, "")
    LOG(log_level, "Storage mapping:")
    for comp in comps:
        LOG(log_level, "\t%-*s" % (15, comp.func.name) + \
            ": "+str(storage_map[comp]))
    return

def remap_storage_for_comps(comps, storage_class_map, schedule,
                            liveness_map, storage_map, opt=False):
    '''
    If storage optimization is enabled, enable reuse by setting array numbers
    for comps which can use the same array for computation.
    '''
    array_count = 0

    if not opt:
        for comp in comps:
            if comp.is_tstencil_type:
                array_count += 2
                storage_map[comp] = (array_count-1, array_count)
            else:
                array_count += 1
                storage_map[comp] = array_count
        return

    # sort comps according to their schedule
    sorted_comps = get_sorted_objs(schedule)

    # initialize a pool of arrays for each storage class
    stg_classes = list(set([comp.storage_class for comp in sorted_comps]))
    array_pool = {}
    for stg_class in stg_classes:
        array_pool[stg_class] = []

    for comp in sorted_comps:
        stg_class = comp.storage_class

        # number of arrays required to realize the compute object
        num_reqd = 2 if comp.is_tstencil_type else 1
        # number of arrays avaiable in the pool
        num_available = len(array_pool[stg_class])

        # number of arrays that can be allocated from the pool
        num_allocated = min(num_available, num_reqd)
        allocated_arrays = [array_pool[stg_class].pop() \
            for _ in range(num_allocated)]

        # number of arrays yet to be allocated
        deficit = num_reqd - num_allocated
        if deficit > 0:
            allocated_arrays += [array_count + 1 + i for i in range(deficit)]
            array_count += deficit

        # Values of the storage_map dictionary are used as keys somewhere else
        # (in array_writers dictionary). This forces us to have tuples that
        # are of hashable type, and not lists.
        storage_map[comp] = tuple(allocated_arrays) if comp.is_tstencil_type \
            else allocated_arrays[0]

        # Return the temporary buffer required by current comp - if tstencil.
        # The result array of the comp will be returned to the pool once it is
        # no more live.
        if comp.is_tstencil_type:
            array_pool[stg_class].append(allocated_arrays[0])

        # return other free arrays to pool
        time = schedule[comp]
        # if any comp is not live after this point
        if time in liveness_map:
            free_comps = liveness_map[time]
            for free_comp in free_comps:
                comp_stg_class = free_comp.storage_class
                storage_index = storage_map[free_comp][1] \
                    if free_comp.is_tstencil_type \
                    else storage_map[free_comp]
                array_pool[comp_stg_class].append(storage_index)

    # ***
    log_schedule(sorted_comps, schedule)
    log_storage_mapping(sorted_comps, storage_map)
    # ***

    return

def remap_storage(pipeline):
    '''
    Map logical storage objects to representative physical arrays
    The mapping can be switched between naive and optimized (with reuse)
    versions, given a schedule for the comps within its group.
    '''
    opt = 'optimize_storage' in pipeline.options

    # a mapping from comp -> index of array of comp's storage class:
    storage_map = {}

    storage_class_map = pipeline.storage_class_map
    # 1. remap for group
    for group in pipeline.groups:
        remap_storage_for_comps(group.comps, storage_class_map[group],
                                group.comps_schedule, group.liveness_map,
                                storage_map, opt)
    # 2. remap for liveouts
    remap_storage_for_comps(pipeline.liveouts, storage_class_map['liveouts'],
                            pipeline.liveouts_schedule, pipeline.liveness_map,
                            storage_map, opt)

    return storage_map

def create_physical_arrays(pipeline):
    '''
    Create cgen CArrays for compute objects using the storage mapping from
    logical storage object of the comp (assumed to be available at this point).
    '''

    opt = 'optimize_storage' in pipeline.options

    def create_new_array(comp, flat_scratch=False, identifier=""):
        '''
        Creates CArray for a given comp
        '''
        stg_class = comp.storage_class
        # array attributes
        array_layout = 'contiguous'
        if comp.is_output or comp.is_image_typ:  # inputs and outputs
            array_name = comp.func.name
        else:
            tag = str(stg_class.id_)
            # array naming
            if opt:
                array_name = genc.CNameGen.get_array_name(comp.is_liveout, tag)
            else:
                array_name = comp.func.name

            if not comp.is_liveout:  # live out
                if flat_scratch:  # linearized array
                    array_layout = 'contiguous_static'
                else:
                    array_layout = 'multidim'
        array_type = genc.TypeMap.convert(comp.func.typ)
        array_sizes = []
        for dim in range(0, stg_class.dims):
            dim_storage = stg_class.get_dim(dim)
            array_sizes.append(get_dim_size(dim_storage))

        # create CArray object
        array = genc.CArray(array_type, array_name+identifier, array_sizes)
        array.layout = array_layout

        return array

    def set_array_for_comp(comp, array_id, created, flat_scratch=False):
        '''
        Set CArray for comp by newly creating it or finding the already created
        corresponding object.
        '''
        def set_array(comp, array_id, created, flat_scratch, identifier=""):
            if array_id in created:
                array = created[array_id]
            else:
                array = create_new_array(comp, flat_scratch, identifier)
                # record the array creation
                created[array_id] = array

            return array

        if comp.is_tstencil_type:
            array1 = set_array(comp, array_id[0], created, flat_scratch, "_T0")
            array2 = set_array(comp, array_id[1], created, flat_scratch, "_T1")
            array = (array1, array2)
        else:
            array = set_array(comp, array_id, created, flat_scratch)

        return array

    def set_arrays_for_inputs(pipeline):
        '''
        Representative CArray objects for inputs. Should not allocate.
        '''
        func_map = pipeline.func_map
        inputs = pipeline.inputs
        for inp in inputs:
            inp_comp = func_map[inp]
            array = create_new_array(inp_comp)
            inp_comp.set_storage_object(array)
        return

    def set_arrays_for_outputs(pipeline, created):
        '''
        Representative CArray objects for outputs. Should not allocate.
        '''
        func_map = pipeline.func_map
        outputs = pipeline.outputs
        for out in outputs:
            out_comp = func_map[out]
            array_id = pipeline.storage_map[out_comp]

            if out_comp.is_tstencil_type:
                # assuming that the temporary buffer required for tstencils
                # will be allocated in the 0'th element of the array list
                array1 = create_new_array(out_comp, flat_scratch, "_T0")
                array2 = create_new_array(out_comp)
                array = (array1, array2)
                # record array creation. Outputs may collide with non-output
                # liveouts for reuse.
                created[array_id[0]] = array[0]
                created[array_id[1]] = array[1]
            else:
                array = create_new_array(out_comp)
                # record array creation. Outputs may collide with non-output
                # liveouts for reuse.
                created[array_id] = array

            out_comp.set_storage_object(array)

        return

    def set_arrays_for_comps(pipeline, created_arrays, flat_scratch):
        '''
        CArray objects for intermediate and non-output liveout compute objects.
        '''
        for group in pipeline.groups:
            # place where created scratchpads are recorded
            created_scratch = {}

            # create / map CArray objects to comps
            for comp in group.comps:
                if comp.is_output:
                    continue
                array_id = pipeline.storage_map[comp]
                if comp.is_liveout:
                    array = set_array_for_comp(comp, array_id, created_arrays)
                else:
                    array = set_array_for_comp(comp, array_id, created_scratch,
                                               flat_scratch)
                comp.set_storage_object(array)
        return

    flat_scratch = 'flatten_scratchpad' in pipeline.options

    # place where created arrays are recorded
    created_arrays = {}

    # first create arrays for pipeline inputs
    set_arrays_for_inputs(pipeline)

    # create arrays for pipeline outputs.
    # doing this first will open doors for using output arrays, that will be
    # allocated outside the pipeline function, for other liveouts.
    set_arrays_for_outputs(pipeline, created_arrays)

    # create arrays for the rest of the comps
    set_arrays_for_comps(pipeline, created_arrays, flat_scratch)

    # collect users for each array created
    array_writers = {}
    for comp in pipeline.comps:
        if comp.array not in array_writers:
            array_writers[comp.array] = []
        array_writers[comp.array].append(comp)

    return array_writers

def map_reverse(map_):
    '''
    Assumes map_[key] = val, where val is a list
    '''
    rmap = {}
    for key in map_:
        for map_val in map_[key]:
            rmap[map_val] = key

    return rmap

def create_array_freelist(pipeline):
    '''
    Create a list of arrays for each time in the group schedule, at which
    these arrays have their last use.
    '''
    def logs(liveness_map2, array_writers, last_use, free_arrays):
        # ***
        log_level = logging.DEBUG-2
        LOG(log_level, "\n_______")
        LOG(log_level, "Reverse liveness map for Liveouts:")
        for comp in liveness_map2:
            LOG(log_level, "\t%-*s" % (15, comp.func.name) + \
                ": " + str(liveness_map2[comp]))
        # ***
        log_level = logging.DEBUG-2
        LOG(log_level, "\n_______")
        LOG(log_level, "Array Users:")
        for array in array_writers:
            if True in [comp.is_liveout for comp in array_writers[array]]:
                LOG(log_level, "\t%-*s" % (15, array.name) + ": " + \
                    str([comp.func.name for comp in array_writers[array]]))
        # ***
        log_level = logging.DEBUG-1
        LOG(log_level, "\n_______")
        LOG(log_level, "Last use map for arrays:")
        for array in last_use:
            LOG(log_level, "\t%-*s" % (15, array.name) + \
                ": " + str(last_use[array]))
        # ***
        log_level = logging.DEBUG-1
        LOG(log_level, "\n_______")
        LOG(log_level, "Free arrays :")
        for g in free_arrays:
            LOG(log_level,
                "\t%-*s" % (15, g.name+" ("+str(g_schedule[g])+")") + \
                ": " + str([arr.name for arr in free_arrays[g]]))
        return

    array_writers = pipeline.array_writers
    g_schedule = pipeline.group_schedule
    liveness_map = pipeline.liveness_map
    # get a map-reverse
    liveness_map2 = map_reverse(liveness_map)

    # ignore all arrays used by pipeline outputs
    out_comps = [pipeline.func_map[func] for func in pipeline.outputs]
    output_arrays = [comp.array for comp in out_comps]
    for array in output_arrays:
        array_writers.pop(array)

    # find the scheduled time (of group) at which arrays have thier last use
    last_use = {}
    for array in array_writers:
        # are we dealing with full arrays? -
        if True in [comp.is_liveout for comp in array_writers[array]]:
            writer_sched = {}
            for writer in array_writers[array]:
                writer_sched[writer] = g_schedule[writer.group]
            last_writer = max(array_writers[array],
                              key=lambda x:writer_sched[x])
            if last_writer in liveness_map2:  # not pipeline outputs
                last_use[array] = liveness_map2[last_writer]

    # reverse-map from group_schedule -> group
    schedule_g = dict((v, k) for k, v in g_schedule.items())

    # create a direct mapping from groups to arrays that are not live after
    # the group's execution is complete
    free_arrays = {}
    for group in g_schedule:
        free_arrays[group] = []
    for array in last_use:
        user_sched = last_use[array]
        # find the group with schedule time = user_sched
        group = schedule_g[user_sched]
        free_arrays[group].append(array)

    # ***
    logs(liveness_map2, array_writers, last_use, free_arrays)

    return free_arrays
