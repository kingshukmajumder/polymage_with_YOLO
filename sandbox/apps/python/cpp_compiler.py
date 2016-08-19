import sys
import subprocess

def gen_compile_string(app_data,in_file,out_file):
    ROOT = app_data['ROOT']
    arg_data = app_data['app_args']
    # CXX compiler and flags :
    cxx = arg_data.cxx
    cxx_flags = arg_data.cxx_flags
    #fi

    # Include Flags :
    include = ""
    if bool(arg_data.pool_alloc):
        include = "-I"+ROOT+"/memory_allocation/ "+\
                  ROOT+"/memory_allocation/simple_pool_allocator.cpp "
    if arg_data.blas:
          if bool(arg_data.blas):
            include += "-I /opt/OpenBLAS/include -L /opt/OpenBLAS/lib -lopenblas "

    # Shared library Flags
    shared = "-fPIC -shared"

    compile_str = cxx + " " \
                + in_file + " -o " + out_file + " "\
                + cxx_flags + " " \
                + include + " " \
                + shared + " " \

    app_data['cxx_string'] = compile_str

    return

def c_compile(in_file, out_file, app_data):
    #compile_str = " " + in_file + " -o " + out_file
    gen_compile_string(app_data,in_file,out_file)

    compile_str = app_data['cxx_string']
    #compile_str += " " + in_file + " -o " + out_file

    print("")
    print("[cpp_compiler]: compiling", in_file, "to", out_file, "...")
    print(">", compile_str)
    subprocess.check_output(compile_str, shell=True)
    print("[cpp_compiler]: ... DONE")

    return
