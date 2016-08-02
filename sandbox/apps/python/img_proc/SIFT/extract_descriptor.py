import numpy as np
import math 

# I am assuming the images will be numpy arrays 
def extract_descriptor(app_data, kpt_list, grd_data, ort_data): 

	# User defined numbers from init.py
	nGLayers = app_data['nGLayers']
	SIFT_D_SCL_FCTR = app_data['SIFT_D_SCL_FCTR']
	nSubregion = app_data['SIFT_DESCR_WIDTH']
	nBinsPerSubregion = app_data['SIFT_D_HIST_BINS']
	SIFT_D_MAG_THR = app_data['SIFT_D_MAG_THR']

	# Global Variables 
	nHalfSubregion = nSubregion >> 1
	double_pi = float(6.283185307179586)
	SQRT2 = float(1.414213562373095) 
	nBinsPerSubregionPerDegree = float(nBinsPerSubregion/double_pi)

	# Circular Bin Creation Variables
	nBins = int(nSubregion * nSubregion * nBinsPerSubregion)
	nHistBins = (nSubregion + 2) * (nSubregion + 2) \
					* (nBinsPerSubregion + 2)
	nSliceStep = (nSubregion + 2) * (nBinsPerSubregion + 2)
	nRowStep = (nBinsPerSubregion + 2)

	descp_list = {}

	for kpt in kpt_list: 

		# Create a new array of bins for every new keypoint
		# Garbage Collecter will optimize the creation and 
		# deletion of these arrays
		# Note: Default type of numpy array is float 
		HistBin = np.zeros(nHistBins)

		octave = kpt.octave
		layer = kpt.layer
		# You do not obtain the SIFT gradient here
		# Only from the gradient pyramids 
		ori = kpt.ort
		ri = kpt.x_ri
		ci = kpt.x_ci
		scale = kpt.layer_scale

		kptr_i = int(ri + 0.5)
		kptc_i = int(ci + 0.5)
		d_kptr = kptr_i - ri
		d_kptc = kptc_i - ci

		layer_index = octave * nGLayers * layer]
		current_grd = grd_data[layer_index]
		current_ort = ort_data[layer_index]
		image_size = current_grd.shape()
		w = image_size(1)
		h = image_size(2)
		subregion_width = SIFT_D_SCL_FCTR * scale 
		win_size = int(SQRT2 * subregion_width * (nSubregion + 1) \
						* 0.5 + 0.5) 

		sin_t = math.sin(ori)/float(subregion_width)
		cos_t = math.cos(ori)/float(subregion_width)

		left = int(math.max(-win_size, 1 - kptc_i))
		right = int(math.min(win_size, w - 2 - kptc_i))
		top = int(math.max(-win_size, 1 - kptr_i))
		bottom = int(math.min(win_size, h - 2 - kptr_i))

		# Going over the rows 
		for i in range(top, bottom+1):
			# Going over the columns 
			for j in range(left, right+1): 

				# Accurate positions relative to 
				rr = i + d_kptc
				cc = j + d_kptc

				# Rotating Coordinate (i, j)
				rrotate = cos_t * cc + sin_t * rr
				crotate = -sin_t * cc + cos_t * rr

				rbin = rrotate + nHalfSubregion - float(0.5)
				cbin = crotate + nHalfSubregion - float(0.5)

				# If Pixel is outside the bin range then it is 
				# counted 
				if (rbin <= -1 || rbin >= nSubregion || cbin <= -1 \
						|| cbin >= nSubregion) :
					continue

				r = kptr_i + i
				c = kptc_i + j
				mag = grdData[r, c]
				angle = rotData[r, c] - ori
				angle1 = double_pi + angle if angle < 0 else angle
				obin = angle1 * nBinsPerSubregionPerDegree

				y0 = int(math.floor(rbin)) 
				x0 = int(math.floor(cbin)) 
				z0 = int(math.floor(obin)) 
				d_rbin = rbin - y0
				d_cbin = cbin - x0
				d_obin = obin - z0
				x1 = x0 + 1
				y1 = y0 + 1
				z1 = z0 + 1

				# Gaussian weight relative to the center of sample region
				g_weight = math.expf((rrotate * rrotate + crotate * \
												crotate) * exp_scale)

				# Gaussian magnitude
				gm = float(mag * g_weight);
				
				# Trilinear Interpolation 
				# Explicit Float casts placed all along here 
				vr1 = float(gm * d_rbin)
				vr0 = float(gm - vr1)
				vrc11 = float(vr1   * d_cbin)
				vrc10 = float(vr1   - vrc11)
				vrc01 = float(vr0   * d_cbin)
				vrc00 = float(vr0   - vrc01)
				vrco111 = float(vrc11 * d_obin)
				vrco110 = float(vrc11 - vrco111)
				vrco101 = float(vrc10 * d_obin)
				vrco100 = float(vrc10 - vrco101)
				vrco011 = float(vrc01 * d_obin)
				vrco010 = float(vrc01 - vrco011)
				vrco001 = float(vrc00 * d_obin)
				vrco000 = float(vrc00 - vrco001)

				# Placing data into the bins 
				idx = y1  * nSliceStep + x1 * nRowStep + z0
				histBin[idx] = histBin[idx] + vrco000
				idx = idx + 1
				histBin[idx] = histBin[idx] + vrco001
				idx = idx + nRowStep - 1
				histBin[idx] = histBin[idx] + vrco010
				idx = idx + 1 
				histBin[idx] = histBin[idx] + vrco011
				idx = idx + nSliceStep - nRowStep - 1
				histBin[idx] = histBin[idx] + vrco100
				idx = idx + 1 
				histBin[idx] = histBin[idx] + vrco101
				idx =  idx + nRowStep - 1
				histBin[idx] = histBin[idx] + vrco110
				idx = idx + 1 
				histBin[idx] = histBin[idx] + vrco111

		# Retrieve edges for orientation bins 
		dstBins = np.zeros(nBins)

		# For the slices 
		for i in range(1, nSubregion+1) :
			# For the rows 
			for j in range(1, nSubregion+1): 

				idx = i * nSliceStep + j * nRowStep
				histBin[idx] = histBin[idx + nBinsPerSubregion]

				if idx != 0 : 
					histBin[idx + nBinsPerSubregion + 1] = histBin[idx - 1]

				idx1 = ((i-1) *nSubregion + j-1)* nBinsPerSubregion

				for k in range(0, nBinsPerSubregion) : 					
					dstBins[idx1 + k] = histBin[idx + k]

		# Normalize the Histogram 
		sum_square = float(0.0)
		for i in range(0, nBins): 
			sum_square += dstBins[i] * dstBins[i]

		# No fast square root function available
		# At least to my knowledge as of now within polymage 
		# or Python 
		thr = float(math.sqrt(sum_square) * SIFT_D_MAG_THR)

		tmp = float(0.0)
		sum_square = float(0.0)

		# Filter all number bigger than 0.2 after normalization 
		for i in range(0, nBins) : 
			tmp = math.min(thr, dstBins[i])
			dstBins[i] = tmp 
			sum_square = sum_square + tmp * tmp

		# Re-normalize
		norm_factor = SIFT_INT_D_FCTR/math.sqrt(sum_square)

		for i in range(0, nBins) :
			dstBins[i] = dstBins[i] * norm_factor

		# Option that can be explored 
		# kpt.descp = dstBins	

		descp_list.append(dstBins)

	return descp_list









