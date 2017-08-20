from __init__ import *

import sys
import subprocess

sys.path.insert(0, ROOT+'/apps/python/')

from cpp_compiler import c_compile
from loader import load_lib
from polymage_crp import polymage_crp

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

def build_crp(app_data):
    pipe_data = app_data['pipe_data']

    out_crp = polymage_crp(pipe_data)
    
    live_outs = [out_crp]
    pipe_name = app_data['app']

    X1 = app_data['X1'] 
    Y1 = app_data['Y1'] 

    K1 = app_data['K1'] 
    K2 = app_data['K2'] 
    K3 = app_data['K3'] 
    K4 = app_data['K4'] 
    K5 = app_data['K5'] 
   
    C1 = app_data['C1'] 
    # C2 = app_data['C2'] 
    # C3 = app_data['C3'] 
    # C4 = app_data['C4'] 
    # C5 = app_data['C5'] 
   
    Fh1 = app_data['Fh1'] 
    Fh2 = app_data['Fh2'] 
    Fh3 = app_data['Fh3'] 
    Fh4 = app_data['Fh4'] 
    Fh5 = app_data['Fh5'] 
   
    Fw1 = app_data['Fw1'] 
    Fw2 = app_data['Fw2'] 
    Fw3 = app_data['Fw3'] 
    Fw4 = app_data['Fw4'] 
    Fw5 = app_data['Fw5'] 

    Fhm1 = app_data['Fhm1'] 
    Fhm2 = app_data['Fhm2'] 
    # Fhm3 = app_data['Fhm3'] 
    # Fhm4 = app_data['Fhm4'] 
    Fhm5 = app_data['Fhm5'] 
   
    Fwm1 = app_data['Fwm1'] 
    Fwm2 = app_data['Fwm2'] 
    # Fwm3 = app_data['Fwm3'] 
    # Fwm4 = app_data['Fwm4'] 
    Fwm5 = app_data['Fwm5'] 


    #p_estimates = [(R1, rows1), (C1, cols1), (R2, rows2), (C2, cols2)]
    #p_constraints = [ Condition(R1, "==", rows1), \
    #                  Condition(C1, "==", cols1), \
    #                  Condition(R2, "==", rows2), \
    #                  Condition(C2, "==", cols2), \
    #                ]
    t_size = [16, 16]
   # g_size = 1
    opts = []
    if app_data['early_free']:
        opts += ['early_free']
    if app_data['optimize_storage']:
        opts += ['optimize_storage']
    if app_data['pool_alloc']:
        opts += ['pool_alloc']

    pipe = buildPipeline(live_outs,
                         #param_estimates=p_estimates,
                         #param_constraints=p_constraints,
                         #tile_sizes = t_size,
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
