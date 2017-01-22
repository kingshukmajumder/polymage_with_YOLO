#!/usr/bin/env python3
import subprocess
import tabulate
import time
import uuid

compile_bool = True
# NOTE: Uncomment the following line to avoid compilation
#compile_bool = False

# NOTE: This variable decides the number of runs for execution
num_trials = 3

sort_fields = ['min', 'max', 'avg']
# NOTE: This string decides the key for sorting of the output table
sort_using = sort_fields[0]

compiler_flags = {}
compiler_flags['gcc'] = 'g++ -O3 -march=native -fopenmp -ftree-vectorize'
compiler_flags['icpc'] = 'icpc -O3 -xhost -openmp'
compiler_flags['clang'] = 'clang++ -O3'

common_flags = '-lrt'

preprocessor_flags = {}
preprocessor_flags['direct'] = ''
preprocessor_flags['indirect'] = '-DINDIRECT'

versions = ['direct', 'indirect']

cpp_source = \
"""
#include<stdio.h>
#include<stdlib.h>
#include<time.h>
#include<iostream>

#ifndef INDIRECT
    #define IC(t, x, y) ( A[((t)%2) * R * C + (x) * C + (y)] )
#else
    #define IC(t, x, y) ( buf[(t)%2][(x) * C + (y)] )
#endif

#ifdef TIMER
    #define TIME(x) x
#else
    #define TIME(x)
#endif

using namespace std;

#define R 4096
#define C 4096
#define T 100

timespec diff(timespec start, timespec end)
{
    timespec temp;
    if ((end.tv_nsec-start.tv_nsec)<0) {
        temp.tv_sec = end.tv_sec-start.tv_sec-1;
        temp.tv_nsec = 1000000000+end.tv_nsec-start.tv_nsec;
    } else {
        temp.tv_sec = end.tv_sec-start.tv_sec;
        temp.tv_nsec = end.tv_nsec-start.tv_nsec;
    }
    return temp;
}

int main()
{
    double *A, *buf[2];

    TIME(timespec begin);
    TIME(timespec end);

    A = (double *)malloc(sizeof(double) * R * C * 2);
    buf[0] = A;
    buf[1] = A + R*C;

    // #pragma omp parallel for collapse(2)
    for(int i = 0; i < R; i++){
        for(int j = 0; j < C; j++){
            A[i*C + j] = 1.0;
            A[R*C + i*C + j] = 0.0;
    }}

    TIME(clock_gettime(CLOCK_REALTIME, &begin));
    for(int t = 0; t < T; t++){
        #pragma omp parallel for collapse(2)
        for(int i = 1; i < R-1; i++){
            for(int j = 1; j < R-1; j++){
                IC(t+1, i, j) = \
                    IC(t, i  , j  ) + \
                    IC(t, i-1, j-1) + \
                    IC(t, i  , j-1) + \
                    IC(t, i+1, j-1) + \
                    IC(t, i-1, j  ) + \
                    IC(t, i  , j  ) + \
                    IC(t, i+1, j  ) + \
                    IC(t, i-1, j+1) + \
                    IC(t, i  , j+1) + \
                    IC(t, i+1, j+1);
    }}}

    TIME(clock_gettime(CLOCK_REALTIME, &end));
    TIME(std::cout <<diff(begin,end).tv_sec <<" . " <<diff(begin,end).tv_nsec <<std::endl);

    return (0);
}
"""

def get_filename(version, compiler):
    return version + '_' + compiler + '.out'

def compile_variants(src_filename):
    for version in versions:
        for compiler in compiler_flags:
            filename = get_filename(version, compiler)
            build_str = compiler_flags[compiler] + ' ' + \
                        common_flags + ' ' + \
                        preprocessor_flags[version] + ' ' + \
                        src_filename + \
                        ' -o ' + filename

            print("generating " + filename + "\nbuild string: " + build_str + "\n" + '-' * 10)
            subprocess.check_output(build_str, shell=True)
    return

def run_variant(version, compiler):
    """returns elapsed time in seconds"""
    filename = get_filename(version, compiler)
    begin_time = time.time()
    subprocess.check_output('./' + filename, shell=True)
    end_time = time.time()
    elapsed_time = end_time - begin_time

    return elapsed_time

def run_all_variants():
    times = {}
    for compiler in compiler_flags:
        if compiler == 'clang': continue
        times[compiler] = {}
        for version in versions:
            times[compiler][version] = []
            print("*** running test for %s: %s ***" % (compiler, version))
            for i in range(0, num_trials):
                trial_time_str = "\ttrial #%s..." % (i + 1, )
                print(trial_time_str, end="", flush=True)
                runtime = run_variant(version, compiler)
                print(" | runtime: %s sec" % runtime)
                times[compiler][version].append(runtime)
    
    return times

def pretty_print_times(times):
    # collection of all rows
    rows = []

    if sort_using == 'min':
        key_index = 2
    elif sort_using == 'max':
        key_index = 3
    elif sort_using == 'avg':
        key_index = 4

    for compiler in compiler_flags:
        if compiler == 'clang': continue
        # row specific to this compiler. Ordered by min time across variants
        compiler_rows = []
        for version in versions:
            mintime = min(times[compiler][version])
            maxtime = max(times[compiler][version])
            avgtime = sum(times[compiler][version]) / float(num_trials)
            compiler_rows.append([compiler, version, mintime, maxtime, avgtime])
        compiler_rows = sorted(compiler_rows, key=lambda row: row[key_index])
        rows += compiler_rows

    print(tabulate.tabulate(rows, headers = ["Compiler", "Version", "Min (sec)", "Max (sec)", "Avg (sec)"]))

    return

def test_runner(cpp_filename):
    if compile_bool:
        compile_variants(cpp_filename)
    times = run_all_variants()
    pretty_print_times(times)


if __name__ == "__main__":
    cpp_filename = str(uuid.uuid4()) + ".cpp"
    cpp_file = open(cpp_filename, "w")
    cpp_file.write(cpp_source)
    cpp_file.close()

    try:
        test_runner(cpp_filename)
    except KeyboardInterrupt:
        print("\nexiting cleanly...")

    import os
    os.remove(cpp_filename)
