import numpy as np

def refine_kpt(dogPyr, nOCT, nDoGLayers, kpt):
	

	return true

def	compute_ort_hist()

# Main Post Processing Function 
def post_processing(app_data):

	#Aquiring Pipe and App Data
	pipe_data = app_data['pipe_data']
	nOCT = pipe_data['nOCT']
	nLayers  = pipe_data['nLayers']
	nGLayers = pipe_data['nGLayers'] 
	gPyr = pipe_data['gPyr']
	nDoGLayers  = pipe_data['nDoGLayers']
	dogPyr = pipe_data['dogPyr']
	nBins = app_data['nBins']
	SIFT_CONTR_THR = app_data['SIFT_CONTR_THR']
	SIFT_ORI_PEAK_RATIO = app_data['SIFT_ORI_PEAK_RATIO']
	nBins = app_data['SIFT_ORI_HIST_BINS']
	hist = [none]*nBins


	# Initializations
	grdPyr = [None]*nOCT*nLayers
	ortPyr = [None]*nOCT*nLayers


	#################################################################################
	#																				#
	#					Creating the Gradient and Orientation Pyramids				#
	#																				#
	#################################################################################

	for i in range(0, nOCT): 

		OCT_layerindex = i*nLayers
		[w, h] = gPyr[OCT_layerindex].shape

		#Cycle through all the layers
		for j in range(1, nLayers): 

			layerindex = i*nGLayers + j; 

			# Initializations for Optimization 

			grdPyr[layerindex] = np.zeros((w, h))
			ortPyr[layerindex] = np.zeros((w, h))

			current_grdImg = np.zeros((w, h))
			current_ortImg = np.zeros((w, h))

			for r in range (0, h)

				for c in range(0, w)

					currentImg = gPyr[layerindex]
					dr = currentImg[r+1, c] - currentImg[r-1, c]
					dc = currentImg[r, c+1] - currentImg[r, c-1]

					current_grdImg[r, c] = np.sqrt(dr * dr + dc * dc)
					current_ortImg[r, c] = np.arctan2(dr, dc)

			grdPyr[layerindex] = current_grdImg
			ortPyr[layerindex] = current_ortImg

	#################################################################################

	#################################################################################
	#																				#
	#							  Detecting Keypoints								#
	#																				#
	#################################################################################

	float contr_thr = (float)0.8 * SIFT_CONTR_THR

	for i in range(0, nOCT):

		OCT_layerindex = i*nLayers
		[w, h] = gPyr(OCT_layerindex).shape

			#Cycle through all the layers
			for j in range(1, nDoGLayers): 

				layerindex = i*nDoGLayers + j; 
				
				high_dogImg = dogPyr[layerindex+1]
				current_dogImg = dogPyr[layerindex]
				low_dogImg = dogPyr[layerindex-1]

				for r in range(0, h)

					for c in range(0, w)

						val = current_dogImg[r, c]

						bool bExtrema = 
						###### Greater Data ##########
						( val >= contr_thr &&
						# High Data
						val > high_dogImg[r-1, c-1] && 
						val > high_dogImg[r-1, c] &&
						val > high_dogImg[r-1, c+1] &&
						val > high_dogImg[r, c-1] &&
						val > high_dogImg[r, c] &&
						val > high_dogImg[r, c+1] &&
						val > high_dogImg[r+1, c-1] &&
						val > high_dogImg[r+1, c] &&
						val > high_dogImg[r+1, c+1] &&
						# Current Data
						val > current_dogImg[r-1, c-1] &&
						val > current_dogImg[r-1, c] &&
						val > current_dogImg[r-1, c+1] &&
						val > current_dogImg[r, c-1] &&
						val > current_dogImg[r, c] &&
						val > current_dogImg[r, c+1] &&
						val > current_dogImg[r+1, c-1] &&
						val > current_dogImg[r+1, c] &&
						val > current_dogImg[r+1, c+1] &&
						#Low Data
						val > low_dogImg[r-1, c-1] &&
						val > low_dogImg[r-1, c] &&
						val > low_dogImg[r-1, c+1] &&
						val > low_dogImg[r, c-1] &&
						val > low_dogImg[r, c] &&
						val > low_dogImg[r, c+1] &&
						val > low_dogImg[r+1, c-1] &&
						val > low_dogImg[r+1, c] &&
						val > low_dogImg[r+1, c+1] && ) ||
						###### Lesser Data ##########
						( val <= -contr_thr &&
						# High Data
						val < high_dogImg[r-1, c-1] && 
						val < high_dogImg[r-1, c] &&
						val < high_dogImg[r-1, c+1] &&
						val < high_dogImg[r, c-1] &&
						val < high_dogImg[r, c] &&
						val < high_dogImg[r, c+1] &&
						val < high_dogImg[r+1, c-1] &&
						val < high_dogImg[r+1, c] &&
						val < high_dogImg[r+1, c+1] &&
						# Current Data
						val < current_dogImg[r-1, c-1] &&
						val < current_dogImg[r-1, c] &&
						val < current_dogImg[r-1, c+1] &&
						val < current_dogImg[r, c-1] &&
						val < current_dogImg[r, c] &&
						val < current_dogImg[r, c+1] &&
						val < current_dogImg[r+1, c-1] &&
						val < current_dogImg[r+1, c] &&
						val < current_dogImg[r+1, c+1] &&
						#Low Data
						val < low_dogImg[r-1, c-1] &&
						val < low_dogImg[r-1, c] &&
						val < low_dogImg[r-1, c+1] &&
						val < low_dogImg[r, c-1] &&
						val < low_dogImg[r, c] &&
						val < low_dogImg[r, c+1] &&
						val < low_dogImg[r+1, c-1] &&
						val < low_dogImg[r+1, c] &&
						val < low_dogImg[r+1, c+1] && )

						if bExtrema: 

							current_kpt = Kpt(i, j, r, c)
							bool goodbExtrema = refine_kpt(dogPyr, nOCT, nDoGLayers, current_kpt)

							if goodbExtrema:
								max_grdP = grdPyr[i * nGpyrLayersv + current_kpt.layer]
								max_ortP = ortPyr[i * nGpyrLayersv + current_kpt.layer]

								float maxmag = compute_ort_hist( max_grdP, max_ortP, current_kpt, hist) 
								float threshold = max_mag * SIFT_ORI_PEAK_RATIO;

								for ii in range(0:nBins):
									if hist[ii] > threshold




						




	#################################################################################

	return kpt_list





