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
        for g_size in [3, 5, 7, 10, 15, 30, 50]:
            create_lib(build_pyramid, app, app_data, g_size)
            for t in range (0, 5):
                print ("Running for iteration #", t)
                pyramid_blending(app_data)
    elif app_data['mode'] == 'tune' or app_data['mode'] == 'tune_execute':
        auto_tune(app_data)
        pass
    else:
        create_lib(build_pyramid, app, app_data)
        pyramid_blending(app_data)

    return

main()
