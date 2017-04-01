from __init__ import *

import sys
import subprocess
import numpy as np
from fractions import Fraction

sys.path.insert(0, ROOT)

from compiler import *
from constructs import *

def sub_band(pipe_data):

    N = Parameter(UInt, "N")

    pipe_data['N'] = N

    x = Variable(UInt, 'x')

    y = Wave(Double, "sig", N)

    L = 2
    length = 25
    wc = 1 / L # Cut-off frequency

    lp = Wave.firwin(length-1, wc, "lp_filt")
    hp = Wave.firwin(length, wc, "hp_filt", pass_zero=False)

    yl = y.lfilter_fir(lp, "sig_lp")
    yh = y.lfilter_fir(hp, "sig_hp")

    ylw = Wave(Double, "sig_lp_wav", y.length, x)
    ylw.defn = [ yl(x) ]
    yhw = Wave(Double, "sig_hp_wav", y.length, x)
    yhw.defn = [ yh(x) ]
    ydl = ylw.downsample(2, "sig_lp_down")
    ydh = yhw.downsample(2, "sig_hp_down")

    s0 = ydl.lfilter_fir(lp, "sig_lpd_lp")
    s1 = ydl.lfilter_fir(hp, "sig_lpd_hp")
    s2 = ydh.lfilter_fir(lp, "sig_hpd_lp")
    s3 = ydh.lfilter_fir(hp, "sig_hpd_hp")

    # Decimate to get the four bands
    s0w = Wave(Double, "s0_wav", ydl.length, x)
    s0w.defn = [ s0(x) ]
    s1w = Wave(Double, "s1_wav", ydl.length, x)
    s1w.defn = [ s1(x) ]
    s2w = Wave(Double, "s2_wav", ydh.length, x)
    s2w.defn = [ s2(x) ]
    s3w = Wave(Double, "s3_wav", ydh.length, x)
    s3w.defn = [ s3(x) ]
    b0 = s0w.downsample(2, "band0")
    b1 = s1w.downsample(2, "band1")
    b2 = s2w.downsample(2, "band2")
    b3 = s3w.downsample(2, "band3")

    # Synthesize the signal
    Ss0 = b0.upsample(2, "b0_up", _out_len=s0w.length)
    Ss1 = b1.upsample(2, "b1_up", _out_len=s1w.length)
    Ss2 = b2.upsample(2, "b2_up", _out_len=s2w.length)
    Ss3 = b3.upsample(2, "b3_up", _out_len=s3w.length)

    # Reconstruction filters
    reconst_fil = lp.scalar_mul(L, "reconst_fil_low")
    reconst_filh = hp.scalar_mul(L, "reconst_fil_high")

    sb0 = Ss0.lfilter_fir(reconst_fil, "b0_up_lp")
    sb1 = Ss1.lfilter_fir(reconst_filh, "b1_up_hp")
    sb2 = Ss2.lfilter_fir(reconst_fil, "b2_up_lp")
    sb3 = Ss3.lfilter_fir(reconst_filh, "b3_up_hp")

    sb0w = Wave(Double, "b0_up_lpw", Ss0.length, x)
    sb0w.defn = [ sb0(x) ]
    sb1w = Wave(Double, "b1_up_hpw", Ss1.length, x)
    sb1w.defn = [ sb1(x) ]
    sb2w = Wave(Double, "b2_up_lpw", Ss2.length, x)
    sb2w.defn = [ sb2(x) ]
    sb3w = Wave(Double, "b3_up_hpw", Ss3.length, x)
    sb3w.defn = [ sb3(x) ]
    Slow = sb0w + sb1w
    Shigh = sb2w + sb3w

    subl = Slow.upsample(2, "subl", _out_len=N)
    subh = Shigh.upsample(2, "subh", _out_len=N)

    subll = subl.lfilter_fir(reconst_fil, "subl_lp")
    subhh = subh.lfilter_fir(reconst_filh, "subh_hp")

    subllw = Wave(Double, "subl_lpw", subl.length, x)
    subllw.defn = [ subll(x) ]
    subhhw = Wave(Double, "subh_hpw", subh.length, x)
    subhhw.defn = [ subhh(x) ]
    yf = subllw + subhhw

    return yf, b0, b1, b2, b3
