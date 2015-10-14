from __future__ import absolute_import, division, print_function

import pipe
import poly
import logging

logging.basicConfig(format="%(levelname)s: %(name)s: %(message)s")

def buildPipeline(outputs,
                  param_estimates = [],
                  param_constraints = [],
                  grouping = [],
                  inline_directives = [],
                  tile_sizes = [],
                  size_threshold = None,
                  pipe_name = None,
                  options = []):

    # Create an isl context that will be used for all polyhedral
    # operations during compilation.
    ctx = poly.isl.Context()

    if tile_sizes == []:
        tile_sizes = [16, 16, 16]

    return pipe.Pipeline(_ctx = ctx,
                         _outputs = outputs,
                         _param_estimates = param_estimates,
                         _param_constraints = param_constraints,
                         _grouping = grouping,
                         _inline_directives = inline_directives,
                         _tile_sizes = tile_sizes,
                         _size_threshold = size_threshold,
                         _name = pipe_name,
                         _options = options)
