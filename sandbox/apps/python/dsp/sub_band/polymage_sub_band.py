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

    ydl = yl.downsample(2, "sig_lp_down")
    ydh = yh.downsample(2, "sig_hp_down")

    s0 = ydl.lfilter_fir(lp, "sig_lpd_lp")
    s1 = ydl.lfilter_fir(hp, "sig_lpd_hp")
    s2 = ydh.lfilter_fir(lp, "sig_hpd_lp")
    s3 = ydh.lfilter_fir(hp, "sig_hpd_hp")

    # Decimate to get the four bands
    b0 = s0.downsample(2, "band0")
    b1 = s1.downsample(2, "band1")
    b2 = s2.downsample(2, "band2")
    b3 = s3.downsample(2, "band3")

    # Synthesize the signal
    Ss0 = b0.upsample(2, "b0_up", _out_len=ydl.length)
    Ss1 = b1.upsample(2, "b1_up", _out_len=ydl.length)
    Ss2 = b2.upsample(2, "b2_up", _out_len=ydh.length)
    Ss3 = b3.upsample(2, "b3_up", _out_len=ydh.length)

    # Reconstruction filters
    reconst_fil = lp.scalar_mul(L, "reconst_fil_low")
    reconst_filh = hp.scalar_mul(L, "reconst_fil_high")

    sb0 = Ss0.lfilter_fir(reconst_fil, "b0_up_lp")
    sb1 = Ss1.lfilter_fir(reconst_filh, "b1_up_hp")
    sb2 = Ss2.lfilter_fir(reconst_fil, "b2_up_lp")
    sb3 = Ss3.lfilter_fir(reconst_filh, "b3_up_hp")

    Slow = sb0 + sb1
    Shigh = sb2 + sb3

    subl = Slow.upsample(2, "subl", _out_len=N)
    subh = Shigh.upsample(2, "subh", _out_len=N)

    subll = subl.lfilter_fir(reconst_fil, "subl_lp")
    subhh = subh.lfilter_fir(reconst_filh, "subh_hp")

    yf = subll + subhh

    return yf, b0, b1, b2, b3
