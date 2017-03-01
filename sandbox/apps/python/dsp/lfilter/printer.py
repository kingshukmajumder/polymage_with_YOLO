import sys

def print_line(to_file=None):
    if to_file:
        print("--------------------------------------------------", file=to_file)
    else:
        print("--------------------------------------------------")

def print_header():
    print("Signal Difference-equation filtering")

def print_usage():
    print("[main]: Usage: ")
    print("[main]: "+sys.argv[0]+" <mode> <image> ", end=" ")
    print("<rows> <cols> <nruns>")
    print("[main]: <mode>  :: {'new', 'existing', 'tune'}")

def print_config(app_data):
    app_args = app_data['app_args']
    sig_len = app_data['sig_len']
    blength = app_data['blength']
    alength = app_data['alength']
    print_line()
    print("# Problem Settings #")
    print("")
    print("[main]: mode        =", app_args.mode)
    #print("[main]: image       =", app_args.img_file)
    print("[main]: signal length  =", sig_len)
    print("[main]: numerator coefficient vector length  =", blength)
    print("[main]: denominator coefficient vector length  =", alength)
    print("[main]: nruns       =", app_args.runs)
    print_line()
