from __init__ import *

import sys
import os.path
import math as mth
from utils import *

def coeff_calc(app_data, nGLayers) :

	sigma0 = float(1.6)
	nLayers = nGLayers - 3
	k_denom = (float(1.0))/ nLayers
	k = mth.pow(float(2.0),k_denom)

	sigma_pre = float(1.0)
	sigz = {}
	sigz[0] = mth.sqrt((sigma0*sigma0) - (sigma_pre*sigma_pre))

	for l in range(1, nGLayers):
		sigma_pre = mth.pow(k, (float(l-1)*sigma0))
		sigma_pre = float(sigma_pre)
		sigma = sigma_pre* k
		sigz[l] = mth.sqrt((sigma*sigma) - (sigma_pre*sigma_pre))

	gCoeff = [None]*nGLayers

	for l in range(0, nGLayers): 
		factor = float(3.0)
		if (sigz[l]*factor) > float(1.0):
			gR = int(mth.ceil(sigz[l]*factor))
		else : 
			gR = 1

		gW = gR * 2 + 1
		accu = float(0.0)
		tmpCoeff = [None]*gW

		for j in range(0, gW):
			tmp = float((j-gR)/sigz[l])
			tmpCoeff[j] = mth.exp(tmp * tmp - float(0.5)) * (1 + j/float(1000.0))
			accu = accu+tmpCoeff[j]

		for j in range(0, gW) :
			tmpCoeff[j] = tmpCoeff[j]/accu

		gCoeff[l] = tmpCoeff


	app_data['gCoeff'] = gCoeff