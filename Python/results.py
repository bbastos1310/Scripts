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
## Leitura do hemisfério
with open('../Segmentation/hemisphere.txt', 'r', encoding='utf-8') as file_hemisphere:
    hemisphere = file_hemisphere.read()  
print(f"{hemisphere} hemisphere")

if (hemisphere == 'left'):
	track_ndDRTT_ACPC = nib.load("ACPC/track_ndDRTT_lh_ACPC.nii.gz") 
	track_DRTT_ACPC = nib.load("ACPC/track_dDRTT_lh_ACPC.nii.gz") 
	track_CST_ACPC = nib.load("ACPC/track_CST_lh_ACPC.nii.gz") 
	track_ML_ACPC = nib.load("ACPC/track_ML_lh_ACPC.nii.gz") 
	mask_lesion_ACPC = nib.load("ACPC/mask_lesion_float_up_ACPC.nii.gz")
	track_ndDRTT = nib.load("track_ndDRTT_lh.nii.gz") 
	track_DRTT = nib.load("track_dDRTT_lh.nii.gz") 
	track_CST = nib.load("track_CST_lh.nii.gz") 
	track_ML = nib.load("track_ML_lh.nii.gz") 
	mask_lesion = nib.load("mask_lesion_float_up.nii.gz")

elif (hemisphere == 'right'):
	track_ndDRTT_ACPC = nib.load("ACPC/track_ndDRTT_rh_ACPC_aligned.nii.gz") 
	track_DRTT_ACPC = nib.load("ACPC/track_dDRTT_rh_ACPC_aligned.nii.gz") 
	track_CST_ACPC = nib.load("ACPC/track_CST_rh_ACPC_aligned.nii.gz") 
	track_ML_ACPC = nib.load("ACPC/track_ML_rh_ACPC_aligned.nii.gz") 
	mask_lesion_ACPC = nib.load("ACPC/mask_lesion_float_up_ACPC_aligned.nii.gz")
	# track_ndDRTT = nib.load("track_ndDRTT_rh.nii.gz") 
	# track_DRTT = nib.load("track_dDRTT_rh.nii.gz") 
	# track_CST = nib.load("track_CST_rh.nii.gz") 
	# track_ML = nib.load("track_ML_rh.nii.gz") 
	# mask_lesion = nib.load("mask_lesion_float_up.nii.gz")

print(".Files loaded (ACPC)")

## Extract data from image
data_ndDRTT_ACPC = track_ndDRTT_ACPC.get_fdata().astype(np.uint16) 
data_DRTT_ACPC = track_DRTT_ACPC.get_fdata().astype(np.uint16) 
data_CST_ACPC = track_CST_ACPC.get_fdata().astype(np.uint16) 
data_ML_ACPC = track_ML_ACPC.get_fdata().astype(np.uint16) 
data_lesion_ACPC = mask_lesion_ACPC.get_fdata()
# data_ndDRTT = track_ndDRTT.get_fdata().astype(np.uint16) 
# data_DRTT = track_DRTT.get_fdata().astype(np.uint16) 
# data_CST = track_CST.get_fdata().astype(np.uint16) 
# data_ML = track_ML.get_fdata().astype(np.uint16) 
# data_lesion = mask_lesion.get_fdata()

del track_ndDRTT_ACPC, track_DRTT_ACPC, track_CST_ACPC, track_ML_ACPC

print(".Data loaded(ACPC)")

#mask_lesion_filtered, data_reference = handleLesiondata(data_lesion, mask_lesion.affine)
mask_lesion_filtered_ACPC, data_reference_ACPC = handleLesiondata(data_lesion_ACPC, mask_lesion_ACPC.affine)

#handleAxialcontour(mask_lesion_ACPC, hemisphere, "acpc", mask_lesion_filtered_ACPC, data_ndDRTT_ACPC, data_DRTT_ACPC, data_CST_ACPC, data_ML_ACPC)
handleAxialcontour(mask_lesion_ACPC, hemisphere, "acpc", mask_lesion_filtered_ACPC, data_ndDRTT_ACPC, data_DRTT_ACPC, data_CST_ACPC, data_ML_ACPC)
handleCoronalcontour(mask_lesion_ACPC, hemisphere, mask_lesion_filtered_ACPC, data_ndDRTT_ACPC, data_DRTT_ACPC, data_CST_ACPC, data_ML_ACPC)
