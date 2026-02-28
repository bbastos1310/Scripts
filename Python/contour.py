import nibabel as nib
import numpy as np
from skimage.segmentation import find_boundaries
import functions

# Main

## Leitura do hemisfério
with open('../Segmentation/hemisphere.txt', 'r', encoding='utf-8') as file_hemisphere:
    hemisphere = file_hemisphere.read()  
print(f"{hemisphere} hemisphere")

dict_tracks = ["ndDRTT", "dDRTT", "ML", "CST"]

if (hemisphere == 'left'):
    lesion_zone2 = nib.load("ACPC/mask_zone2_ACPC.nii.gz") 
    data_zone2 = lesion_zone2.get_fdata().astype(bool)

    contour_ndDRTT_acpc = np.zeros(data_zone2.shape, dtype=np.uint8)
    contour_dDRTT_acpc = np.zeros(data_zone2.shape, dtype=np.uint8)
    contour_CST_acpc = np.zeros(data_zone2.shape, dtype=np.uint8)
    contour_ML_acpc = np.zeros(data_zone2.shape, dtype=np.uint8)

    contour_ndDRTT_coronal = np.zeros(data_zone2.shape, dtype=np.uint8)
    contour_dDRTT_coronal = np.zeros(data_zone2.shape, dtype=np.uint8)
    contour_CST_coronal = np.zeros(data_zone2.shape, dtype=np.uint8)
    contour_ML_coronal = np.zeros(data_zone2.shape, dtype=np.uint8)
    	
    for track_number in range (len(dict_tracks)):
        track = nib.load("ACPC/track_" + dict_tracks[track_number] + "_lh_ACPC.nii.gz")
        track_core = nib.load("ACPC/track_" + dict_tracks[track_number] + "_lh_ACPC_core.nii.gz")  
        data_track = track.get_fdata()
        data_core = track_core.get_fdata().astype(bool)
        
        data_track_binary = np.zeros(data_track.shape, dtype=bool)
        slice_track = np.zeros(data_track.shape[2], dtype=np.uint8)
        slice_core = np.zeros(data_track.shape[2], dtype=np.uint8)
        
        data_track_binary[data_track > 0.01] = True
		
		#ACPC contour
        for k in range (data_track.shape[2]):
            slice_track = find_boundaries(data_track_binary[:,:,k], mode='outer', connectivity = 2) 
            slice_core = find_boundaries(data_core[:,:,k], mode='outer', connectivity = 2) 
            if track_number == 0:
                contour_ndDRTT_acpc[:,:,k][slice_track == 1] = 1
                contour_ndDRTT_acpc[:,:,k][slice_core == 1] = 2
            elif track_number == 1:
                contour_dDRTT_acpc[:,:,k][slice_track == 1] = 3
                contour_dDRTT_acpc[:,:,k][slice_core == 1] = 4
            elif track_number == 2:
                contour_ML_acpc[:,:,k][slice_track == 1] = 5
                contour_ML_acpc[:,:,k][slice_core == 1] = 6
            elif track_number == 3:
                contour_CST_acpc[:,:,k][slice_track == 1] = 7
                contour_CST_acpc[:,:,k][slice_core == 1] = 8
            else:
                pass
		
        #Coronal contour
        slice_track = np.zeros(data_track.shape[1], dtype=np.uint8)
        slice_core = np.zeros(data_track.shape[1], dtype=np.uint8)
		
        for j in range (data_track.shape[1]):
            slice_track = find_boundaries(data_track_binary[:,j,:], mode='outer', connectivity = 2) 
            slice_core = find_boundaries(data_core[:,j,:], mode='outer', connectivity = 2) 
            if track_number == 0:
                contour_ndDRTT_coronal[:,j,:][slice_track == 1] = 1
                contour_ndDRTT_coronal[:,j,:][slice_core == 1] = 2
            elif track_number == 1:
                contour_dDRTT_coronal[:,j,:][slice_track == 1] = 3
                contour_dDRTT_coronal[:,j,:][slice_core == 1] = 4
            elif track_number == 2:
                contour_ML_coronal[:,j,:][slice_track == 1] = 5
                contour_ML_coronal[:,j,:][slice_core == 1] = 6
            elif track_number == 3:
                contour_CST_coronal[:,j,:][slice_track == 1] = 7
                contour_CST_coronal[:,j,:][slice_core == 1] = 8
            else:
                pass
        print(f"Track {track_number + 1} completed") 
        del track_core, data_track, data_core
    
    functions.saveImage(contour_ndDRTT_acpc.astype(np.uint8), track, "Contour/contour_ndDRTT_lh_acpc")
    functions.saveImage(contour_ndDRTT_coronal.astype(np.uint8), track, "Contour/contour_ndDRTT_lh_coronal")
    functions.saveImage(contour_dDRTT_acpc.astype(np.uint8), track, "Contour/contour_dDRTT_lh_acpc")
    functions.saveImage(contour_dDRTT_coronal.astype(np.uint8), track, "Contour/contour_dDRTT_lh_coronal")
    functions.saveImage(contour_ML_acpc.astype(np.uint8), track, "Contour/contour_ML_lh_acpc")
    functions.saveImage(contour_ML_coronal.astype(np.uint8), track, "Contour/contour_ML_lh_coronal")
    functions.saveImage(contour_CST_acpc.astype(np.uint8), track, "Contour/contour_CST_lh_acpc")
    functions.saveImage(contour_CST_coronal.astype(np.uint8), track, "Contour/contour_CST_lh_coronal")
		
if (hemisphere == 'right'):
    lesion_zone2 = nib.load("ACPC/mask_zone2_ACPC.nii.gz") 
    data_zone2 = lesion_zone2.get_fdata().astype(bool)

    contour_ndDRTT_acpc = np.zeros(data_zone2.shape, dtype=np.uint8)
    contour_dDRTT_acpc = np.zeros(data_zone2.shape, dtype=np.uint8)
    contour_CST_acpc = np.zeros(data_zone2.shape, dtype=np.uint8)
    contour_ML_acpc = np.zeros(data_zone2.shape, dtype=np.uint8)

    contour_ndDRTT_coronal = np.zeros(data_zone2.shape, dtype=np.uint8)
    contour_dDRTT_coronal = np.zeros(data_zone2.shape, dtype=np.uint8)
    contour_CST_coronal = np.zeros(data_zone2.shape, dtype=np.uint8)
    contour_ML_coronal = np.zeros(data_zone2.shape, dtype=np.uint8)
    	
    for track_number in range (len(dict_tracks)):
        track = nib.load("ACPC/track_" + dict_tracks[track_number] + "_rh_ACPC.nii.gz")
        track_core = nib.load("ACPC/track_" + dict_tracks[track_number] + "_rh_ACPC_core.nii.gz")  
        data_track = track.get_fdata()
        data_core = track_core.get_fdata().astype(bool)
        
        data_track_binary = np.zeros(data_track.shape, dtype=bool)
        slice_track = np.zeros(data_track.shape[2], dtype=np.uint8)
        slice_core = np.zeros(data_track.shape[2], dtype=np.uint8)
        
        data_track_binary[data_track > 0.01] = True
		
		#ACPC contour
        for k in range (data_track.shape[2]):
            slice_track = find_boundaries(data_track_binary[:,:,k], mode='outer', connectivity = 2) 
            slice_core = find_boundaries(data_core[:,:,k], mode='outer', connectivity = 2) 
            if track_number == 0:
                contour_ndDRTT_acpc[:,:,k][slice_track == 1] = 1
                contour_ndDRTT_acpc[:,:,k][slice_core == 1] = 2
            elif track_number == 1:
                contour_dDRTT_acpc[:,:,k][slice_track == 1] = 3
                contour_dDRTT_acpc[:,:,k][slice_core == 1] = 4
            elif track_number == 2:
                contour_ML_acpc[:,:,k][slice_track == 1] = 5
                contour_ML_acpc[:,:,k][slice_core == 1] = 6
            elif track_number == 3:
                contour_CST_acpc[:,:,k][slice_track == 1] = 7
                contour_CST_acpc[:,:,k][slice_core == 1] = 8
            else:
                pass
		
        #Coronal contour
        slice_track = np.zeros(data_track.shape[1], dtype=np.uint8)
        slice_core = np.zeros(data_track.shape[1], dtype=np.uint8)
		
        for j in range (data_track.shape[1]):
            slice_track = find_boundaries(data_track_binary[:,j,:], mode='outer', connectivity = 2) 
            slice_core = find_boundaries(data_core[:,j,:], mode='outer', connectivity = 2) 
            if track_number == 0:
                contour_ndDRTT_coronal[:,j,:][slice_track == 1] = 1
                contour_ndDRTT_coronal[:,j,:][slice_core == 1] = 2
            elif track_number == 1:
                contour_dDRTT_coronal[:,j,:][slice_track == 1] = 3
                contour_dDRTT_coronal[:,j,:][slice_core == 1] = 4
            elif track_number == 2:
                contour_ML_coronal[:,j,:][slice_track == 1] = 5
                contour_ML_coronal[:,j,:][slice_core == 1] = 6
            elif track_number == 3:
                contour_CST_coronal[:,j,:][slice_track == 1] = 7
                contour_CST_coronal[:,j,:][slice_core == 1] = 8
            else:
                pass
        print(f"Track {track_number + 1} completed") 
        del track_core, data_track, data_core
    
    functions.saveImage(contour_ndDRTT_acpc.astype(np.uint8), track, "Contour/contour_ndDRTT_rh_acpc")
    functions.saveImage(contour_ndDRTT_coronal.astype(np.uint8), track, "Contour/contour_ndDRTT_rh_coronal")
    functions.saveImage(contour_dDRTT_acpc.astype(np.uint8), track, "Contour/contour_dDRTT_rh_acpc")
    functions.saveImage(contour_dDRTT_coronal.astype(np.uint8), track, "Contour/contour_dDRTT_rh_coronal")
    functions.saveImage(contour_ML_acpc.astype(np.uint8), track, "Contour/contour_ML_rh_acpc")
    functions.saveImage(contour_ML_coronal.astype(np.uint8), track, "Contour/contour_ML_rh_coronal")
    functions.saveImage(contour_CST_acpc.astype(np.uint8), track, "Contour/contour_CST_rh_acpc")
    functions.saveImage(contour_CST_coronal.astype(np.uint8), track, "Contour/contour_CST_rh_coronal")	           
        								
