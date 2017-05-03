import numpy as np
import time
import sys

from __init__ import *

from init import init_all
from printer import print_header, print_config, print_line
from builder import create_lib,build_maxfilter
from exec_pipe import maxfilter
#from app_tuner import auto_tune

app = "max_filter"

def main():
    print_header()

    app_data = {}
    app_data['app'] = app
    app_data['ROOT'] = ROOT

    init_all(app_data)
    print_config(app_data)

    if app_data['mode'] == 'tune+':
        for g_size in [3, 5, 7, 10, 15]:
            create_lib(build_maxfilter, app, app_data, g_size)
            for t in range (0, 5):
                print ("Running for iteration #", t)
                maxfilter(app_data)
    elif app_data['mode'] == 'tune':
        auto_tune(pipe_data,app_data)
        pass
    else:
        create_lib(build_maxfilter, app, app_data)
        for t in range (0, 5):
            maxfilter(app_data)

    return

main()
