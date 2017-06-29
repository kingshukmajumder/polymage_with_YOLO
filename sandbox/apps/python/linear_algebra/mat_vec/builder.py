from __init__ import *

import sys
import subprocess

sys.path.insert(0, ROOT+'/apps/python/')

from cpp_compiler import c_compile
from loader import load_lib
from polymage_matvec import matvec

from compiler import *
from constructs import *

def codegen(pipe, file_name, app_data):
    print("")
    print("[builder]: writing the code to", file_name, "...")
    code = pipe.generate_code(is_extern_c_func=True,
                              are_io_void_ptrs=True)

    f = open(file_name, 'w')
    f.write(code.__str__())
    f.close()

    return

def generate_graph(pipe, file_name, app_data):
    graph_file = file_name+".dot"
    png_graph = file_name+".png"

    print("")
    print("[builder]: writing the graph dot file to", graph_file, "...")

    graph = pipe.pipeline_graph
    graph.write(graph_file)
    print("[builder]: ... DONE")

    dotty_str = "dot -Tpng "+graph_file+" -o "+png_graph

    print("")
    print("[builder]: drawing the graph using dotty to", png_graph)
    print(">", dotty_str)
    subprocess.check_output(dotty_str, shell=True)
    print("[builder]: ... DONE")

    return

def create_tile_sizes_file(t_sizes):
    file_name = "tile.sizes"
    tile_file = open(file_name, 'w')
    for tile_size in t_sizes:
        tile_file.write(str(tile_size) + "\n")
    tile_file.close()
    return

def build_matvec(app_data):
    pipe_data = app_data['pipe_data']
    # matmul function in polymage_matvec.py 
    out_matvec = matvec(pipe_data) #<------------------------------------------------------------------How are we able to handle mat1 * v1 || mat1* mat2
    # print('!!!!!!!!!!!!!!!',out_matvec)
    R = pipe_data['R']
    C = pipe_data['C']
    #R2 = pipe_data['R2']
    #C2 = pipe_data['C2']

    # live_outs implies all the Outputs
    # This implies that only one value was returned
    if not isinstance(out_matvec, list):
        live_outs = [out_matvec]
    else:
        live_outs = out_matvec

    pipe_name = app_data['app']

    rows1 = app_data['rows1']
    cols1 = app_data['cols1']
    #rows2 = app_data['rows2']
    #cols2 = app_data['cols2']
    #----------------------------------------------------------------------------Why are we using p_estimates and p_constraints
    p_estimates = [(R, rows1), (C, cols1)] #, (R2, rows2), (C2, cols2)]
    p_constraints = [ Condition(R, "==", rows1), \
                      Condition(C, "==", cols1) \
                      #Condition(R2, "==", rows2), \
                      #Condition(C2, "==", cols2), \
                    ]

    # Pluto schedule requires tile.sizes file
    if(app_data['pluto']):
        t_size = app_data['tiles'].split(',')
        create_tile_sizes_file(t_size)

    g_size = 1
    opts = []
    if app_data['early_free']:
        opts += ['early_free']
    if app_data['optimize_storage']:
        opts += ['optimize_storage']
    if app_data['pool_alloc']:
        opts += ['pool_alloc']
    if app_data['blas'] == 'OpenBLAS':
        opts += ['openblas']
    if app_data['blas'] == 'MKL':
        opts += ['mkl']
    if app_data['pluto']:
        opts += ['pluto']
    # call to buildPipeleine() in builder.py file
    pipe = buildPipeline(live_outs,
                         param_estimates=p_estimates,
                         param_constraints=p_constraints,
                         #group_size = g_size,
                         options = opts,
                         pipe_name = pipe_name)
    return pipe

def create_lib(build_func, pipe_name, app_data):
    mode = app_data['mode']
    pipe_src  = pipe_name+".cpp"
    pipe_so   = pipe_name+".so"
    app_args = app_data['app_args']
    graph_gen = bool(app_args.graph_gen)

    if build_func != None:
        if mode == 'new':
            # build_func() ----> build_matmul() builder.py
            # build the polymage pipeline
            pipe = build_func(app_data)

            # draw the pipeline graph to a png file
            if graph_gen:
                generate_graph(pipe, pipe_name, app_data)

            # generate pipeline cpp source
            codegen(pipe, pipe_src, app_data)

    if mode != 'ready':
        # compile the cpp code
        c_compile(pipe_src, pipe_so, app_data)

    # load the shared library
    lib_func_name = "pipeline_"+pipe_name
    load_lib(pipe_so, lib_func_name, app_data)

    return
