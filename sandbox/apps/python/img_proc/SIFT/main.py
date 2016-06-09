#This is the main.py for SIFT

import numpy as np
import time
import sys

from __init__ import *

from init import init_all
from printer import print_header, print_config, print_line
from builder import create_lib,build_pyramid
from exec_pipe import sift
from app_tuner import auto_tune

app = "sift"

def main():
    print_header()

    app_data = {}
    app_data['app'] = app
    app_data['ROOT'] = ROOT

    init_all(app_data)
    print_config(app_data)
    if app_data['mode'] == 'tune' or app_data['mode'] == 'tune_execute':
        auto_tune(app_data)
        pass
    else:
        create_lib(build_pyramid, app, app_data)
        sift(app_data)
    return

main()
