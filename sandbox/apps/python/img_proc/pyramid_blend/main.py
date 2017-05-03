import numpy as np
import time
import sys

from __init__ import *

from init import init_all
from printer import print_header, print_config, print_line
from builder import create_lib,build_pyramid
from exec_pipe import pyramid_blending
from app_tuner import auto_tune

app = "pyramid_blend"

def main():
    print_header()

    app_data = {}
    app_data['app'] = app
    app_data['ROOT'] = ROOT

    init_all(app_data)
    print_config(app_data)
    if app_data['mode'] == 'tune+':
        for g_size in [3, 5, 7]:
            for t1 in [8, 16, 32, 64, 128, 256]:
                for t2 in [8, 16, 32, 64, 128, 256]:
                    create_lib(build_pyramid, app, app_data, g_size, [t1, t2])
                    for t in range (0, 0):
                        print ("Running for iteration #", t)
                        pyramid_blending(app_data)
    elif app_data['mode'] == 'tune' or app_data['mode'] == 'tune_execute':
        auto_tune(app_data)
        pass
    else:
        create_lib(build_pyramid, app, app_data)
        min_avg = 100000
        for r in range (0,5):
            min_avg = min (min_avg, pyramid_blending(app_data))
        print ("Minimum Average Time ", min_avg)

    return

main()
