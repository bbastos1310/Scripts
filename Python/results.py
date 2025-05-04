import nibabel as nib
import matplotlib.pyplot as plt
import numpy as np
from skimage import measure
from skimage import measure

import functions

def handleRelativeintersection (data_reference, data_compare):
	# Função para quantizar a interseção do parâmetro analisado com a lesão, leva em consideração a intensidade da lesão em cada voxel ("Análogo a uma média ponderada")
	
	data_intersection = np.zeros(data_reference.shape, dtype=np.float16)
	mask_intersection = ((data_reference != 0) & (data_compare != 0)).astype(bool)
	data_intersection[mask_intersection] = data_reference[mask_intersection] * data_compare[mask_intersection] # Multiplicação dos valores nos voxels em que ocorre interseção
	print(f"inter_sum:{data_intersection.sum()}, ref_sum:{data_reference.sum()}")
	rel_intersection = data_intersection.sum()/data_reference.sum() 
	return rel_intersection
	
def handleAxialcontour (im_ref, hemisphere, data_lesion, data_ndDRTT, data_DRTT, data_CST, data_ML):
	# Função que cria os contornos dos tratos 
	contour_mask = np.zeros(data_lesion.shape, dtype=np.uint8)		
			
	if (hemisphere == 'left'):
		hem = 'lh'
	elif (hemisphere == 'right'):
		hem = 'rh'
	else:
		print("hemisphere must be left or right")
	
	for k in range (data_lesion.shape[2]):
		slice_2d = data_lesion[:, :, k]
		
		contours_lesion = measure.find_contours(data_lesion[:,:,k], level=0.3)	
		for contour in contours_lesion:
			rr, cc = np.round(contour).astype(int).T
			valid = (rr >= 0) & (rr < slice_2d.shape[0]) & (cc >= 0) & (cc < slice_2d.shape[1])
			contour_mask[rr[valid], cc[valid], k] = 1  
		
		contours_ndDRTT = measure.find_contours(data_ndDRTT[:,:,k], level=0.5)	
		for contour in contours_ndDRTT:
			rr, cc = np.round(contour).astype(int).T
			valid = (rr >= 0) & (rr < slice_2d.shape[0]) & (cc >= 0) & (cc < slice_2d.shape[1])
			contour_mask[rr[valid], cc[valid], k] = 2
		
		contours_DRTT = measure.find_contours(data_DRTT[:,:,k], level=0.5)	
		for contour in contours_DRTT:
			rr, cc = np.round(contour).astype(int).T
			valid = (rr >= 0) & (rr < slice_2d.shape[0]) & (cc >= 0) & (cc < slice_2d.shape[1])
			contour_mask[rr[valid], cc[valid], k] = 3 
			
		contours_CST = measure.find_contours(data_CST[:,:,k], level=0.5)	
		for contour in contours_CST:
			rr, cc = np.round(contour).astype(int).T
			valid = (rr >= 0) & (rr < slice_2d.shape[0]) & (cc >= 0) & (cc < slice_2d.shape[1])
			contour_mask[rr[valid], cc[valid], k] = 4  
		
		contours_ML = measure.find_contours(data_ML[:,:,k], level=0.5)	
		for contour in contours_ML:
			rr, cc = np.round(contour).astype(int).T
			valid = (rr >= 0) & (rr < slice_2d.shape[0]) & (cc >= 0) & (cc < slice_2d.shape[1])
			contour_mask[rr[valid], cc[valid], k] = 5
	
	nifti_contour = nib.Nifti1Image(contour_mask, im_ref.affine)
	nib.save(nifti_contour, "axial_contour.nii.gz")
	print("Image axial_contour.nii.gz saved")
	
def handleCoronalcontour (im_ref, hemisphere, data_lesion, data_ndDRTT, data_DRTT, data_CST, data_ML):
	# Função que cria os contornos dos tratos 
	contour_mask = np.zeros((640,640,640,5), dtype=np.uint8)
				
	if (hemisphere == 'left'):
		hem = 'lh'
	elif (hemisphere == 'right'):
		hem = 'rh'
	else:
		print("hemisphere must be left or right")
	
	# #Lesion
	# for j in range (data_lesion.shape[1]):
		# mask_lesion[:, j, :] = functions.contourSlice(data_lesion[:, j, :])
	# contour_mask[mask_lesion] = 1
	
	for j in range (data_lesion.shape[1]):	
		slice_2d = data_lesion[:, j, :]
		
		contours_lesion = measure.find_contours(data_lesion[:, j, :], level=0.3)	
		for contour in contours_lesion:
			rr, cc = np.round(contour).astype(int).T
			valid = (rr >= 0) & (rr < slice_2d.shape[0]) & (cc >= 0) & (cc < slice_2d.shape[1])
			contour_mask[rr[valid], j, cc[valid], 4] = 1  
		
		contours_ndDRTT = measure.find_contours(data_ndDRTT[:, j, :], level=0.5)	
		for contour in contours_ndDRTT:
			rr, cc = np.round(contour).astype(int).T
			valid = (rr >= 0) & (rr < slice_2d.shape[0]) & (cc >= 0) & (cc < slice_2d.shape[1])
			contour_mask[rr[valid], j, cc[valid], 0] = 2
			contour_mask[rr[valid], j, cc[valid], 4] = 2
		
		contours_DRTT = measure.find_contours(data_DRTT[:, j, :], level=0.5)	
		for contour in contours_DRTT:
			rr, cc = np.round(contour).astype(int).T
			valid = (rr >= 0) & (rr < slice_2d.shape[0]) & (cc >= 0) & (cc < slice_2d.shape[1])
			contour_mask[rr[valid], j, cc[valid], 1] = 3
			contour_mask[rr[valid], j, cc[valid], 4] = 3
			
		contours_CST = measure.find_contours(data_CST[:, j, :], level=0.5)	
		for contour in contours_CST:
			rr, cc = np.round(contour).astype(int).T
			valid = (rr >= 0) & (rr < slice_2d.shape[0]) & (cc >= 0) & (cc < slice_2d.shape[1])
			contour_mask[rr[valid], j, cc[valid], 2] = 4  
			contour_mask[rr[valid], j, cc[valid], 4] = 4
		
		contours_ML = measure.find_contours(data_ML[:, j, :], level=0.5)	
		for contour in contours_ML:
			rr, cc = np.round(contour).astype(int).T
			valid = (rr >= 0) & (rr < slice_2d.shape[0]) & (cc >= 0) & (cc < slice_2d.shape[1])
			contour_mask[rr[valid], j, cc[valid], 3] = 5
			contour_mask[rr[valid], j, cc[valid], 4] = 5
	
	nifti_contour = nib.Nifti1Image(contour_mask, im_ref.affine)
	nib.save(nifti_contour, "coronal_contour.nii.gz")
	print("Image coronal_contour.nii.gz saved")
		
		
# Main
## Load files

track_ndDRTT = nib.load("track_ndDRTT_lh.nii.gz") 
track_DRTT = nib.load("track_DRTT_lh.nii.gz") 
track_CST = nib.load("track_CST_lh.nii.gz") 
track_ML = nib.load("track_ML_lh.nii.gz") 
mask_lesion = nib.load("mask_lesion_float_up.nii.gz")

print(".Files loaded")

## Extract data from image
data_ndDRTT = track_ndDRTT.get_fdata().astype(np.uint16) 
data_DRTT = track_DRTT.get_fdata().astype(np.uint16) 
data_CST = track_CST.get_fdata().astype(np.uint16) 
data_ML = track_ML.get_fdata().astype(np.uint16) 
data_lesion = mask_lesion.get_fdata()

print(".Data loaded")

del track_ndDRTT, track_DRTT, track_CST, track_ML

data_reference = np.zeros(data_lesion.shape)
data_reference[data_lesion != 0] = 1 - data_lesion[data_lesion != 0]

nifti_teste = nib.Nifti1Image(data_reference, mask_lesion.affine)
nib.save(nifti_teste, "data_reference.nii.gz")

#handleAxialcontour(mask_lesion, "left", data_lesion, data_ndDRTT, data_DRTT, data_CST, data_ML)
#handleCoronalcontour(mask_lesion, "left", data_lesion, data_ndDRTT, data_DRTT, data_CST, data_ML)
intersection_ndDRTT = handleRelativeintersection(data_reference, data_ndDRTT)
print(intersection_ndDRTT)
intersection_DRTT = handleRelativeintersection(data_reference, data_DRTT)
print(intersection_DRTT)
intersection_CST = handleRelativeintersection(data_reference, data_CST)
print(intersection_CST)
