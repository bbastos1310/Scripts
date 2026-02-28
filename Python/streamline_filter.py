# Local libraries
import functions

# External libraries
import numpy as np
import nibabel as nib
from scipy.ndimage import gaussian_filter

def handleNorm(data_track):
	data_track_norm = np.zeros(data_track.shape)
	data_track_binary = np.zeros(data_track.shape).astype(bool)
	mask_connected = np.zeros(data_track.shape)
	
	max_value = np.max(data_track)
	min_value = np.min(data_track)
	data_track_norm[data_track != 0] = data_track[data_track != 0]/(max_value - min_value)
	# data_track_binary[data_track_norm > 0] = 1
	# mask_connected = functions.connectedComponents(data_track_binary)
	# data_track_norm[mask_connected != True] = 0
	return data_track_norm
	
def handleInnerlimit(data_track_norm, image, track, hemisphere):
	data_track_in = np.zeros(data_track_norm.shape)

	if (hemisphere == 'left'):
		hem = 'lh'
	elif (hemisphere == 'right'):
		hem = 'rh'
	else:
		print("hemisphere must be left or right")
			
	# mean = np.mean(data_track_norm[data_track_norm != 0])
	# std = np.std(data_track_norm[data_track_norm != 0])
	# print(f"mean = {mean}, std = {std}")
	# data_track_in[data_track_norm > (mean + 2 * std)] = 1
			
	data_track_in[data_track_norm > 0.1] = 1
	functions.saveImage(functions.connectedComponents(data_track_in).astype(np.uint8), image, "track_" + track + "_" + hem + "_core")
	
	

# Main
## Leitura do hemisfério
with open('../Segmentation/hemisphere.txt', 'r', encoding='utf-8') as file_hemisphere:
    hemisphere = file_hemisphere.read()  
print(f"{hemisphere} hemisphere")

dict_tracks = ["ndDRTT", "dDRTT", "ML", "CST"]

if (hemisphere == 'left'):
	for track in range (len(dict_tracks)):
		img = nib.load("track_" + dict_tracks[track] + "_lh_weighted.nii.gz")
		data = img.get_fdata()
		print("Data " + "track_" + dict_tracks[track] + "_lh_weighted.nii.gz loaded")
		
		data_norm = handleNorm(gaussian_filter(data, sigma = 0.5))
		functions.saveImage(data_norm.astype(np.float32), img, "track_" + dict_tracks[track] + "_lh_smoothed")
		handleInnerlimit(gaussian_filter(data_norm, sigma = 0.5), img, dict_tracks[track], hemisphere)
		del data, img
	

elif (hemisphere == 'right'):
	for track in range (len(dict_tracks)):
		img = nib.load("track_" + dict_tracks[track] + "_rh_weighted.nii.gz")
		data = img.get_fdata()
		print("Data" + "track_" + dict_tracks[track] + "_rh_weighted.nii.gz loaded")
		
		data_norm = handleNorm(gaussian_filter(data, sigma = 0.5))
		functions.saveImage(data_norm.astype(np.float32), img, "track_" + dict_tracks[track] + "_rh_smoothed")
		handleInnerlimit(gaussian_filter(data_norm, sigma = 0.5), img, dict_tracks[track], hemisphere)
		del data, img
