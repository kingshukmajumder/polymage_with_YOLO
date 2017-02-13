import sys

def print_line(to_file=None):
    if to_file:
        print("--------------------------------------------------", file=to_file)
    else:
        print("--------------------------------------------------")

def print_header():
    print("Signal Windowing")

def print_usage():
    print("[main]: Usage: ")
    print("[main]: "+sys.argv[0]+" <mode> <image> ", end=" ")
    print("<rows> <cols> <nruns>")
    print("[main]: <mode>  :: {'new', 'existing', 'tune'}")

def print_config(app_data):
    app_args = app_data['app_args']
    length = app_data['length']
    win_type = app_data['type']
    win_map = {0 : "hamming", 1 : "hanning", 2 : "bartlett", 3 : "blackman",
               4 : "nuttall", 5 : "blackman-harris", 6 : "blackman-nuttall",
               7 : "flat top", 8 : "dirichlet"}
    print_line()
    print("# Problem Settings #")
    print("")
    print("[main]: mode        =", app_args.mode)
    #print("[main]: image       =", app_args.img_file)
    print("[main]: signal length  =", length)
    print("[main]: window type =", win_map[win_type])
    print("[main]: nruns       =", app_args.runs)
    print_line()
