import sys
import subprocess

sys.path.insert(0, '../../../../optimizer')
sys.path.insert(0, '../../../../frontend')

from Compiler   import *
from Constructs import *

def cCompile(inFile, outFile, cCompiler=None):
    if cCompiler == None or cCompiler == "intel":
        cxx = "icpc"
        opt = "-openmp -xhost -O3 -ipo -ansi-alias"
    elif cCompiler == "gnu":
        cxx = "g++"
        opt = "-fopenmp -march=native -O3 -ftree-vectorize"
    #fi

    inc = "-I../../../memory_allocation/ "+\
          "../../../memory_allocation/simple_pool_allocator.cpp"
    shared = "-fPIC -shared"
    out = "-o "+outFile

    compileStr = cxx + " " \
               + opt + " " \
               + inc + " " \
               + shared + " " \
               + inFile + " " \
               + out

    print
    print "[compiler]: compiling residual function to", outFile, "..."
    print ">", compileStr
    subprocess.check_output(compileStr, shell=True)
    print "[compiler]: ... DONE"

    return