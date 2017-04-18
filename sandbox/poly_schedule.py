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
# poly_schedule.py : Polyhedral transformations, fusion, overlapped tiling.
#

from __future__ import absolute_import, division, print_function

import logging
from grouping import get_group_dep_vecs
from utils import *
from poly import *

# LOG CONFIG #
poly_sched_logger = logging.getLogger("poly_schedule.py")
poly_sched_logger.setLevel(logging.INFO)
LOG = poly_sched_logger.log

def format_schedule_constraints(dim_in, dim_out, align, scale, level_no):
    ineq_coeff = []
    eq_coeff   = []
    dim_set = [ False for i in range(0, dim_out) ]
    # Adding identity constraint for each dimension
    for i in range(0, dim_in):
        coeff = {}
        coeff[('out', align[i])] = 1
        if scale[i] != NULL:
            assert scale[i] >= 1
        coeff[('in', i)] = -1 * scale[i]
        eq_coeff.append(coeff)
        dim_set[align[i]] = True

    # Setting the leading schedule dimension to level
    level_coeff = {}
    level_coeff[('out', 0)] = -1
    level_coeff[('constant', 0)] = level_no-1
    eq_coeff.append(level_coeff)

    # Setting the remaining dimensions to zero
    for i in range(1, dim_out):
        if not dim_set[i]:
            coeff = {}
            coeff[('out', i)] = 1
            coeff[('constant', 0)] = 0
            eq_coeff.append(coeff)
    return [ineq_coeff, eq_coeff]

def format_schedule_constraints_without_align_scale(dim_in, dim_out,level_no):
    ineq_coeff = []
    eq_coeff = []
    dim_set = [False for i in range(0, dim_out)]
    # Setting the leading schedule dimension to level
    level_coeff = {}
    level_coeff[('out', 0)] = -1
    level_coeff[('constant', 0)] = level_no - 1
    eq_coeff.append(level_coeff)

    # Setting the remaining dimensions to zero
    for i in range(1, dim_out):
        if not dim_set[i]:
            coeff = {}
            coeff[('out', i)] = -1
            coeff[(('in', i - 1))] = 1
            eq_coeff.append(coeff)
    return [ineq_coeff, eq_coeff]

def base_schedule(group):
    """
    Construct the base schedule for a group with a polyhedral representation.
    """

    assert(group.isPolyhedral)

    parts = []
    for sublist in group.polyRep.poly_parts.values():
        parts.extend(sublist)

    for part in parts:
        dim_in = part.sched.dim(isl._isl.dim_type.in_)
        dim_out = part.sched.dim(isl._isl.dim_type.out)
        [ineqs, eqs] = format_schedule_constraints(dim_in, dim_out,
                                                   part.align,
                                                   part.scale,
                                                   part.level)
        part.sched = add_constraints(part.sched, ineqs, eqs)

    return parts

def base_schedule_for_matrix_ops(group):
    """
        Construct the base schedule for a group with a polyhedral representation.
        """

    assert (group.isPolyhedral)

    parts = []
    for sublist in group.polyRep.poly_parts.values():
        parts.extend(sublist)

    for part in parts:
        dim_in = part.sched.dim(isl._isl.dim_type.in_)
        dim_out = part.sched.dim(isl._isl.dim_type.out)
        [ineqs, eqs] = format_schedule_constraints_without_align_scale(dim_in, dim_out,
                                                   part.level)
        part.sched = add_constraints(part.sched, ineqs, eqs)

    return parts

def stripMineSchedule(sched, dim, size):
    sched = sched.insert_dims(isl._isl.dim_type.out, dim, 1)
    name = sched.get_dim_name(isl._isl.dim_type.out, 1 + dim) 
    sched = sched.set_dim_name(isl._isl.dim_type.out, dim, 'S_' + name)
    ineqs = []
    #  size*(Ti) <= i <= size*(Ti) + size - 1
    coeff = {}
    coeff[('out', dim)] = sizes[dim - startDim] 
    coeff[('constant', 0)] = sizes[dim - startDim] - 1
    coeff[('out', numDims + dim)] = -1
    ineqs.append(coeff)

    coeff = {}
    coeff[('out', dim)] = -sizes[dim - startDim] 
    coeff['out', numDims + dim] = 1
    ineqs.append(coeff) 
    sched = addConstriants(sched, ineqs, [])

    return sched

def tileSchedule(sched, dim, size, overlapOffset = 0):
    # Extend space to accomodate the tiling dimensions
    sched = sched.insert_dims(isl._isl.dim_type.out, dim, 1)
    # Create the tile dimensions and their constraints
    name = sched.get_dim_name(isl._isl.dim_type.out, 1 + dim) 
    sched = sched.set_dim_name(isl._isl.dim_type.out, dim, '_T' + name)

    ineqs = []
    #  size*(Ti) <= i <= size*(Ti) + size - 1
    coeff = {}
    coeff[('out', dim)] = size 
    coeff[('constant', 0)] = size - 1 + overlapOffset
    coeff[('out', 1 + dim)] = -1
    ineqs.append(coeff)

    coeff = {}
    coeff[('out', dim)] = -size 
    coeff['out', 1 + dim] = 1
    ineqs.append(coeff) 
    sched = addConstriants(sched, ineqs, [])
    return (sched, ('rect', name, '_T' + name, size))

def compute_tile_slope(dep_vecs, hmax):
    # Compute slopes
    # -- The first dimension in the domain gives the comp obj order. The slope
    #    of the tile in each dimension is computed w.r.t the comp obj order.
    #    The min extent and max extent in each dimension are computed. The
    #    hyperplanes representing the min and max extent give the shape of the
    #    tile in that dimension.
    #
    # =================================================================
    # '*' = live-out / live-in
    # '+' = intermediate
    # '-' = spurious compute due to over-approximation
    # (edges bw '*' and '+' are the actual dependences)
    #
    #  ^  * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
    #  |               /|\               X                |\
    #  |              + + + + + + + + + + + + + + + + + + + +
    #  |             /| |              /   \              |  \
    #  |            - + + + + + + + + + + + + + + + + + + + + -
    #  |           / /|\|            /       \            |    \
    #  h          - + + + + + + + + + + + + + + + + + + + + + + -
    #  |         / /|\  |          /           \          |      \
    #  |        - + + + + + + + + + + + + + + + + + + + + + + + + -
    #  |       / /|\    |        /               \        |        \
    #  v  * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * *
    #         <--- a --->       <------- o ------->       <--- b --->
    #
    # a = max_width
    # b = min_width
    # o = overlap
    # =================================================================

    if len(dep_vecs) < 1 :
        return ([], [])

    vec_len = len(dep_vecs[0][0])
    slope_min = [ (0, 1) for i in range(0, vec_len - 1) ]
    slope_max = [ (0, 1) for i in range(0, vec_len - 1) ]
    # Find max and min widths of dependencies at the base
    widths = []
    hmin = min([ dep[1] for dep in dep_vecs ])
    # extent cumulated at each level
    min_width = [ 0 for i in range(0, vec_len - 1) ]
    max_width = [ 0 for i in range(0, vec_len - 1) ]
    dep_unknown = [ False for i in range(0, vec_len - 1) ]
    # for each level
    for currh in range(hmax - 1, hmin - 1, -1):
        local_max_w = [ 0 for i in range(0, vec_len - 1) ]
        local_min_w = [ 0 for i in range(0, vec_len - 1) ]
        # dep vecs for this level
        h_dep_vecs = [ dep_vec for dep_vec in dep_vecs
                                 if dep_vec[1] == currh ]
        # h corresponds to topo-order height in the pipeline
        for dep_vec, h in h_dep_vecs:
            for i in range(0, len(dep_vec)-1):
                if dep_vec[i+1] == '*':
                    dep_unknown[i] = True
                    continue
                if dep_vec[i+1] > 0:
                    local_max_w[i] = max(local_max_w[i], dep_vec[i+1])
                if dep_vec[i+1] < 0:
                    local_min_w[i] = min(local_min_w[i], dep_vec[i+1])
        for i in range(0, len(dep_vec)-1):
            max_width[i] = max_width[i] + local_max_w[i]
            min_width[i] = min_width[i] + local_min_w[i]
        # remember the cumukated extent at each level
        widths.append((list(min_width), currh))
        widths.append((list(max_width), currh))

    # use the level-specific extents to determine the slope
    # (h will be descending, as 'widths' list was populated in that order)
    for width, h in widths:
        scale = hmax - h
        for i in range(0, vec_len-1):
            # be careful while constructing Fraction object
            # min slope
            if ((Fraction(width[i], scale) < Fraction(slope_min[i][0],
                                                      slope_min[i][1])) and \
                width[i] < 0):
                slope_min[i] = (width[i], scale)
            # max slope
            if ((Fraction(width[i], scale) > Fraction(slope_max[i][0],
                                                      slope_max[i][1])) and \
                width[i] > 0):
                slope_max[i] = (width[i], scale)

    for i in range(0, vec_len-1):
        if dep_unknown[i]:
            slope_min[i] = '*'
            slope_max[i] = '*'

    return (slope_min, slope_max)

def mark_par_and_vec_for_tile(poly_part):
    p = poly_part
    # -- Mark parallel dimensions and vector dimensions for tiles
    #    -- Find the outer most parallel dimension which can generate "enough"
    #       tasks for the given number of threads.
    #    -- Partial and full tile separation to enable better vectorization.
    outer_parallel_dim = None
    inner_vec_dim = None
    for dim in p.dim_tile_info:
        if p.dim_tile_info[dim][0] == 'none':
            # Either the dimension is too small to be parallelized or
            # is skewed. In both cases the dimension cannot be parallel.
            # This can change when we choose to not tile a dimension.
            continue
        elif p.dim_tile_info[dim][0] == 'overlap':
            dim_name = p.dim_tile_info[dim][1]
            tile_dim_name = p.dim_tile_info[dim][2]
            sched_dim = p.sched.find_dim_by_name(isl._isl.dim_type.out,
                                                 dim_name)
            tile_dim = p.sched.find_dim_by_name(isl._isl.dim_type.out,
                                                tile_dim_name)
            # update outermost parallel dim
            if outer_parallel_dim is not None:
                outer_parallel_dim = min(tile_dim, outer_parallel_dim)
            else:
                outer_parallel_dim = tile_dim
            # update outermost vector dim
            if inner_vec_dim is not None:
                inner_vec_dim = max(sched_dim, inner_vec_dim)
            else:
                inner_vec_dim = sched_dim

    # mark parallel
    if outer_parallel_dim is not None:
        p_dim_name = p.sched.get_dim_name(isl._isl.dim_type.out,
                                          outer_parallel_dim)
        p.parallel_sched_dims.append(p_dim_name)
    # mark vector
    if inner_vec_dim is not None:
        v_dim_name = p.sched.get_dim_name(isl._isl.dim_type.out,
                                        inner_vec_dim)
        p.vector_sched_dim.append(v_dim_name)

    return

def mark_par_and_vec(poly_part, param_estimates):
    p = poly_part
    # Determine the outer most dim and mark it parallel,
    # the inner most dim and mark it as vector
    parallel_dim = None
    vec_dim = None
    dim_in = p.sched.dim(isl._isl.dim_type.in_)
    domain = []
    for dim in range(0, dim_in):
        interval = p.comp.func.domain[dim]
        # Since size could be estimated so can interval size be
        intr_size = get_dim_size(interval, param_estimates)

        # outer parallel dim
        if(get_constant_from_expr(intr_size) >= 16):
            if parallel_dim is not None:
                parallel_dim = min(p.align[dim], parallel_dim)
            else:
                parallel_dim = p.align[dim]

        # inner vector dim
        if(get_constant_from_expr(intr_size) >= 4):
            if vec_dim is not None:
                vec_dim = max(p.align[dim], vec_dim)
            else:
                vec_dim = p.align[dim]

    # mark parallel
    if parallel_dim is not None:
        p_dim_name = p.sched.get_dim_name(isl._isl.dim_type.out,
                                          parallel_dim)
        p.parallel_sched_dims.append(p_dim_name)
    # mark vector
    if vec_dim is not None:
        v_dim_name = p.sched.get_dim_name(isl._isl.dim_type.out,
                                          vec_dim)
        p.vector_sched_dim.append(v_dim_name)

    return

def mark_par_and_vec_for_pluto_sched(poly_part, parallel_loops):
    # TODO: assuming that the name of the out-dims of the part are prefixed with
    # 'o'
    prefix = 'o'

    # init par and vec sched dims
    poly_part.parallel_sched_dims = []
    poly_part.vector_sched_dim = []

    nploops = len(parallel_loops)
    if nploops == 1:
        # the only parallel dim will be outer parallel
        par_dim = parallel_loops[0]
        poly_part.parallel_sched_dims.append(prefix + str(par_dim))
    elif nploops > 1:
        # outermost dim
        par_dim = min(parallel_loops)
        poly_part.parallel_sched_dims.append(prefix + str(par_dim))
        # innermost dim
        vec_dim = max(parallel_loops)
        poly_part.vector_sched_dim.append(prefix + str(vec_dim))

    return

def enable_tile_scratchpad(group_parts):
    # Determine the buffer sizes for stages in each dimension
    for p in group_parts:
        for dim in p.dim_tile_info:
            if p.dim_tile_info[dim][0] == 'none':
                continue
            dim_name = p.dim_tile_info[dim][1]
            tile_dim_name = p.dim_tile_info[dim][2]
            extent = p.dim_tile_info[dim][3]
            if p.dim_tile_info[dim][0] == 'overlap':
                # Accounting for the overlap region
                left = p.dim_tile_info[dim][4]
                right = p.dim_tile_info[dim][5]
                h = p.dim_tile_info[dim][6]
                extent += abs(left * h) + abs(right * h)
            p.dim_scratch_size[dim] = \
                int(math.ceil(Fraction(extent, p.scale[dim])))
            mul_name = \
              '_Mul_'+p.sched.get_dim_name(isl._isl.dim_type.in_, dim)
            dim_in = p.sched.dim(isl._isl.dim_type.in_)
            dim_id =  p.sched.get_tuple_id(isl._isl.dim_type.in_)
            p.sched = p.sched.insert_dims(isl._isl.dim_type.in_, dim_in, 1)
            p.sched = p.sched.set_tuple_id(isl._isl.dim_type.in_, dim_id)
            p.sched = \
              p.sched.set_dim_name(isl._isl.dim_type.in_, dim_in, mul_name)
            sched_dim = \
              p.sched.find_dim_by_name(isl._isl.dim_type.out, dim_name)
            tile_dim = \
              p.sched.find_dim_by_name(isl._isl.dim_type.out, tile_dim_name)

            eqs = []
            coeff = {}
            coeff[('in', dim_in)] = p.scale[dim]
            coeff[('out', sched_dim)] = -1
            coeff[('out', tile_dim)] = p.dim_tile_info[dim][3]
            eqs.append(coeff)

            ineqs = []

            p.sched = add_constraints(p.sched, ineqs, eqs)

    return

def fused_schedule(pipeline, group, param_estimates):
    """Generate an optimized schedule for the stage."""
    g_poly_parts = group.polyRep.poly_parts
    g_all_parts = []
    for comp in g_poly_parts:
        g_all_parts.extend(g_poly_parts[comp])

    # get dependence vectors between each part of the group and each of its
    # parents' part
    comp_deps = get_group_dep_vecs(pipeline, group, g_all_parts)

    # No point in tiling a group that has no dependencies
    is_stencil = len(comp_deps) > 0 and len(g_all_parts) > 1
    for dep, h in comp_deps:
        # Skips groups which have self deps
        if dep[0] == 0:
            is_stencil = False

    # threshold for parallelism
    if not is_stencil:
        for p in g_all_parts:
            part_size = p.get_size(param_estimates)
            big_part = (part_size != '*' and \
                        part_size > pipeline._size_threshold)
            if not p.is_self_dependent and big_part:
                mark_par_and_vec(p, pipeline._param_estimates)

    # Find the parts which are not liveout
    for p in g_all_parts:
        is_liveout = not is_stencil
        #is_liveout = True
        p.set_liveness(p.is_liveout or is_liveout)

    if is_stencil:
        assert(len(g_all_parts) > 1)
        hmax = max( [ p.level for p in g_all_parts ] )
        hmin = min( [ p.level for p in g_all_parts ] )
        slope_min, slope_max = compute_tile_slope(comp_deps, hmax)

        #splitTile(stageGroups[gi], slopeMin, slopeMax)
        overlap_tile(pipeline, g_all_parts, slope_min, slope_max)

        enable_tile_scratchpad(g_all_parts)

        for p in g_all_parts:
            mark_par_and_vec_for_tile(p)

        '''
        for p in g_all_parts:
            skewed_schedule(p)
        '''

    return

def move_independent_dim(dim, group_parts, stageDim):
    # Move the independent dimensions outward of the stage dimension.
    for part in group_parts:
        part.sched = part.sched.insert_dims(isl._isl.dim_type.out, 
                                            stageDim, 1)
        noDepId = part.sched.get_dim_id(
                        isl._isl.dim_type.out, dim + 1)
        noDepName = part.sched.get_dim_name(
                        isl._isl.dim_type.out, dim + 1)
        eqs = []
        coeff = {}
        coeff[('out', dim+1)] = -1
        coeff[('out', stageDim)] = 1
        eqs.append(coeff)
        part.sched = addConstriants(part.sched, [], eqs)
        part.sched = part.sched.remove_dims(
                            isl._isl.dim_type.out, dim+1, 1)
        part.sched = part.sched.set_dim_name(
                                isl._isl.dim_type.out, 
                                stageDim, noDepName)

def get_group_height(group_parts):
    min_height = min( [ part.level for part in group_parts ] )
    max_height = max( [ part.level for part in group_parts ] )
    return max_height - min_height


def match_idiom_matrix_mul(parts):
    zero_found = False
    reduction_found = False
    for part in parts:
        if isinstance(part.func,Reduction):
            if part.expr == 0:
                zero_found = True
            if isinstance(part.expr,Reduce):
                expr = part.expr
                reduce_op = part.expr.op_type
                reduce_expr = expr.expression
                if isinstance(reduce_expr, AbstractBinaryOpNode) and reduce_op == Op.Sum:
                    if isinstance(reduce_expr.left, Reference) \
                            and isinstance(reduce_expr.right, Reference):
                        if is_object_matrix(reduce_expr.left.objectRef) \
                                and is_object_matrix(reduce_expr.right.objectRef):
                            if reduce_expr.op == '*':
                                reduction_found = True
    if reduction_found:
        return True
    return False

def match_idiom_sig_fft(parts):
    fft_found = False
    for part in parts:
        if isinstance(part.func, Wave):
            if isinstance(part.expr, Reference):
                if isinstance(part.expr.objectRef, Wave):
                    lhs = part.func
                    rhs = part.expr.objectRef
                    if (lhs.type == Complex and rhs.type == Double and \
                        lhs.length.__str__() == (rhs.length // 2 + 1).__str__() \
                        and lhs.variables[0] == rhs.variables[0]):
                            fft_found = True
    return fft_found

def is_object_matrix(obj):
    if isinstance(obj, Matrix) or (isinstance(obj, Function) and obj.is_mat_func):
        return True
    return False

def overlap_tile(pipeline, group_parts, slope_min, slope_max):
    comp_dim = 0
    tile_dims = 0
    no_tile_dims = 0
    h = get_group_height(group_parts)
    num_tile_dims = 0
    for i in range(1, len(slope_min) + 1):
        # Check if every part in the group has enough iteration
        # points in the dimension to benefit from tiling.
        tile = False
        for part in group_parts:
            curr_dim = comp_dim + no_tile_dims + 2*tile_dims + 1
            lower_bound = part.sched.range().dim_min(curr_dim)
            upper_bound = part.sched.range().dim_max(curr_dim)
            size = upper_bound.sub(lower_bound)
            if (size.is_cst() and size.n_piece() == 1):
                aff = (size.get_pieces())[0][1]
                val = aff.get_constant_val()
                if val > pipeline._tile_sizes[num_tile_dims]:
                    tile = True
            else:
                tile = True
        if tile and slope_min[i-1] != '*':
            # Altering the schedule by constructing overlapped tiles
            for part in group_parts:
                # Extend space to accomodate the tiling dimensions
                part.sched = part.sched.insert_dims(
                                isl._isl.dim_type.out,
                                comp_dim + tile_dims, 1)
                # get the name of the untiled dim to name its corresponding
                # tiled dimension
                name = part.sched.get_dim_name(
                            isl._isl.dim_type.out,
                            comp_dim + no_tile_dims + 2*tile_dims + 2)
                part.sched = part.sched.set_dim_name(
                                isl._isl.dim_type.out,
                                comp_dim + tile_dims,
                                '_T' + name)
                right = int(math.floor(Fraction(slope_min[i-1][0],
                                                slope_min[i-1][1])))
                left = int(math.ceil(Fraction(slope_max[i-1][0],
                                              slope_max[i-1][1])))
                # L and R are normals to the left and the right
                # bounding hyperplanes of the uniform dependencies

                tile_size = pipeline._tile_sizes[num_tile_dims]
                # Compute the overlap shift
                #print(slope_max, slope_min, h, L, R, i-1)
                overlap_shift = abs(left * (h)) + abs(right * (h))
                for j in range(0, len(part.align)):
                    if i == part.align[j]:
                        assert j not in part.dim_tile_info
                        if tile_size%part.scale[j] != 0:
                            tile_size = int(math.ceil(part.scale[j]))
                        part.dim_tile_info[j] = ('overlap', name, '_T' + name,
                                                 tile_size, left, right, h)
                ineqs = []
                eqs = []
                coeff = {}
                it_dim = comp_dim + no_tile_dims + 2*tile_dims + 2
                tile_dim = comp_dim + tile_dims
                time_dim = comp_dim + tile_dims + 1

                coeff[('out', time_dim)] = -left
                coeff[('out', it_dim)] = 1
                coeff[('out', tile_dim)] = -tile_size
                ineqs.append(coeff)

                coeff = {}
                coeff[('out', time_dim)] = left
                coeff[('out', it_dim)] = -1
                coeff[('out', tile_dim)] = tile_size
                coeff[('constant', 0)] = tile_size - 1 + overlap_shift
                ineqs.append(coeff)
            
                coeff = {}
                coeff[('out', time_dim)] = -right
                coeff[('out', it_dim)] = 1
                coeff[('out', tile_dim)] = -tile_size
                ineqs.append(coeff)

                coeff = {}
                coeff[('out', time_dim)] = right
                coeff[('out', it_dim)] = -1
                coeff[('out', tile_dim)] = tile_size
                coeff[('constant', 0)] = tile_size + overlap_shift - 1
                ineqs.append(coeff)

                prior_dom = part.sched.domain()
                part.sched = add_constraints(part.sched, ineqs, eqs)
                post_dom = part.sched.domain()

                assert(part.sched.is_empty() == False)
                # Tiling should not change the domain that is iterated over
                assert(prior_dom.is_equal(post_dom))
            tile_dims += 1
            num_tile_dims += 1
        else:
            #self.move_independent_dim(i, group_parts, comp_dim)
            name = part.sched.get_dim_name(isl._isl.dim_type.out, comp_dim)
            for part in group_parts:
                for j in range(0, len(part.align)):
                    if i == part.align[j]:
                        assert j not in part.dim_tile_info
                        part.dim_tile_info[j] = ('none', name)
            no_tile_dims += 1

    return

def splitTile(self, group, slopeMin, slopeMax):
    stageDim = 0
    dtileDims = 0
    numTileDims = 0
    for i in range(1, len(slopeMin) + 1):
        if ((slopeMin[i-1][0] != 0 or slopeMax[i-1][0] !=0)):
            # Altering the schedule by constructing split tiles.
            for part in group:
                # Extend space to accomodate the tiling dimensions
                part.sched = part.sched.insert_dims(
                                isl._isl.dim_type.out, 
                                stageDim + 2*dtileDims, 2)
                # Dimension i is for the orientation of the tiles 
                # upward or inverted.
                name = part.sched.get_dim_name(
                            isl._isl.dim_type.out, 
                            stageDim + 3*dtileDims + 3)
                part.sched = part.sched.set_dim_name(
                                isl._isl.dim_type.out, 
                                stageDim + 2*dtileDims + 1, 
                                '_T' + name)
                part.sched = part.sched.set_dim_name(
                                isl._isl.dim_type.out, 
                                stageDim + 2*dtileDims, 
                                '_Dir' + name)
                
                L = (slopeMin[i-1][0], slopeMin[i-1][1])
                R = (slopeMax[i-1][0], slopeMax[i-1][1])
                # L and R are normals to the left and the right 
                # bounding hyperplanes of the uniform dependencies
                
    # Tile size
    #   -- Pick tile sizes such that there are only two sets of tiles 
    #      in the time sense .i.e there should be only one fused stage. 
    #      This has to be revisited when time iterated computations are 
    #      incorporated
                #offset = 3*tileSize/4
                tileSize = self.tileSizes[numTileDims]
                offset = tileSize/2
                ineqs = []
                eqs = []
                coeff = {}
                coeff[('out', stageDim + 2*dtileDims + 2)] = L[0]
                coeff[('out', stageDim + 3*dtileDims + 3)] = L[1]
                coeff[('out', stageDim + 2*dtileDims + 1)] = -tileSize
                ineqs.append(coeff)

                coeff = {}
                coeff[('out', stageDim + 2*dtileDims + 2)] = -L[0]
                coeff[('out', stageDim + 3*dtileDims + 3)] = -L[1]
                coeff[('out', stageDim + 2*dtileDims + 1)] = tileSize
                coeff[('constant', 0)] = tileSize - 1
                ineqs.append(coeff)
                
                coeff = {}
                coeff[('out', stageDim + 2*dtileDims + 2)] = R[0]
                coeff[('out', stageDim + 3*dtileDims + 3)] = R[1]
                coeff[('out', stageDim + 2*dtileDims + 1)] = -tileSize 
                coeff[('out', stageDim + 2*dtileDims)] = -tileSize 
                coeff[('constant', 0)] = -offset
                ineqs.append(coeff)

                coeff = {}
                coeff[('out', stageDim + 2*dtileDims + 2)] = -R[0]
                coeff[('out', stageDim + 3*dtileDims + 3)] = -R[1]
                coeff[('out', stageDim + 2*dtileDims + 1)] = tileSize
                coeff[('out', stageDim + 2*dtileDims)] = tileSize 
                coeff[('constant', 0)] = tileSize + offset - 1
                ineqs.append(coeff)

                coeff = {}
                coeff[('out', stageDim + 2*dtileDims)] = 1
                coeff[('constant', 0)] = 1
                ineqs.append(coeff)

                coeff = {}
                coeff[('out', stageDim + 2*dtileDims)] = -1
                coeff[('constant', 0)] = 0
                ineqs.append(coeff)

                #eqsUpward = eqs[:]
                #eqsDown = eqs[:]
                #coeff = {}
                #coeff[('out', stageDim + 2*dtileDims)] = -1
                #coeff[('constant', 0)] = 0
                #eqsUpward.append(coeff)

                #coeff = {}
                #coeff[('out', stageDim + 2*dtileDims)] = 1
                #coeff[('constant', 0)] = 1
                #eqsDown.append(coeff)

                #schedUp = addConstriants(part.sched, ineqs, eqsUpward)
                #schedDown = addConstriants(part.sched, ineqs, eqsDown)                                
                #part.sched = schedUp.union(schedDown)
                part.sched = addConstriants(part.sched, ineqs, eqs)
                assert(part.sched.is_empty() == False)
            dtileDims += 1
            numTileDims += 1
        else:
            stageDim = self.moveIndependentDim(i, group, stageDim)

def skewed_schedule(poly_part):
    # Second level storage savings can be achieved by utilizing modulo buffers
    # in the non-vector dimension. The fastest varying dimension is considered
    # the vector dimension and by this point should be the inner-most dimension.

    # Disabling this for two reasons
    # 1) The code generator generates awful code. There is no reason to expect
    #    it to generate anything nice.
    # 2) The dimension that has skewing applied to it need not be tiled. This
    #    has to be integrated into scheduling itself.
    p = poly_part
    one_dim = True
    for dim in p.dim_tile_info:
        if p.dim_tile_info[dim][0] == 'overlap' and one_dim:
            one_dim = False
            dim_name = p.dim_tile_info[dim][1]

            # Skewing the dimension
            sched_dim = \
              p.sched.find_dim_by_name(isl._isl.dim_type.out, dim_name)
            p.sched = \
              p.sched.insert_dims(isl._isl.dim_type.out, sched_dim  + 1, 1)
            p.sched = p.sched.set_dim_name(isl._isl.dim_type.out,
                                           sched_dim + 1, '_shift' + dim_name)
            time_dim = p.sched.find_dim_by_name(isl._isl.dim_type.out, '_t')
            right = p.dim_tile_info[dim][5]

            eqs = []
            coeff = {}
            coeff[('out', sched_dim)] = 1
            coeff[('out', time_dim)] = abs(right)
            coeff[('out', sched_dim + 1)] = -1
            eqs.append(coeff)
            p.sched = add_constraints(p.sched, [], eqs)

            p.sched = p.sched.remove_dims(isl._isl.dim_type.out, sched_dim, 1)

            # Moving time inside
            time_dim = p.sched.find_dim_by_name(isl._isl.dim_type.out, '_t')
            p.sched = p.sched.insert_dims(isl._isl.dim_type.out, time_dim, 1)
            p.sched = p.sched.set_dim_name(isl._isl.dim_type.out,
                                           time_dim, '_tmp' + dim_name)
            sched_dim = p.sched.find_dim_by_name(isl._isl.dim_type.out,
                                                 '_shift' + dim_name)

            eqs = []
            coeff = {}
            coeff[('out', time_dim)] = 1
            coeff[('out', sched_dim)] = -1
            eqs.append(coeff)
            p.sched = add_constraints(p.sched, [], eqs)
            p.sched = p.sched.remove_dims(isl._isl.dim_type.out, sched_dim, 1)
            p.sched = p.sched.set_dim_name(isl._isl.dim_type.out,
                                           time_dim, '_shift' + dim_name)

    return

def getDomainDimCoeffs(self, sched, arg):
    domDimCoeff = {}
    if (isAffine(arg)):
        coeff = getAffineVarAndParamCoeff(arg)
        for item in coeff:
            if type(item) == Variable:
                dim = sched.find_dim_by_name(isl._isl.dim_type.in_,
                                             item.name)
                domDimCoeff[dim] = coeff[item]
    return domDimCoeff

def getParamCoeffs(self, sched, arg):
    paramCoeff = {}
    if (isAffine(arg)):
        coeff = getAffineVarAndParamCoeff(arg)
        for item in coeff:
            if type(item) == Parameter:
                dim = sched.find_dim_by_name(isl._isl.dim_type.param,
                                             item.name)
                paramCoeff[dim] == coeff[item]
    return paramCoeff
