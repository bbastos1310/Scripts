import nibabel as nib
import matplotlib.pyplot as plt
import numpy as np
import os
from joblib import Parallel, delayed
from scipy.ndimage import gaussian_filter, binary_fill_holes
from skimage import measure
from skimage.morphology import binary_closing

import functions

def handleRelativeintersection (data_reference, data_compare):
	# Função para quantizar a interseção do parâmetro analisado com a lesão, leva em consideração a intensidade da lesão em cada voxel ("Análogo a uma média ponderada")
	
	data_intersection = np.zeros(data_reference.shape, dtype=np.float16)
	mask_intersection = ((data_reference != 0) & (data_compare != 0)).astype(bool)
	data_intersection[mask_intersection] = data_reference[mask_intersection] * data_compare[mask_intersection] # Multiplicação dos valores nos voxels em que ocorre interseção
	print(f"inter_sum:{data_intersection.sum()}, ref_sum:{data_reference.sum()}")
	rel_intersection = data_intersection.sum()/data_reference.sum() 
	return rel_intersection
	
def handleAxialcontour (im_ref, hemisphere, plan, data_lesion, data_ndDRTT, data_DRTT, data_CST, data_ML):
	# Função que cria os contornos dos tratos 
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
		
		contours_lesion = measure.find_contours(data_lesion[:,:,k], level=0.3)	
		for contour in contours_lesion:
			rr, cc = np.round(contour).astype(int).T
			valid = (rr >= 0) & (rr < slice_2d.shape[0]) & (cc >= 0) & (cc < slice_2d.shape[1])
			contour_mask_ndDRTT[rr[valid], cc[valid], k] = 1
			contour_mask_DRTT[rr[valid], cc[valid], k] = 1
			contour_mask_CST[rr[valid], cc[valid], k] = 1
			contour_mask_ML[rr[valid], cc[valid], k] = 1  
		
		contours_ndDRTT = measure.find_contours(data_ndDRTT[:,:,k], level=0.5)	
		for contour in contours_ndDRTT:
			rr, cc = np.round(contour).astype(int).T
			valid = (rr >= 0) & (rr < slice_2d.shape[0]) & (cc >= 0) & (cc < slice_2d.shape[1])
			contour_mask_ndDRTT[rr[valid], cc[valid], k] = 2
		
		contours_DRTT = measure.find_contours(data_DRTT[:,:,k], level=0.5)	
		for contour in contours_DRTT:
			rr, cc = np.round(contour).astype(int).T
			valid = (rr >= 0) & (rr < slice_2d.shape[0]) & (cc >= 0) & (cc < slice_2d.shape[1])
			contour_mask_DRTT[rr[valid], cc[valid], k] = 3 
			
		contours_CST = measure.find_contours(data_CST[:,:,k], level=0.5)	
		for contour in contours_CST:
			rr, cc = np.round(contour).astype(int).T
			valid = (rr >= 0) & (rr < slice_2d.shape[0]) & (cc >= 0) & (cc < slice_2d.shape[1])
			contour_mask_CST[rr[valid], cc[valid], k] = 4  
		
		contours_ML = measure.find_contours(data_ML[:,:,k], level=0.5)	
		for contour in contours_ML:
			rr, cc = np.round(contour).astype(int).T
			valid = (rr >= 0) & (rr < slice_2d.shape[0]) & (cc >= 0) & (cc < slice_2d.shape[1])
			contour_mask_ML[rr[valid], cc[valid], k] = 5
	if (plan == 'axial'):
		nifti_contour = nib.Nifti1Image(contour_mask_ndDRTT, im_ref.affine)
		nib.save(nifti_contour, "axial_contour_ndDRTT.nii.gz")

		nifti_contour = nib.Nifti1Image(contour_mask_DRTT, im_ref.affine)
		nib.save(nifti_contour, "axial_contour_DRTT.nii.gz")

		nifti_contour = nib.Nifti1Image(contour_mask_CST, im_ref.affine)
		nib.save(nifti_contour, "axial_contour_CST.nii.gz")

		nifti_contour = nib.Nifti1Image(contour_mask_ML, im_ref.affine)
		nib.save(nifti_contour, "axial_contour_ML.nii.gz")
	elif (plan == 'acpc'):
		nifti_contour = nib.Nifti1Image(contour_mask_ndDRTT, im_ref.affine)
		nib.save(nifti_contour, "Contour/acpc_contour_ndDRTT.nii.gz")

		nifti_contour = nib.Nifti1Image(contour_mask_DRTT, im_ref.affine)
		nib.save(nifti_contour, "Contour/acpc_contour_DRTT.nii.gz")

		nifti_contour = nib.Nifti1Image(contour_mask_CST, im_ref.affine)
		nib.save(nifti_contour, "Contour/acpc_contour_CST.nii.gz")

		nifti_contour = nib.Nifti1Image(contour_mask_ML, im_ref.affine)
		nib.save(nifti_contour, "Contour/acpc_contour_ML.nii.gz")
	print("images saved")
	
def handleCoronalcontour (im_ref, hemisphere, data_lesion, data_ndDRTT, data_DRTT, data_CST, data_ML):
	# Função que cria os contornos dos tratos 
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
			contour_mask_ndDRTT[rr[valid], j, cc[valid]] = 1  
			contour_mask_DRTT[rr[valid], j, cc[valid]] = 1  
			contour_mask_CST[rr[valid], j, cc[valid]] = 1  
			contour_mask_ML[rr[valid], j, cc[valid]] = 1  
		
		contours_ndDRTT = measure.find_contours(data_ndDRTT[:, j, :], level=0.5)	
		for contour in contours_ndDRTT:
			rr, cc = np.round(contour).astype(int).T
			valid = (rr >= 0) & (rr < slice_2d.shape[0]) & (cc >= 0) & (cc < slice_2d.shape[1])
			contour_mask_ndDRTT[rr[valid], j, cc[valid]] = 2
					
		contours_DRTT = measure.find_contours(data_DRTT[:, j, :], level=0.5)	
		for contour in contours_DRTT:
			rr, cc = np.round(contour).astype(int).T
			valid = (rr >= 0) & (rr < slice_2d.shape[0]) & (cc >= 0) & (cc < slice_2d.shape[1])
			contour_mask_DRTT[rr[valid], j, cc[valid]] = 3
						
		contours_CST = measure.find_contours(data_CST[:, j, :], level=0.5)	
		for contour in contours_CST:
			rr, cc = np.round(contour).astype(int).T
			valid = (rr >= 0) & (rr < slice_2d.shape[0]) & (cc >= 0) & (cc < slice_2d.shape[1])
			contour_mask_CST[rr[valid], j, cc[valid]] = 4  
					
		contours_ML = measure.find_contours(data_ML[:, j, :], level=0.5)	
		for contour in contours_ML:
			rr, cc = np.round(contour).astype(int).T
			valid = (rr >= 0) & (rr < slice_2d.shape[0]) & (cc >= 0) & (cc < slice_2d.shape[1])
			contour_mask_ML[rr[valid], j, cc[valid]] = 5
	
	nifti_contour = nib.Nifti1Image(contour_mask_ndDRTT, im_ref.affine)
	nib.save(nifti_contour, "coronal_contour_ndDRTT.nii.gz")
	
	nifti_contour = nib.Nifti1Image(contour_mask_DRTT, im_ref.affine)
	nib.save(nifti_contour, "coronal_contour_DRTT.nii.gz")
	
	nifti_contour = nib.Nifti1Image(contour_mask_CST, im_ref.affine)
	nib.save(nifti_contour, "coronal_contour_CST.nii.gz")
	
	nifti_contour = nib.Nifti1Image(contour_mask_ML, im_ref.affine)
	nib.save(nifti_contour, "coronal_contour_ML.nii.gz")
	


def handleLesiondata(data_lesion_up, affine):
	data_lesion_filtered = np.zeros(data_lesion_up.shape, dtype=float)
	mask_lesion = np.zeros(data_lesion_up.shape, dtype=np.uint8)
	mask_closed = np.zeros(data_lesion_up.shape, dtype=np.uint8)
	
	for k in range(data_lesion_up.shape[2]):
	  contornos = measure.find_contours(np.abs(data_lesion_up[:,:,k]), level=0.25)
	  # Itera sobre cada contorno encontrado
	  for contorno in contornos:
		  # Obter as coordenadas dos contornos
		  r = contorno[:, 0].astype(int)
		  c = contorno[:, 1].astype(int)
		  mask_lesion[r, c, k] = 1
		  
	kmin = np.where(mask_lesion != 0)[2].min()
	kmax = np.where(mask_lesion != 0)[2].max()
	for k in range (kmin, kmax + 1):
		mask_closed[:,:,k] = binary_fill_holes(mask_lesion[:,:,k])
		
	mask_closed_connected = functions.connectedComponents(mask_closed)
	
	chunk_size = 64
	chunks = [
		mask_closed_connected[i:i+chunk_size, j:j+chunk_size, k:k+chunk_size]
		for i in range(0, 640, chunk_size)
		for j in range(0, 640, chunk_size)
		for k in range(0, 640, chunk_size)
	]

	# Processa chunks em paralelo
	results = Parallel(n_jobs=os.cpu_count())(
		delayed(functions.process_chunk)(chunk) for chunk in chunks
	)

	# Recompõe a imagem
	mask_closed_connected_solid = np.zeros_like(mask_closed_connected)
	idx = 0
	for i in range(0, 640, chunk_size):
		for j in range(0, 640, chunk_size):
			for k in range(0, 640, chunk_size):
				mask_closed_connected_solid[
					i:i+chunk_size, 
					j:j+chunk_size, 
					k:k+chunk_size
				] = results[idx]
				idx += 1
				
	# Suavização Gaussiana
	mask_lesion_smoothed = gaussian_filter(mask_closed_connected_solid.astype(float), sigma=2)
	mask_lesion_smoothed_binary = (mask_lesion_smoothed > 0.5).astype(np.uint8)
	
	data_lesion_filtered[mask_lesion_smoothed_binary == 1] = data_lesion_up[mask_lesion_smoothed_binary == 1]
	
	nifti_teste = nib.Nifti1Image(data_lesion_filtered, affine)
	nib.save(nifti_teste, "lesion_teste.nii.gz")
	
	mask_center = np.zeros(data_lesion_up.shape, dtype=np.uint8)
	mask_center[(data_lesion_filtered < 0.15) & (data_lesion_filtered != 0)] = 1
	mask_center_connected = functions.connectedComponents(mask_center).astype(np.uint8)
	
	mask_reference = functions.minDistance(mask_lesion_smoothed_binary, mask_center_connected)
	mask_reference[mask_lesion_smoothed_binary != 0] = 1 - (mask_reference[mask_lesion_smoothed_binary != 0]/mask_reference[mask_lesion_smoothed_binary != 0].max())
		
	nifti_teste = nib.Nifti1Image(mask_reference, affine)
	nib.save(nifti_teste, "lesion_center_teste.nii.gz")
	
	return mask_lesion_smoothed_binary, mask_reference
		
		
		
# Main
## Load files

# track_ndDRTT = nib.load("track_ndDRTT_lh.nii.gz") 
# track_DRTT = nib.load("track_DRTT_lh.nii.gz") 
# track_CST = nib.load("track_CST_lh.nii.gz") 
# track_ML = nib.load("track_ML_lh.nii.gz") 
# mask_lesion = nib.load("mask_lesion_float_up.nii.gz")

# print(".Files loaded")

## Extract data from image
# data_ndDRTT = track_ndDRTT.get_fdata().astype(np.uint16) 
# data_DRTT = track_DRTT.get_fdata().astype(np.uint16) 
# data_CST = track_CST.get_fdata().astype(np.uint16) 
# data_ML = track_ML.get_fdata().astype(np.uint16) 
# data_lesion = mask_lesion.get_fdata()

# print(".Data loaded")

# del track_ndDRTT, track_DRTT, track_CST, track_ML

# mask_lesion_filtered, data_reference = handleLesiondata(data_lesion, mask_lesion.affine)

# handleAxialcontour(mask_lesion, "left", "axial", data_lesion, data_ndDRTT, data_DRTT, data_CST, data_ML)
# handleCoronalcontour(mask_lesion, "left", data_lesion, data_ndDRTT, data_DRTT, data_CST, data_ML)
# intersection_ndDRTT = handleRelativeintersection(data_reference, data_ndDRTT)
# print(intersection_ndDRTT)
# intersection_DRTT = handleRelativeintersection(data_reference, data_DRTT)
# print(intersection_DRTT)
# intersection_CST = handleRelativeintersection(data_reference, data_CST)
# print(intersection_CST)
# intersection_ML = handleRelativeintersection(data_reference, data_ML)
# print(intersection_ML)

## ACPC plan
## Load files
track_ndDRTT_ACPC = nib.load("ACPC/track_ndDRTT_lh_ACPC.nii.gz") 
track_DRTT_ACPC = nib.load("ACPC/track_DRTT_lh_ACPC.nii.gz") 
track_CST_ACPC = nib.load("ACPC/track_CST_lh_ACPC.nii.gz") 
track_ML_ACPC = nib.load("ACPC/track_ML_lh_ACPC.nii.gz") 
mask_lesion_ACPC = nib.load("ACPC/mask_lesion_float_up_ACPC.nii.gz")

print(".Files loaded (ACPC)")

## Extract data from image
data_ndDRTT_ACPC = track_ndDRTT_ACPC.get_fdata().astype(np.uint16) 
data_DRTT_ACPC = track_DRTT_ACPC.get_fdata().astype(np.uint16) 
data_CST_ACPC = track_CST_ACPC.get_fdata().astype(np.uint16) 
data_ML_ACPC = track_ML_ACPC.get_fdata().astype(np.uint16) 
data_lesion_ACPC = mask_lesion_ACPC.get_fdata()

del track_ndDRTT_ACPC, track_DRTT_ACPC, track_CST_ACPC, track_ML_ACPC

print(".Data loaded(ACPC)")

handleAxialcontour(mask_lesion_ACPC, "left", "acpc", data_lesion_ACPC, data_ndDRTT_ACPC, data_DRTT_ACPC, data_CST_ACPC, data_ML_ACPC)
