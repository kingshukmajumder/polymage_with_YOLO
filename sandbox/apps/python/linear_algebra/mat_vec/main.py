import numpy as np
import time
import sys

from __init__ import *

from init import init_all
from printer import print_header, print_config, print_line
from builder import create_lib,build_matvec
from exec_pipe import matvec

#from app_tuner import auto_tune

app = "matvec"

def main():
    # printer.py
    print_header()
    #--------------
    # Empty data 
    app_data = {}
    # app=matvec
    app_data['app'] = app
    # from __init__.py
    app_data['ROOT'] = ROOT
    #---------------
    # print('---------->',app_data)
    # ~/init.py
    init_all(app_data)
    # print('---------->',app_data)
    # ~/printer.py
    print_config(app_data)

    if app_data['mode'] == 'tune':
        auto_tune(app_data)
    else:
        # ~/builder.py
        create_lib(build_matvec, app, app_data)
        matvec(app_data)

    return


main()
