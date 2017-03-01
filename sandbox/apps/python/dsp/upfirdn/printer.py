import sys

def print_line(to_file=None):
    if to_file:
        print("--------------------------------------------------", file=to_file)
    else:
        print("--------------------------------------------------")

def print_header():
    print("Signal Upsample, FIR filter, and downsample")

def print_usage():
    print("[main]: Usage: ")
    print("[main]: "+sys.argv[0]+" <mode> <image> ", end=" ")
    print("<rows> <cols> <nruns>")
    print("[main]: <mode>  :: {'new', 'existing', 'tune'}")

def print_config(app_data):
    app_args = app_data['app_args']
    fir_len = app_data['fir_len']
    sig_len = app_data['sig_len']
    up = app_data['up']
    down = app_data['down']
    print_line()
    print("# Problem Settings #")
    print("")
    print("[main]: mode        =", app_args.mode)
    #print("[main]: image       =", app_args.img_file)
    print("[main]: FIR filter coefficient vector length  =", fir_len)
    print("[main]: signal length  =", sig_len)
    print("[main]: upsampling rate  =", up)
    print("[main]: downsampling rate  =", down)
    print("[main]: nruns       =", app_args.runs)
    print_line()
