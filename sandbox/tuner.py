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
# tuner.py : autotuning by codegen, compilation and execution of various
#            configurations of grouping and tile sizes.
#

import ctypes
import _ctypes
import pipe
import constructs
import subprocess
import time
import string
import random
import sys
import os

from compiler import *
from utils import *

# print to multiple files
def print_to(s, to_file, _end="\n"):
    for f in to_file:
        print(s, file=f, end=_end)

# print a line
def print_line(to_file):
    print_to("--------------------------------------------------", to_file)

def dynamic_display(plot_data):
    '''
    DEFUNCT - something wrong with forking the processes, can't use when
    configs are too many
    '''
    plot_gnu(plot_data)

    out_file = plot_data['out_file']
    subprocess.check_output("sleep 0.5", shell=True)
    new_proc = subprocess.Popen(["eog", str(out_file)])

    if 'old_proc' in plot_data:
        old_proc = plot_data['old_proc']
        old_proc.kill()

    plot_data['old_proc'] = new_proc

    return

def plot_gnu(plot_data):
    xmin = 0
    xmax = plot_data['configs']+1
    tmin = plot_data['min_time']
    tmax = plot_data['max_time']
    diff = tmax - tmin
    if diff == 0:
        diff = 10
    ymin = tmin - (diff / 10)
    ymax = tmax + (diff / 10)
    out_file = plot_data['out_dir']+"/"+"out.png"
    in_file = plot_data['in_file']

    cmd = "set terminal png; "
    cmd += "set output '"+out_file+"'; "
    cmd += "set xrange ["+str(xmin)+":"+str(xmax)+"]; "
    cmd += "set yrange ["+str(ymin)+":"+str(ymax)+"]; "
    cmd += "set arrow 1 from " + \
           str(xmin)+","+str(tmin) + " to " +\
           str(xmax)+","+str(tmin) + " nohead; "
    cmd += "plot '"+in_file+"' with lines; "

    gnuplot_str = "gnuplot -e \""+cmd+"\""
    subprocess.check_output(gnuplot_str, shell=True)

    plot_data['out_file'] = out_file

    return

# TODO:
# 1. Introduce parallelism in code generation and compilation           ( )
# 2. Make the search configurations in each space a Set before
#    enumerating                                                        ( )
#
def generate(_tuner_arg_data):

    # unpack the arguments from the arg dictionary
    try:
        _tuner_app_name = _tuner_arg_data['_tuner_app_name']
    except KeyError:
        print('tuner : generator : \'_tuner_app_name\' - \
               not an optional parameter')

    try:
        _tuner_pipe_name = _tuner_arg_data['_tuner_pipe_name']
    except KeyError:
        _tuner_pipe_name = None

    try:
        _tuner_live_outs = _tuner_arg_data['_tuner_live_outs']
    except KeyError:
        print('tuner : generator : \'_tuner_live_outs\' - \
                not an optional parameter')

    try:
        _tuner_param_constraints = _tuner_arg_data['_tuner_param_constraints']
    except KeyError:
        _tuner_param_constraints = None

    try:
        _tuner_param_estimates = _tuner_arg_data['_tuner_param_estimates']
    except KeyError:
        _tuner_param_estimates = None

    try:
        _tuner_tile_size_configs = _tuner_arg_data['_tuner_tile_size_configs']
    except KeyError:
        _tuner_tile_size_configs = None

    try:
        _tuner_group_size_configs = _tuner_arg_data['_tuner_group_size_configs']
    except KeyError:
        _tuner_group_size_configs = None

    try:
        _tuner_opts = _tuner_arg_data['_tuner_opts']
    except KeyError:
        _tuner_opts = []

    # for now, assume the following option to be deprecated
    '''
    try:
        _tuner_inline_directives = _tuner_arg_data['_tuner_inline_directives']
    except KeyError:
        _tuner_inline_directives = None
    '''

    try:
        _tuner_dst_path = _tuner_arg_data['_tuner_dst_path']
    except KeyError:
        _tuner_dst_path = '/tmp'

    try:
        _tuner_cxx_string = _tuner_arg_data['_tuner_cxx_string']
    except KeyError:
        _tuner_cxx_string = None

    try:
        _tuner_root_path = _tuner_arg_data['_tuner_root_path']
    except KeyError:
        if 'pool_alloc' in _tuner_opts and not _tuner_cxx_string:
            print('tuner : generator : \'_tuner_root_path\' - \
                    not set, but is required for \'pool_alloc\'')
        else:
            _tuner_root_path = None

    try:
        _tuner_debug_flag = _tuner_arg_data['_tuner_debug_flag']
    except KeyError:
        _tuner_debug_flag = False

    # make a list of files to which the strings are to be broadcasted
    dump_files = []

    if _tuner_debug_flag:
        dump_files.append(sys.stdout)

    def print_params(to_file=[]):
        if to_file.__len__() == 0:
            return

        # print the details of the args
        print_line(to_file)
        print_to("App name                : \""+_tuner_app_name+"\"", to_file)
        print_to("Code Path               : \""+_tuner_dst_path+"\"", to_file)
        print_to("Live-out Functions      :", to_file, " ")
        for func in _tuner_live_outs:
            print_to("\""+func.name+"\",", to_file, " ")
        print_to("\nParameter Constraints   :", to_file, " ")
        for constraint in _tuner_param_constraints:
            print_to(constraint, to_file, " ")
        print_to("\nParameter Estimates     :", to_file, " ")
        for estimate in _tuner_param_estimates:
            print_to((estimate[0].name, estimate[1]), to_file, " ")
        
        if (_tuner_tile_size_configs != None):
            print_to("\nTile sizes              :", to_file)
            for tile_sizes in _tuner_tile_size_configs:
                print_to(tile_sizes, to_file,)
        print_to("\nGroup sizes             :", to_file)
        for group_sizes in _tuner_group_size_configs:
            print_to(group_sizes, to_file, " ")
        '''
        print_to("\nfunctions to be inlined:", to_file, " ")
        for func in _tuner_inline_directives:
            print_to("\""+func.name+"\",", to_file, " ")
        '''
        print("")

    app_name = _tuner_app_name+'_polymage_'

    def random_string():
        # for now, using a random string of length 10 
        # as subdir name
        return ''.join(random.SystemRandom().choice(
                    string.ascii_lowercase + \
                    string.ascii_uppercase + \
                    string.digits) \
                    for _ in range(10))
 
    # ensure that a subdirectory is created, with a name not conflicting with
    # existing ones
    dst_sub_dir = str(_tuner_dst_path)+'/'+'Poly'+random_string()+'Mage/'
    while os.path.exists(dst_sub_dir):
        dst_sub_dir =str(_tuner_dst_path)+'/'+'Poly'+random_string()+'Mage/'

    # subdirectories and files
    os.makedirs(dst_sub_dir)
    prog_prefix = str(dst_sub_dir)+str(app_name)
    config_file_name = str(dst_sub_dir)+'configurations.txt'
    config_file = open(config_file_name, 'a')
    dump_files.append(config_file)

    # Compile String parts
    if not _tuner_cxx_string:
        #cxx='icpc'
        #opt_flags='-openmp -xhost -O3 -ansi-alias'
        cxx='g++'
        opt_flags='-fopenmp -march=native -O3 -ftree-vectorize'
        shared_lib_flags='-fPIC -shared'
        if 'pool_alloc' in _tuner_opts:
            include_flags='-I'+_tuner_root_path+'/memory_allocation/'+ \
                _tuner_root_path+'/memory_allocation/simple_pool_allocator.cpp'
        else:
            include_flags=''
        other_CXX=''
        _tuner_cxx_string = cxx+' '+ \
                            opt_flags+' '+ \
                            shared_lib_flags+' '+ \
                            include_flags+' '+ \
                            other_CXX+' '

    # Generate group sizes automatically, if none is specified by the user.
    # TODO:
    # 1. Limit the configuration space to the total number of
    #    functions in the pipeline, since any group size greater
    #    than that will lead to redundancy.                             ( )
    #
    if _tuner_group_size_configs == None:
        for i in range(1, 4):
            _tuner_group_size_configs.append(i)
        # Assuming that the number of functions does not exceed
        # this maximum, include a "group-all"
        _tuner_group_size_configs.append(200)

    print_params(dump_files)

    # file close
    dump_files.remove(config_file)
    config_file.close()

    _tuner_config = 0

    total_t1 = time.time()
    # iterate over tile_sizes
    if (_tuner_tile_size_configs == None):
        _tuner_tile_size_configs = [16,256]
        
    for _tuner_tile_size in _tuner_tile_size_configs:
    # iterate over group_sizes
        for _tuner_group_size in _tuner_group_size_configs:
            _tuner_config += 1

            # Update configs file:
            config_file = open(config_file_name, 'a')
            dump_files.append(config_file)

            print_line(dump_files)
            print_to("Config     : #"+str(_tuner_config), dump_files)
            print_to("Tile sizes : "+str(_tuner_tile_size), dump_files)
            print_to("Group size : "+str(_tuner_group_size), dump_files)

            # .cpp and .so files
            c_file_name = str(prog_prefix)+str(_tuner_config)+'.cpp'
            so_file_name = str(prog_prefix)+str(_tuner_config)+'.so'
            #dot_file_name = str(prog_prefix)+str(_tuner_config)+'.dot'

            t1 = time.time()

            # building the pipeline :
            _tuner_build_error = False
            #try:
            if (True):
                _tuner_pipe = buildPipeline(
                                 _tuner_live_outs,
                                 param_constraints=_tuner_param_constraints,
                                 param_estimates=_tuner_param_estimates,
                                 tile_sizes=_tuner_tile_size,
                                 group_size=_tuner_group_size,
                                 options=_tuner_opts,
                                 pipe_name=_tuner_pipe_name)
            #except:
            #    _tuner_build_error = True
            #finally:
            #    pass

            # code generation :
            if _tuner_build_error is True:
                print_to("[ERROR] Build fail ...", dump_files)
            else:
                c_file = open(c_file_name, 'a')
                c_file.write(_tuner_pipe.generate_code(is_extern_c_func=True, \
                                                       are_io_void_ptrs=True).__str__())
                c_file.close()

                '''
                g = _tuner_pipe.draw_pipeline_graph_with_groups()
                g.write(dot_file_name)
                '''

            t2 = time.time()

            # print the polymage code compilation and cpp code generation time
            codegen_time = float(t2) - float(t1)
            print_to("Code Generation Time   : "+str(codegen_time*1000)+"ms",
                      dump_files)

            # compilation :
            cxx_string = _tuner_cxx_string+" "+c_file_name+" -o "+so_file_name
            _tuner_compile_error = False

            t1 = time.time()
            try:
                subprocess.check_output(cxx_string, shell=True)
                pass
            except:
                _tuner_compile_error = True
            finally:
                pass
            t2 = time.time()

            if _tuner_compile_error is True:
                print_to("[ERROR] Compilation aborted ...",
                         dump_files)
            else:
                compile_time = float(t2) - float(t1)
                print_to("Compilation Time       : "+str(compile_time*1000)+"ms",
                          dump_files)
                # total time for this variant:
                print_to("Total                  : "+\
                          str((codegen_time+compile_time)*1000)+"ms",
                          dump_files)

            # file close
            dump_files.remove(config_file)
            config_file.close()

    total_t2 = time.time()
    total_time = float(total_t2) - float(total_t1)

    # file open
    config_file = open(config_file_name, 'a')
    dump_files.append(config_file)

    print_line(dump_files)
    # print the time taken by the tuner to generate and compile all variants
    print_to("Time taken to generate all variants : ", dump_files)
    print_to(str(total_time*1000)+"ms", dump_files)
    print_line(dump_files)

    # file close
    dump_files.remove(config_file)
    config_file.close()

    return dst_sub_dir, _tuner_config, _tuner_pipe

def execute(_tuner_arg_data):

    try:
        _tuner_custom_executor = _tuner_arg_data['_tuner_custom_executor']
    except KeyError:
        _tuner_custom_executor = None

    try:
        _tuner_pipe_arg_data = _tuner_arg_data['_tuner_pipe_arg_data']
    except KeyError:
        if _tuner_custom_executor:
            _tuner_pipe_arg_data = None
        else:
            print('tuner : executer : \'_tuner_pipe_arg_data\' - \
                   not an optional parameter')

    try:
        _tuner_app_data = _tuner_arg_data['_tuner_app_data']
    except KeyError:
        _tuner_app_data = None

    try:
        _tuner_app_name = _tuner_arg_data['_tuner_app_name']
    except KeyError:
        print('tuner : executer : \'_tuner_app_name\' - \
               not an optional parameter')

    try:
        _tuner_pipe = _tuner_arg_data['_tuner_pipe']
    except KeyError:
        print('tuner : executer : \'_tuner_pipe\' - \
               not an optional parameter')

    try:
        _tuner_src_path = _tuner_arg_data['_tuner_src_path']
    except KeyError:
        _tuner_src_path = "/tmp"

    try:
        _tuner_configs_count = _tuner_arg_data['_tuner_configs_count']
    except KeyError:
        _tuner_configs_count = 0

    try:
        _tuner_omp_threads = _tuner_arg_data['_tuner_omp_threads']
    except KeyError:
        _tuner_omp_threads = 1

    try:
        _tuner_nruns = _tuner_arg_data['_tuner_nruns']
    except KeyError:
        _tuner_nruns = 1

    try:
        _tuner_debug_flag = _tuner_arg_data['_tuner_debug_flag']
    except KeyError:
        _tuner_debug_flag = True

    # make a list of files to which the strings are to be broadcasted
    dump_files = []
    if _tuner_debug_flag:
        dump_files.append(sys.stdout)

    OMP_NUM_THREADS = str(_tuner_omp_threads)
    KMP_PLACE_THREADS = str(_tuner_omp_threads)+"c,1t"

    def print_params(to_file=[]):
        if len(to_file) == 0:
            return
        print_line(to_file)
        print_to("App Name              : \""+_tuner_app_name+"\"", to_file)
        print_to("Total Configurations  :"+str(_tuner_configs_count), to_file)
        print_to("OMP_NUM_THREADS       :"+OMP_NUM_THREADS, to_file)
        print_to("KMP_PLACE_THREADS     :"+KMP_PLACE_THREADS, to_file)
        print_to("Number of Tuning Runs :"+str(_tuner_nruns), to_file)

    # set other variables
    app_name = _tuner_app_name+'_polymage_'
    prog_prefix = str(_tuner_src_path)+'/'+str(app_name)

    date_time_now = time.strftime("%d-%m-%Y_%H.%M.%S")
    tuning_report_file_name = str(_tuner_src_path)+'/tuning_report'+'_'+str(date_time_now)+'.txt'

    tuning_report_file = open(tuning_report_file_name, 'a')
    dump_files.append(tuning_report_file)
    print_params(dump_files)
    dump_files.remove(tuning_report_file)
    tuning_report_file.close()

    tuning_plot_file_name = str(_tuner_src_path)+"/"+'plot'+'_'+str(date_time_now)+'.dat'

    _tuner_max_time = 1000000

    # TODO: iterate over thread count for tuning                ( )

    # set the thread-count
    os.environ["OMP_NUM_THREADS"] = OMP_NUM_THREADS
    os.environ["KMP_PLACE_THREADS"] = KMP_PLACE_THREADS

    # shared library function name
    lib_function_name = 'pipeline_'+_tuner_pipe.name

    # Parameters, Inputs (Images), Outputs
    _tuner_pipe_params, _tuner_pipe_inputs, _tuner_pipe_outputs = \
        get_ordered_cfunc_params(_tuner_pipe)
    pipe_func_params = [_tuner_pipe_params,
                        _tuner_pipe_inputs,
                        _tuner_pipe_outputs]

    # map function arguments to function parameters
    pipe_func_args = None
    if _tuner_pipe_arg_data:
        pipe_func_args = map_cfunc_args(pipe_func_params,
                                        _tuner_pipe_arg_data)

    plot_data = {}
    real_time_graph = False

    tuning_time_t1 = time.time()

    global_min_config = 0
    global_min_time = _tuner_max_time
    global_max_time = 0
    for _tuner_config in range(1, _tuner_configs_count+1):
        # log to file
        tuning_report_file = open(tuning_report_file_name, 'a')
        dump_files.append(tuning_report_file)

        print_line(dump_files)
        print_to("Config #"+str(_tuner_config)+" : ", dump_files, " ")

        # load shared library, name the function
        so_file_name = str(prog_prefix)+str(_tuner_config)+'.so'

        # load shared library
        _tuner_load_error = False

        try:
            lib_pipeline = ctypes.cdll.LoadLibrary(so_file_name)
        except:
            _tuner_load_error = True

        if _tuner_load_error :
            print_to("[ERROR] in loading shared library ...",
                      dump_files)
        else:
            pipeline_func = lib_pipeline[lib_function_name]

            # TODO:
            # 1. Switch between report types - whether
            #    to print min / average / gmean etc.                ( )
            # 2. Graphics plots                                     ( )
            #

            # start timer
            local_min_time = _tuner_max_time

            # run
            for run in range(1, _tuner_nruns+1):
                t1 = time.time()
                _tuner_runtime_error = False

                try:
                    if _tuner_custom_executor == None:
                        pipeline_func(*pipe_func_args)
                    else:
                        _tuner_custom_executor(lib_pipeline,
                                               pipeline_func,
                                               pipe_func_params,
                                               pipe_func_args,
                                               _tuner_arg_data,
                                               _tuner_app_data)
                except:
                    _tuner_runtime_error = True
                t2 = time.time()
                t_total = float(t2) - float(t1)

                # local minima
                if float(t_total) < float(local_min_time):
                    local_min_time = t_total

            if _tuner_runtime_error:
                print_to("[ERROR] Execution Aborted ...",
                         dump_files)
            else:
                # global minima
                if float(local_min_time) < float(global_min_time):
                    global_min_time = local_min_time
                    global_min_config = _tuner_config
                # global maxima
                if float(local_min_time) > float(global_max_time):
                    global_max_time = local_min_time

                print_to(str(local_min_time*1000)+" ms "+\
                         "("+str(global_min_time*1000)+" ms)",
                         dump_files)

            s = str(_tuner_config)+" "+str(local_min_time)
            tuning_plot_file = open(tuning_plot_file_name, 'a')
            print_to(s, [tuning_plot_file])
            tuning_plot_file.close()

            if real_time_graph:
                plot_data['configs'] = _tuner_configs_count
                plot_data['min_time'] = global_min_time
                plot_data['max_time'] = global_max_time
                plot_data['out_dir'] = str(_tuner_src_path)
                plot_data['in_file'] = tuning_plot_file_name
                # dynamic_display(plot_data)

        dump_files.remove(tuning_report_file)
        tuning_report_file.close()

    if not real_time_graph:
        plot_data['configs'] = _tuner_configs_count
        plot_data['min_time'] = global_min_time
        plot_data['max_time'] = global_max_time
        plot_data['out_dir'] = str(_tuner_src_path)
        plot_data['in_file'] = tuning_plot_file_name
        # plot_gnu(plot_data)

    tuning_report_file = open(tuning_report_file_name, 'a')
    dump_files.append(tuning_report_file)

    tuning_time_t2 = time.time()
    tuning_time = float(tuning_time_t2) - float(tuning_time_t1)

    # print the best config and time taken by it
    print_line(dump_files)
    print_to("Best Config :", dump_files)
    print_to("Config #"+str(global_min_config)+" -- ",
             dump_files, " ")
    print_to(str(global_min_time*1000)+"ms", dump_files)
    print_to("Src Path    : \""+_tuner_src_path+"\"", dump_files)

    print_line(dump_files)
    # print the toal time taken by the tuner to execute all configs
    print_to("Tuning Time :", dump_files)
    print_to(str(tuning_time*1000)+"ms", dump_files)
    print_line(dump_files)

    dump_files.remove(tuning_report_file)
    tuning_report_file.close()

    return
