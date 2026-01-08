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

def handleLesiondata(data_lesion_float, data_lesion_smoothed, image, threshold):
	data_lesion_filtered = np.zeros(data_lesion_float.shape, dtype=float)
	mask_lesion = np.zeros(data_lesion_float.shape, dtype=np.uint8)
	mask_closed = np.zeros(data_lesion_float.shape, dtype=np.uint8)
	
	for k in range(data_lesion_float.shape[2]):
	  contornos = measure.find_contours(np.abs(data_lesion_float[:,:,k]), level=threshold)
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
	
	# Voxels do centro da lesão
	data_lesion_filtered[mask_closed_connected_solid == 1] = data_lesion_float[mask_closed_connected_solid == 1]
	data_center = np.zeros(data_lesion_float.shape, dtype=np.uint8)
	data_center[(data_lesion_filtered < 0.1) & (data_lesion_filtered != 0)] = 1
	mask_center_connected = functions.connectedComponents(data_center).astype(np.uint8)
	
	functions.saveImage(mask_center_connected, image, "lesion_center")
	# nifti_center = nib.Nifti1Image(mask_center_connected, affine)
	# nib.save(nifti_center, "../Analysis/lesion_center.nii.gz")
				
	# Máscara binária
	data_binary = (data_lesion_smoothed > 0.5).astype(np.uint8)
	
	functions.saveImage(data_binary, image, "lesion_binary")
	# nifti_binary = nib.Nifti1Image(data_binary, affine)
	# nib.save(nifti_binary, "../Analysis/lesion_binary.nii.gz")
	
	# Pesos de acordo com a distância ao centro do voxel
	
	data_weight = functions.minDistance(data_binary, mask_center_connected)
	data_weight[data_binary != 0] = 1 - (data_weight[data_binary != 0]/data_weight[data_binary != 0].max())
	
	functions.saveImage(data_weight, image, "lesion_weight")
	# nifti_weight = nib.Nifti1Image(data_weight, affine)
	# nib.save(nifti_weight, "../Analysis/lesion_weight.nii.gz")
	
	return data_binary, data_weight, mask_center_connected

def handleWeightedintersection (data_reference, data_compare):
	# Função para quantizar a interseção do parâmetro analisado com a lesão, leva em consideração a distância do centro da lesão em cada voxel ("Análogo a uma média ponderada")
	
	data_intersection = np.zeros(data_reference.shape, dtype=np.float16)
	mask_intersection = ((data_reference != 0) & (data_compare != 0)).astype(bool)
	data_intersection[mask_intersection] = data_reference[mask_intersection] * data_compare[mask_intersection] # Multiplicação dos valores nos voxels em que ocorre interseção
	print(f"inter_sum:{data_intersection.sum()}, ref_sum:{data_reference.sum()}")
	rel_intersection = data_intersection.sum()/data_reference.sum() 
	return rel_intersection
	
def handleAbsoluteintersection (data_reference, data_compare):
	# Função para quantificar a interseção do parâmetro analisado com a lesão, leva em consideração a intensidade da lesão em cada voxel ("Análogo a uma média ponderada")
	
	data_intersection = np.zeros(data_reference.shape, dtype=np.float16)
	mask_intersection = ((data_reference != 0) & (data_compare != 0)).astype(bool)
	intersection = (mask_intersection[mask_intersection == True].size)*(0.4)**3
	
	return intersection
	
def handleMintrackdistance(data_center, data_track):
	
	data_distances = functions.minDistance(data_center, data_track)
	#functions.saveImage(data_distances,image,"distances")
	min_distance = data_distances[data_center == True].min()
	
	return data_distances
		
		
		
# Main
## Load files

with open('../Segmentation/hemisphere.txt', 'r', encoding='utf-8') as file_hemisphere:
    hemisphere = file_hemisphere.read()  
print(f"{hemisphere} hemisphere")

if (hemisphere == 'left'):
	track_ndDRTT_ACPC = nib.load("../Tractography/ACPC/track_ndDRTT_lh_ACPC_aligned.nii.gz") 
	track_dDRTT_ACPC = nib.load("../Tractography/ACPC/track_dDRTT_lh_ACPC_aligned.nii.gz") 
	track_CST_ACPC = nib.load("../Tractography/ACPC/track_CST_lh_ACPC_aligned.nii.gz") 
	track_ML_ACPC = nib.load("../Tractography/ACPC/track_ML_lh_ACPC_aligned.nii.gz") 
	mask_lesion_float = nib.load("../Tractography/ACPC/mask_lesion_float_up_ACPC_aligned.nii.gz")
	mask_lesion_smoothed = nib.load("../Tractography/ACPC/mask_lesion_smoothed_up_ACPC_aligned.nii.gz")
	

elif (hemisphere == 'right'):
	track_ndDRTT_ACPC = nib.load("../Tractography/ACPC/track_ndDRTT_rh_ACPC_aligned.nii.gz") 
	track_dDRTT_ACPC = nib.load("../Tractography/ACPC/track_dDRTT_rh_ACPC_aligned.nii.gz") 
	track_CST_ACPC = nib.load("../Tractography/ACPC/track_CST_rh_ACPC_aligned.nii.gz") 
	track_ML_ACPC = nib.load("../Tractography/ACPC/track_ML_rh_ACPC_aligned.nii.gz") 
	mask_lesion_float = nib.load("../Tractography/ACPC/mask_lesion_float_up_ACPC_aligned.nii.gz")
	mask_lesion_smoothed = nib.load("../Tractography/ACPC/mask_lesion_smoothed_up_ACPC_aligned.nii.gz")


print(".Files loaded (ACPC)")

## Extract data from image
data_ndDRTT_ACPC = track_ndDRTT_ACPC.get_fdata().astype(np.uint16) 
data_dDRTT_ACPC = track_dDRTT_ACPC.get_fdata().astype(np.uint16) 
data_CST_ACPC = track_CST_ACPC.get_fdata().astype(np.uint16) 
data_ML_ACPC = track_ML_ACPC.get_fdata().astype(np.uint16) 
data_lesion_float = mask_lesion_float.get_fdata()
data_lesion_smoothed = mask_lesion_smoothed.get_fdata()

print(".Data loaded(ACPC)")

del track_ndDRTT_ACPC, track_dDRTT_ACPC, track_CST_ACPC, track_ML_ACPC

data_binary, data_weight, data_center = handleLesiondata(data_lesion_float, data_lesion_smoothed, mask_lesion_float, 0.1)

#Volume da lesão
lesion_volume = (data_binary[data_binary == True].size)*(0.4)**3
print(f"Volume = {lesion_volume}")

#ndDRTT
abs_intersection_ndDRTT = handleAbsoluteintersection(data_binary, data_ndDRTT_ACPC)
rel_intersection_ndDRTT = handleWeightedintersection(data_weight, data_ndDRTT_ACPC)
distance_ndDRTT = handleMintrackdistance(data_center, data_ndDRTT_ACPC)
print(f"TRACT ndDRTT \n Absolute = {abs_intersection_ndDRTT}, Relative = {rel_intersection_ndDRTT}, Distance = {distance_ndDRTT}")

#dDRTT
abs_intersection_dDRTT = handleAbsoluteintersection(data_binary, data_dDRTT_ACPC)
rel_intersection_dDRTT = handleWeightedintersection(data_weight, data_dDRTT_ACPC)
distance_dDRTT = handleMintrackdistance(data_center, data_dDRTT_ACPC)
print(f"TRACT dDRTT \n Absolute = {abs_intersection_dDRTT}, Relative = {rel_intersection_dDRTT}, Distance = {distance_dDRTT}")

#CST
abs_intersection_CST = handleAbsoluteintersection(data_binary, data_CST_ACPC)
rel_intersection_CST = handleWeightedintersection(data_weight, data_CST_ACPC)
distance_CST = handleMintrackdistance(data_center, data_CST_ACPC, mask_lesion_float)
print(f"TRACT CST \n Absolute = {abs_intersection_CST}, Relative = {rel_intersection_CST}, Distance = {distance_CST}")

#ML
abs_intersection_ML = handleAbsoluteintersection(data_binary, data_ML_ACPC)
rel_intersection_ML = handleWeightedintersection(data_weight, data_ML_ACPC)
distance_ML = handleMintrackdistance(data_center, data_ML_ACPC)
print(f"TRACT ndDRTT \n Absolute = {abs_intersection_ML}, Relative = {rel_intersection_ML}, Distance = {distance_ML}")

