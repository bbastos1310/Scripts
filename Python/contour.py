import nibabel as nib
import matplotlib.pyplot as plt
import numpy as np
import os
from joblib import Parallel, delayed
from scipy.ndimage import gaussian_filter, binary_fill_holes
from skimage import measure
from skimage.morphology import binary_closing
from skimage.segmentation import find_boundaries
import functions

def handleAxialcontour (im_ref, hemisphere, plan, data_lesion, data_ndDRTT, data_DRTT, data_CST, data_ML):
	# Função que cria os contornos dos tratos 
	contour_lesion = np.zeros(data_lesion.shape, dtype=np.uint8)
	contour_mask_ndDRTT = np.zeros(data_lesion.shape, dtype=np.uint8)
	contour_mask_DRTT = np.zeros(data_lesion.shape, dtype=np.uint8)
	contour_mask_CST = np.zeros(data_lesion.shape, dtype=np.uint8)
	contour_mask_ML = np.zeros(data_lesion.shape, dtype=np.uint8)	
			
	if (hemisphere == 'left'):
		hem = 'lh'
	elif (hemisphere == 'right'):
		hem = 'rh'
	else:
		print("hemisphere must be left or right")
	
	for k in range (data_lesion.shape[2]):
		slice_2d = data_lesion[:, :, k]
		contour_lesion[:,:,k] = find_boundaries(slice_2d, mode='outer', connectivity = 2) 
		contour_mask_ndDRTT[:,:,k] = find_boundaries(data_ndDRTT[:,:,k], mode='outer', connectivity = 2) * 2
		contour_mask_DRTT[:,:,k] = find_boundaries(data_DRTT[:,:,k], mode='outer', connectivity = 2) * 3
		contour_mask_CST[:,:,k] = find_boundaries(data_CST[:,:,k], mode='outer', connectivity = 2) * 4
		contour_mask_ML[:,:,k] = find_boundaries(data_ML[:,:,k], mode='outer', connectivity = 2) * 5
			
	if (plan == 'axial'):
		nifti_contour = nib.Nifti1Image(contour_lesion, im_ref.affine)
		nib.save(nifti_contour, "Contour/axial_contour_lesion.nii.gz")
		
		nifti_contour = nib.Nifti1Image(contour_mask_ndDRTT, im_ref.affine)
		nib.save(nifti_contour, "Contour/axial_contour_ndDRTT.nii.gz")

		nifti_contour = nib.Nifti1Image(contour_mask_DRTT, im_ref.affine)
		nib.save(nifti_contour, "Contour/axial_contour_dDRTT.nii.gz")

		nifti_contour = nib.Nifti1Image(contour_mask_CST, im_ref.affine)
		nib.save(nifti_contour, "Contour/axial_contour_CST.nii.gz")

		nifti_contour = nib.Nifti1Image(contour_mask_ML, im_ref.affine)
		nib.save(nifti_contour, "Contour/axial_contour_ML.nii.gz")
	
	elif (plan == 'acpc'):
		nifti_contour = nib.Nifti1Image(contour_lesion, im_ref.affine)
		nib.save(nifti_contour, "Contour/acpc_contour_lesion.nii.gz")
		
		nifti_contour = nib.Nifti1Image(contour_mask_ndDRTT, im_ref.affine)
		nib.save(nifti_contour, "Contour/acpc_contour_ndDRTT.nii.gz")

		nifti_contour = nib.Nifti1Image(contour_mask_DRTT, im_ref.affine)
		nib.save(nifti_contour, "Contour/acpc_contour_dDRTT.nii.gz")

		nifti_contour = nib.Nifti1Image(contour_mask_CST, im_ref.affine)
		nib.save(nifti_contour, "Contour/acpc_contour_CST.nii.gz")

		nifti_contour = nib.Nifti1Image(contour_mask_ML, im_ref.affine)
		nib.save(nifti_contour, "Contour/acpc_contour_ML.nii.gz")
	print("images saved")
	
def handleCoronalcontour (im_ref, hemisphere, data_lesion, data_ndDRTT, data_DRTT, data_CST, data_ML):
	# Função que cria os contornos dos tratos 
	contour_lesion = np.zeros(data_lesion.shape, dtype=np.uint8)
	contour_mask_ndDRTT = np.zeros(data_lesion.shape, dtype=np.uint8)
	contour_mask_DRTT = np.zeros(data_lesion.shape, dtype=np.uint8)
	contour_mask_CST = np.zeros(data_lesion.shape, dtype=np.uint8)
	contour_mask_ML = np.zeros(data_lesion.shape, dtype=np.uint8)
				
	if (hemisphere == 'left'):
		hem = 'lh'
	elif (hemisphere == 'right'):
		hem = 'rh'
	else:
		print("hemisphere must be left or right")
	
		
	for j in range (data_lesion.shape[1]):	
		slice_2d = data_lesion[:, j, :]
		contour_lesion[:,j,:] = find_boundaries(slice_2d, mode='outer', connectivity = 2) 
		contour_mask_ndDRTT[:,j,:] = find_boundaries(data_ndDRTT[:,j,:], mode='outer', connectivity = 2) * 2
		contour_mask_DRTT[:,j,:] = find_boundaries(data_DRTT[:,j,:], mode='outer', connectivity = 2) * 3
		contour_mask_CST[:,j,:] = find_boundaries(data_CST[:,j,:], mode='outer', connectivity = 2) * 4
		contour_mask_ML[:,j,:] = find_boundaries(data_ML[:,j,:], mode='outer', connectivity = 2) * 5
	
	nifti_contour = nib.Nifti1Image(contour_lesion, im_ref.affine)
	nib.save(nifti_contour, "Contour/coronal_contour_lesion.nii.gz")
	
	nifti_contour = nib.Nifti1Image(contour_mask_ndDRTT, im_ref.affine)
	nib.save(nifti_contour, "Contour/coronal_contour_ndDRTT.nii.gz")
	
	nifti_contour = nib.Nifti1Image(contour_mask_DRTT, im_ref.affine)
	nib.save(nifti_contour, "Contour/coronal_contour_dDRTT.nii.gz")
	
	nifti_contour = nib.Nifti1Image(contour_mask_CST, im_ref.affine)
	nib.save(nifti_contour, "Contour/coronal_contour_CST.nii.gz")
	
	nifti_contour = nib.Nifti1Image(contour_mask_ML, im_ref.affine)
	nib.save(nifti_contour, "Contour/coronal_contour_ML.nii.gz")
	
# Main

## Leitura do hemisfério
with open('../Segmentation/hemisphere.txt', 'r', encoding='utf-8') as file_hemisphere:
    hemisphere = file_hemisphere.read()  
print(f"{hemisphere} hemisphere")

## Load files

if (hemisphere == 'left'):
	lesion_ACPC = nib.load("ACPC/mask_zone2_ACPC.nii.gz") 
	track_ndDRTT_ACPC = nib.load("ACPC/track_ndDRTT_lh_ACPC.nii.gz") 
	track_DRTT_ACPC = nib.load("ACPC/track_dDRTT_lh_ACPC.nii.gz") 
	track_CST_ACPC = nib.load("ACPC/track_CST_lh_ACPC.nii.gz") 
	track_ML_ACPC = nib.load("ACPC/track_ML_lh_ACPC.nii.gz") 

elif (hemisphere == 'right'):
	lesion_ACPC = nib.load("ACPC/mask_zone2_ACPC.nii.gz")
	track_ndDRTT_ACPC = nib.load("ACPC/track_ndDRTT_rh_ACPC.nii.gz") 
	track_DRTT_ACPC = nib.load("ACPC/track_dDRTT_rh_ACPC.nii.gz") 
	track_CST_ACPC = nib.load("ACPC/track_CST_rh_ACPC.nii.gz") 
	track_ML_ACPC = nib.load("ACPC/track_ML_rh_ACPC.nii.gz") 

print(".Files loaded (ACPC)")

## Extract data from image
mask_lesion_ACPC = lesion_ACPC.get_fdata().astype(np.uint8) 
data_ndDRTT_ACPC = track_ndDRTT_ACPC.get_fdata().astype(np.uint8) 
data_DRTT_ACPC = track_DRTT_ACPC.get_fdata().astype(np.uint8) 
data_CST_ACPC = track_CST_ACPC.get_fdata().astype(np.uint8) 
data_ML_ACPC = track_ML_ACPC.get_fdata().astype(np.uint8) 

del track_ndDRTT_ACPC, track_DRTT_ACPC, track_CST_ACPC, track_ML_ACPC

print(".Data loaded(ACPC)")

handleAxialcontour(lesion_ACPC, hemisphere, "acpc", mask_lesion_ACPC, data_ndDRTT_ACPC, data_DRTT_ACPC, data_CST_ACPC, data_ML_ACPC)
handleCoronalcontour(lesion_ACPC, hemisphere, mask_lesion_ACPC, data_ndDRTT_ACPC, data_DRTT_ACPC, data_CST_ACPC, data_ML_ACPC)
