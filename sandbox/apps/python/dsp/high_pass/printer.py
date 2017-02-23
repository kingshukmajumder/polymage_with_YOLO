import sys

def print_line(to_file=None):
    if to_file:
        print("--------------------------------------------------", file=to_file)
    else:
        print("--------------------------------------------------")

def print_header():
    print("Signal High Pass Filtering")

def print_usage():
    print("[main]: Usage: ")
    print("[main]: "+sys.argv[0]+" <mode> <image> ", end=" ")
    print("<rows> <cols> <nruns>")
    print("[main]: <mode>  :: {'new', 'existing', 'tune'}")

def print_config(app_data):
    app_args = app_data['app_args']
    length = app_data['length']
    cutoff = app_data['cutoff']
    factor = app_data['factor']
    print_line()
    print("# Problem Settings #")
    print("")
    print("[main]: mode        =", app_args.mode)
    #print("[main]: image       =", app_args.img_file)
    print("[main]: signal length  =", length)
    print("[main]: cutoff frequency in Hz =", cutoff)
    print("[main]: attenuation factor =", factor)
    print("[main]: nruns       =", app_args.runs)
    print_line()
