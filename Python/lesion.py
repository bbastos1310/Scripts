# Local libraries
import functions
import roi_definition as roi

# External libraries
import nibabel as nib
import numpy as np
from scipy.ndimage import gaussian_filter, binary_fill_holes, center_of_mass, generate_binary_structure, binary_dilation
from skimage.morphology import footprint_rectangle, closing
from skimage import measure
from joblib import Parallel, delayed
import os

def handleLesionmask(data, data_rostral_lh, data_rostral_rh, Contrast):
	print(f"Lesion's mask")
	
	# Inicializa uma máscara binária com zeros
	mask = np.zeros(np.abs(data).shape, dtype=np.float32)
	
	#Percentis para definição do threshold
	sphere_lh = functions.sphereMask(data_rostral_lh, 15)
	# print(f"percentil_92_lh = {np.percentile(data[sphere_lh],92)}")
	# print(f"percentil_95_lh = {np.percentile(data[sphere_lh],95)}")
	# print(f"percentil_98_lh = {np.percentile(data[sphere_lh],98)}")
	percentile_lh_92 = np.percentile(data[sphere_lh],92)
	percentile_lh_95 = np.percentile(data[sphere_lh],95)
	percentile_lh_98 = np.percentile(data[sphere_lh],98)
	
	sphere_rh = functions.sphereMask(data_rostral_rh, 15)
	# print(f"percentil_92_rh = {np.percentile(data[sphere_rh],92)}")
	# print(f"percentil_95_rh = {np.percentile(data[sphere_rh],95)}")
	# print(f"percentil_98_rh = {np.percentile(data[sphere_rh],98)}")
	percentile_rh_92 = np.percentile(data[sphere_rh],92)
	percentile_rh_95 = np.percentile(data[sphere_rh],95)
	percentile_rh_98 = np.percentile(data[sphere_rh],98)
	
	if (percentile_lh_98 > percentile_rh_98):
		threshold = percentile_lh_98
		threshold_2 = percentile_lh_95
		threshold_3 = percentile_lh_92
	else:
		threshold = percentile_rh_98
		threshold_2 = percentile_rh_95
		threshold_3 = percentile_rh_92
	
	# Verifica o contorno para cada corte a partir de um limiar
	for x in range(data.shape[0]):
	  contornos = measure.find_contours(np.abs(data[x,:,:]), level=threshold)
	  # Itera sobre cada contorno encontrado
	  for contorno in contornos:
		  # Obter as coordenadas dos contornos
		  r = contorno[:, 0].astype(int)
		  c = contorno[:, 1].astype(int)
		  mask[x, r, c] = 1
  
	# plt.imshow(mask[:,113,:], cmap='gray')
	# # Salvar a imagem em um arquivo
	# plt.savefig("mask_contour.png")  # Salva como arquivo PNG
	# # Fechar o plot para liberar memória
	# plt.close()
	# print("-Imagem mask_contour.png salva")
	
	# Closing
	mask_closed = np.zeros(data.shape)
	for x in range (data.shape[0]):
	  mask_closed[x,:,:] = closing(mask[x,:,:], footprint_rectangle((4, 4)))
	
	# Labels
	label_mask, num_labels = measure.label(mask_closed,connectivity=1 ,return_num=True)
	
	# Define o limite mínimo de voxels para manter os labels
	min_voxels = 200  # Ajuste este valor conforme necessário
	
	# Itera sobre os labels e calcula as propriedades dos objetos rotulados
	labels_filtered = np.zeros_like(label_mask)
	for region in measure.regionprops(label_mask):
		if region.area >= min_voxels:  # `area` retorna o número de voxels
			labels_filtered[label_mask == region.label] = region.label
	
	# plt.imshow(color.label2rgb(labels_filtered[:,113,:], bg_label=0))
	# plt.savefig("filtered_labels.png")  # Salva como arquivo PNG
	# plt.close
	# print("-Imagem filtered_labels.png salva")
	
	# Lesion selection
	closest_label = None
	min_distance = float('inf')
	lesion_hemisphere = "left"
	center_rostral_lh = center_of_mass(data_rostral_lh)
	center_rostral_rh = center_of_mass(data_rostral_rh)
	
	print("-Cálculo do label mais próximo do centro, esse comando é um pouco demorado")
	
	# Calcular o centro de massa de cada label e a distância no hemisfério esquerdo
	for label in range(1, num_labels + 1):  # Começa do label 1 até o número total de labels
		actual_label = (labels_filtered == label)  # Cria uma máscara para o label atual
		center = center_of_mass(actual_label)  # Calcula o centro de massa

		# Calcula a distância entre o centro do label e o centro da imagem
		distance_center = np.linalg.norm(np.array(center) - center_rostral_lh)

		# Atualiza o label mais central se a distância for menor
		if distance_center < min_distance:
			min_distance = distance_center
			closest_label = label
			center_lesion = center
	
	# Calcular o centro de massa de cada label e a distância no hemisfério direito
	for label in range(1, num_labels + 1):  # Começa do label 1 até o número total de labels
		actual_label = (labels_filtered == label)  # Cria uma máscara para o label atual
		center = center_of_mass(actual_label)  # Calcula o centro de massa

		# Calcula a distância entre o centro do label e o centro da imagem
		distance_center = np.linalg.norm(np.array(center) - center_rostral_rh)

		# Atualiza o label mais central se a distância for menor
		if distance_center < min_distance:
			lesion_hemisphere = "right"
			min_distance = distance_center
			closest_label = label
			center_lesion = center
	
	# Voxels pertencentes à lesão
	mask_lesion = (labels_filtered == closest_label)
	lesion_index_tuple = np.where(mask_lesion == True)
	x_array = lesion_index_tuple[0]
	y_array = lesion_index_tuple[1]
	z_array = lesion_index_tuple[2]	
	num_points = len(x_array)
	lesion_coordinates = np.zeros((num_points, 3))
	for point in range(num_points):
	  lesion_coordinates[point] = [x_array[point], y_array[point], z_array[point]]
	
	# Criação de uma imagem da máscara da lesão
	lesion_coordinates = lesion_coordinates.astype(np.int32)
	lesion_data_float = np.zeros(data.shape)
	lesion_data_binary = np.zeros(data.shape)
	for point in range(num_points):
	  lesion_data_float[lesion_coordinates[point][0],lesion_coordinates[point][1],lesion_coordinates[point][2]] = data[lesion_coordinates[point][0],lesion_coordinates[point][1],lesion_coordinates[point][2]]
	  lesion_data_binary[lesion_coordinates[point][0],lesion_coordinates[point][1],lesion_coordinates[point][2]] = 1
	functions.saveImage(lesion_data_float, Contrast, "mask_lesion_float_initial")
	functions.saveImage(lesion_data_binary, Contrast, "mask_lesion_binary_initial")
	
	with open("hemisphere.txt", "w") as file_hemisphere:
		file_hemisphere.write(lesion_hemisphere)
	
	print(f"lesion_hemisphere = {lesion_hemisphere}")
	
	return lesion_data_float, lesion_data_binary, threshold, threshold_2, threshold_3

def handleLesioncenter(data_lesion_float, image, threshold):
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
		
	functions.saveImage(mask_closed.astype(np.int8), image, "mask_closed")
		
	mask_closed_connected = functions.connectedComponents(mask_closed)
	functions.saveImage(mask_closed_connected.astype(np.int8), image, "mask_closed_connected")
	
	# chunk_size = 64
	# chunks = [
		# mask_closed_connected[i:i+chunk_size, j:j+chunk_size, k:k+chunk_size]
		# for i in range(0, 640, chunk_size)
		# for j in range(0, 640, chunk_size)
		# for k in range(0, 640, chunk_size)
	# ]

	# # Processa chunks em paralelo
	# results = Parallel(n_jobs=os.cpu_count())(
		# delayed(functions.process_chunk)(chunk) for chunk in chunks
	# )

	# # Recompõe a imagem
	# mask_closed_connected_solid = np.zeros_like(mask_closed_connected)
	# idx = 0
	# for i in range(0, 640, chunk_size):
		# for j in range(0, 640, chunk_size):
			# for k in range(0, 640, chunk_size):
				# mask_closed_connected_solid[
					# i:i+chunk_size, 
					# j:j+chunk_size, 
					# k:k+chunk_size
				# ] = results[idx]
				# idx += 1
	
	# Voxels do centro da lesão
	data_lesion_filtered[mask_closed_connected == 1] = data_lesion_float[mask_closed_connected == 1]
	data_center = np.zeros(data_lesion_float.shape, dtype=np.uint8)
	data_center[(data_lesion_filtered < 0.1) & (data_lesion_filtered != 0)] = 1
	mask_center_connected = functions.connectedComponents(data_center).astype(np.uint8)
	
	functions.saveImage(mask_center_connected, image, "mask_lesion_center")
	# nifti_center = nib.Nifti1Image(mask_center_connected, affine)
	# nib.save(nifti_center, "../Analysis/lesion_center.nii.gz")
				
	## Máscara binária
	# data_binary = (data_lesion_smoothed > 0.5).astype(np.uint8)
	
	# functions.saveImage(data_binary, image, "lesion_binary")
	# nifti_binary = nib.Nifti1Image(data_binary, affine)
	# nib.save(nifti_binary, "../Analysis/lesion_binary.nii.gz")
	
	## Pesos de acordo com a distância ao centro do voxel
	
	# data_weight = functions.minDistance(data_binary, mask_center_connected)
	# data_weight[data_binary != 0] = 1 - (data_weight[data_binary != 0]/data_weight[data_binary != 0].max())
	
	# functions.saveImage(data_weight, image, "lesion_weight")
	# nifti_weight = nib.Nifti1Image(data_weight, affine)
	# nib.save(nifti_weight, "../Analysis/lesion_weight.nii.gz")
	
	return mask_center_connected

def handleZones(data_difference, data_center, image, threshold, threshold_2, threshold_3):
	# Função para delimitar as zonas da lesão
	# Raio central da lesão
	for radius in np.arange(1,20,0.5):
		mask_intersection = np.zeros(data_difference.shape)

		mask_in = functions.sphereMask(data_center, radius)
		mask_out = functions.sphereMask(data_center, radius + 0.5)
		mask_intersection = ~mask_in & mask_out
		median_intersection = np.median(data_difference[mask_intersection == 1])

		if median_intersection >= threshold:
			radius_1 = radius
			break

	print(f"radius_1 = {radius_1}")
	data_zone1 = functions.sphereMask(data_center, radius_1).astype(np.int32)
	functions.saveImage(data_zone1, image, "lesion_zone1")

	#Raio externo da lesão
	for radius in np.arange(radius_1 + 0.5,20,0.5):
		mask_intersection = np.zeros(data_difference.shape)

		mask_in = functions.sphereMask(data_center, radius)
		mask_out = functions.sphereMask(data_center, radius + 0.5)
		mask_intersection = ~mask_in & mask_out
		median_intersection = np.median(data_difference[mask_intersection == 1])

		if median_intersection <= threshold_2:
			radius_2 = radius
			break

	print(f"radius_2 = {radius_2}")
	mask_in = functions.sphereMask(data_center, radius_1)
	mask_out = functions.sphereMask(data_center, radius_2)
	mask_intersection = ~mask_in & mask_out
	
	data_zone2 = mask_intersection.astype(np.int32)
	functions.saveImage(data_zone2, image, "lesion_zone2")
	
	# Edemas adjacentes à lesão
	for radius in np.arange(radius_2,20,0.5):
	  mask_intersection = np.zeros(data_difference.shape)

	  mask_in = functions.sphereMask(data_center, radius)
	  mask_out = functions.sphereMask(data_center, radius + 0.5)
	  mask_intersection = ~mask_in & mask_out
	  percentile_intersection = np.percentile(data_difference[mask_intersection == 1], 80)
	  print(percentile_intersection)

	  if percentile_intersection <= threshold_3:
		  radius_3 = radius + 0.5
		  break

	print(f"radius_3 = {radius_3}")

	mask_edema = np.zeros(data_difference.shape)
	mask_in = functions.sphereMask(data_center, radius_2)
	mask_limit = functions.sphereMask(data_center, radius_3 + 2)

	struct = generate_binary_structure(3,2)
	mask_dilated = binary_dilation(mask_in, structure = struct)
	mask_border = mask_dilated & ~mask_in
	mask_edema = mask_border

	mask_difference = data_difference > threshold_3
	mask_edema = (mask_edema) | (~mask_in & mask_limit & mask_difference)
	print(mask_edema[mask_edema == 1].size)
	
	data_edema = nib.Nifti1Image(functions.connectedComponents(mask_edema).astype(np.int32), image.affine)
	nib.save(data_edema, "lesion_zone3.nii.gz")	
	
	
# Main
## Load files

im_T2 = nib.load("T2_raw_coreg.nii.gz")
im_T2_24 = nib.load("T2_raw_24_coreg_resampled.nii.gz")
im_Contrast = nib.load("Contrast_raw_coreg.nii.gz") # Contrast gm/wm image before procedure
im_Contrast_24 = nib.load("Contrast_raw_coreg_24_resampled.nii.gz") # Contrast gm/wm image after procedure
im_csf = nib.load("5tt_coreg_csf_resampled.nii.gz") # CSF
im_rostral_lh = nib.load("ROI_rostral_lh_Contrast_resampled.nii.gz")
im_rostral_rh = nib.load("ROI_rostral_rh_Contrast_resampled.nii.gz")

print(".Files loaded")

## Extract data from image
data_T2 = im_T2.get_fdata() 
data_T2_24 = im_T2_24.get_fdata() 
data_Contrast = im_Contrast.get_fdata() 
data_Contrast_24 = im_Contrast_24.get_fdata() 
data_csf = im_csf.get_fdata().astype(bool)
data_rostral_lh = im_rostral_lh.get_fdata().astype(bool) 
data_rostral_rh = im_rostral_rh.get_fdata().astype(bool) 
 
print(".Data loaded")

del im_T2, im_T2_24, im_Contrast_24, im_csf, im_rostral_lh, im_rostral_rh # deletar as imagens da memória já que possuem resolução alta 

# Normalização
# data_preNorm = data_Contrast/np.abs(data_Contrast).max()
# data_24Norm = data_Contrast_24/np.abs(data_Contrast_24).max()

# data_preNorm_T2 = data_T2/np.abs(data_T2).max()
# data_24Norm_T2 = data_T2_24/np.abs(data_T2_24).max()

percentile_pre = np.percentile(data_Contrast, 99)
data_preNorm = data_Contrast/percentile_pre
mean_pre = np.mean(data_preNorm[data_csf])
std_pre = np.std(data_preNorm[data_csf])

percentile_24 = np.percentile(data_Contrast_24, 99)
data_24 = data_Contrast_24/percentile_24
mean_24 = np.mean(data_24[data_csf])
std_24 = np.std(data_24[data_csf])

data_24Norm = (data_24 - mean_24) * (std_pre/std_24) + mean_pre

# Diferença entre as imagens
data_difference = (data_24Norm - data_preNorm)**2

# Salvar a subtração das imagens
functions.saveImage(data_difference, im_Contrast, "Contrast_difference")

# Máscara em torno da região rostral do núcleo VL para reduzir o tempo de processamento
mask_sphere = np.zeros(data_Contrast.shape, dtype = bool)

mask_sphere_lh = functions.sphereMask(data_rostral_lh, 15)
mask_sphere_rh = functions.sphereMask(data_rostral_rh, 15)
mask_sphere[mask_sphere_lh | mask_sphere_rh] = True

### Centro da lesão
threshold = 0.4
data_difference[~mask_sphere] = 0
mask_lesion_float_initial, mask_lesion_binary_initial, threshold, threshold_2, threshold_3 = handleLesionmask(data_difference, data_rostral_lh, data_rostral_rh, im_Contrast)
mask_lesion_center = handleLesioncenter(mask_lesion_float_initial, im_Contrast, threshold)
functions.saveImage(mask_lesion_center,im_Contrast,"mask_lesion_center")

### Zonas da lesão
handleZones(data_difference, mask_lesion_center, im_Contrast, threshold, threshold_2, threshold_3)
