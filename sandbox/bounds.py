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
# bounds.py : Interval analysis and function bounds check pass
#

from __future__ import absolute_import, division, print_function

from expression import isAffine
from poly import extract_value_dependence
import logging
import pipe

# LOG CONFIG #
bounds_logger = logging.getLogger("bounds.py")
bounds_logger.setLevel(logging.ERROR)

LOG = bounds_logger.log

def bounds_check_pass(pipeline):
    """
    Bounds check pass analyzes if function values used in the compute
    objects are within the domain of the functions. Static analysis is
    only possible when the references to function values are regular
    i.e. they are not data dependent. We restrict ourselves to affine
    references.
    """
    for group in pipeline.groups:
        for child in group.children:
            check_refs(child, group)
        for inp in group.image_refs:
            check_refs(group, pipeline.input_groups[inp])
    return

def check_refs(child_group, parent_group):
    # Check refs works only on non-fused groups. It can be made to
    # work with fused groups as well. However, it might serve very
    # little use.
    # assert (not child_group.isFused() and not parent_group.isFused())

    # get the only comp_obj in child and parent groups
    parent_comp = parent_group.comps[0]
    parent_func = parent_comp.func
    child_comp = child_group.comps[0]
    child_func = child_comp.func

    # Only verifying if both child and  parent group have a polyhedral
    # representation
    if child_group.polyRep.poly_parts and parent_group.polyRep.poly_doms:
        for child_part in child_group.polyRep.poly_parts[child_comp]:
            # Compute dependence relations between child and parent
            child_refs = child_part.refs
            if child_part.pred:
                child_refs += child_part.pred.collect(Reference)

            # It is not generally feasible to check the validity of
            # and access when the reference is not affine. 
            # Approximations can be done but for now skipping them.
            def affine_ref(ref):
                affine = True
                for arg in ref.arguments:
                    affine = affine and isAffine(arg)
                return affine

            # filter out only the affine refs to parent_func
            child_refs = [ ref for ref in child_refs \
                                 if ref.objectRef == parent_func and
                                    affine_ref(ref) ]

            log_level = logging.DEBUG
            deps = []

            
            parent_dom = parent_group.polyRep.poly_doms[parent_comp]
            # the domain set of the parent
            parent_dom_set = None
            # assuming it is Tstencil, we need to project out the time 
            # dimension
            import islpy as isl; # TERRIBLE: FIXME HACK TODO
            if parent_comp.is_tstencil_type:
                full_space = parent_dom.dom_set.get_space()
                # drop the leading time dimension so it doesn't mess with
                # the constraint assignment we do
                # All the constraint stuff doesn't know about the fake
                # time dimension
                removed_time_space = full_space.copy().drop_dims(isl.dim_type.out, 0, 1)
                parent_dom_set = isl.BasicSet.universe(removed_time_space)

            else:
                # otherwise, just return the full set
                parent_dom_set = isl.BasicSet.universe(parent_dom.dom_set.get_space())


            assert parent_dom_set is not None

            for ref in child_refs:
                deps += extract_value_dependence(child_part, ref, parent_dom_set)
                LOG(log_level, "ref : "+str(ref))
            for dep in deps:
                # import pudb; pudb.set_trace()
                diff = dep.rel.range().subtract(parent_dom_set)
                # ***
                ref_str = "referenced    = "+str(dep.rel.range())
                dom_str = "parent domain = "+str(parent_dom_set)
                log_level = logging.DEBUG
                LOG(log_level, ref_str)
                LOG(log_level, dom_str)
                # ***
                if(not diff.is_empty()):
                    # ***
                    log_level = logging.ERROR
                    LOG(log_level, "_______________________")
                    LOG(log_level, "Reference out of domain")
                    LOG(log_level, ref_str)
                    LOG(log_level, dom_str)
                    LOG(log_level, "Child Dom:\n%s" % dep)
                    LOG(log_level, "Parent Dom:\n%s" % parent_dom)
                    LOG(log_level, "Child group:\n%s\n%s" % (child_group, child_comp))
                    LOG(log_level, "Parent group:\n%s\n%s" % (parent_group, parent_comp))
                    LOG(log_level, "diff:\n%s" % diff)
                    LOG(log_level, "_______________________")
                    # ***
                    raise TypeError("Reference out of domain", child_group,
                                     parent_group, diff)

    return
