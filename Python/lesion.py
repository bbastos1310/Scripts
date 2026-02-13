# Local libraries
import functions
import roi_definition as roi

# External libraries
import nibabel as nib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.ndimage import correlate, binary_fill_holes, center_of_mass, generate_binary_structure, binary_dilation, binary_erosion
from scipy.optimize import least_squares
from skimage.morphology import footprint_rectangle, diamond, ball, closing, flood
from skimage.segmentation import find_boundaries
from skimage import measure
from skimage import color
from joblib import Parallel, delayed
import os

def handleLesionmask(data, data_rostral_lh, data_rostral_rh, Contrast):
	print(f"Lesion's mask")
	
	# Inicializa uma máscara binária com zeros
	mask = np.zeros(np.abs(data).shape, dtype=bool)
	
	mask[data > 0.1] = 1
  
	# Closing
	mask_closed = np.zeros(data.shape)
	kmin = np.where(data != 0)[2].min()
	kmax = np.where(data != 0)[2].max()
	
	for k in range (kmin, kmax):
		mask_closed_temp = np.zeros(mask[:,:,k].shape, dtype=np.uint8)
		mask_closed_temp = closing(mask[:,:,k])
		mask_closed[:,:,k] = mask_closed_temp
		#mask_closed[:,:,k] = functions.connectedComponents(mask_closed_temp)
	
	functions.saveImage(mask_closed.astype(np.uint8), Contrast, "mask_closed")
	
	# Labels
	label_mask, num_labels = measure.label(mask_closed, connectivity=1 ,return_num=True)
	
	# Define o limite mínimo de voxels para manter os labels
	min_voxels = 2000  # Ajuste este valor conforme necessário
	
	# Itera sobre os labels e calcula as propriedades dos objetos rotulados
	labels_filtered = np.zeros_like(label_mask)
	for region in measure.regionprops(label_mask):
		if region.area >= min_voxels:  # area retorna o número de voxels
			labels_filtered[label_mask == region.label] = region.label
	
	plt.imshow(color.label2rgb(labels_filtered[:,:,265], bg_label=0))
	plt.savefig("filtered_labels.png")  # Salva como arquivo PNG
	plt.close
	print("-Imagem filtered_labels.png salva")
	
	# Lesion selection
	closest_label = None
	min_distance = float('inf')
	lesion_hemisphere = "left"
	center_rostral_lh = center_of_mass(data_rostral_lh)
	center_rostral_rh = center_of_mass(data_rostral_rh)
		
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
	
	lesion_data_float = functions.connectedComponents(lesion_data_float)
	lesion_data_binary = binary_dilation(functions.connectedComponents(lesion_data_binary))
	
	for point in range(num_points):
	  lesion_data_float[lesion_coordinates[point][0],lesion_coordinates[point][1],lesion_coordinates[point][2]] = data[lesion_coordinates[point][0],lesion_coordinates[point][1],lesion_coordinates[point][2]]
	  lesion_data_binary[lesion_coordinates[point][0],lesion_coordinates[point][1],lesion_coordinates[point][2]] = 1
	functions.saveImage(lesion_data_float.astype(np.uint8), Contrast, "mask_lesion_float_initial")
	functions.saveImage(lesion_data_binary.astype(np.uint8), Contrast, "mask_lesion_binary_initial")
	
	with open("hemisphere.txt", "w") as file_hemisphere:
		file_hemisphere.write(lesion_hemisphere)
	
	print(f"lesion_hemisphere = {lesion_hemisphere}")
	
	return lesion_data_float, lesion_data_binary.astype(bool)


def handleLesionzones(data_lesion_binary, data_T2_24, data_difference, image):
    mask_center = np.zeros(data_lesion_binary.shape, dtype=bool)
    mask_closed = np.zeros(data_lesion_binary.shape, dtype=bool)
    mask_zone1 = np.zeros(data_lesion_binary.shape, dtype=bool)
    mask_zone2 = np.zeros(data_lesion_binary.shape, dtype=bool)
    mask_zone3 = np.zeros(data_lesion_binary.shape, dtype=bool)
    data_correlate = np.zeros(data_lesion_binary.shape, dtype=np.uint16)
    kernel = np.array([[1,2,4,8,16,32,64]]) # kernel para preenchimento de 2 ou 3 espaços vazios na linha ou na coluna
    kernel_border = np.array([[1,2,4],[8,16,32],[64,128,256]]) # kernel para verificar se o voxel é interno
	
    mask_closed[data_lesion_binary] = 1
	
	# Preenchimento das zonas 1 e 2
    kmin = np.where(data_lesion_binary == 1)[2].min()
    kmax = np.where(data_lesion_binary == 1)[2].max()
	
    for k in range (kmin, kmax):
        mask_correlate = np.zeros(data_lesion_binary[:,:,k].shape, dtype=bool)
        mask_border = np.zeros(data_lesion_binary[:,:,k].shape, dtype=bool)
        data_correlate[:,:,k] = correlate(data_lesion_binary[:,:,k].astype(np.uint16), kernel, mode = 'constant')
        mask_correlate = np.isin(data_correlate[:,:,k], (17, 18, 19, 20, 21, 22, 23, 35, 36, 37, 38, 39, 49, 50, 51, 52, 53, 54, 55, 68, 69, 70, 71, 81, 82, 83, 84, 85, 86, 87, 98, 99, 100, 101, 102, 103, 113, 114, 115, 117, 118, 119))
        data_lesion_binary[:,:,k] = data_lesion_binary[:,:,k] | mask_correlate
        data_correlate[:,:,k] = correlate(data_lesion_binary[:,:,k].astype(np.uint16), kernel.T, mode = 'constant')
        mask_correlate = np.isin(data_correlate[:,:,k], (17, 18, 19, 20, 21, 22, 23, 35, 36, 37, 38, 39, 49, 50, 51, 52, 53, 54, 55, 68, 69, 70, 71, 81, 82, 83, 84, 85, 86, 87, 98, 99, 100, 101, 102, 103, 113, 114, 115, 117, 118, 119))
        data_lesion_binary[:,:,k] = data_lesion_binary[:,:,k] | mask_correlate
        label_mask, num_labels = measure.label(binary_fill_holes(data_lesion_binary[:,:,k]), connectivity=2 ,return_num=True)
        if num_labels == 1:
            #mask_correlate = np.zeros(data_lesion_binary[:,:,k].shape, dtype=bool)
            jmin = np.where(data_lesion_binary[:,:,k] == 1)[1].min()
            jmax = np.where(data_lesion_binary[:,:,k] == 1)[1].max()
            for j in range(jmin, jmax): #preenchimento de voxels entre os valores máximo e mínimo
	            try:
		            i_min = np.where(data_lesion_binary[:,j,k] == 1)[0].min()
		            i_max = np.where(data_lesion_binary[:,j,k] == 1)[0].max()
		            mask_closed[i_min:i_max,j,k] = 1
	            except ValueError:
	                pass
            data_correlate[:,:,k] = correlate(mask_closed[:,:,k].astype(np.uint16), kernel, mode = 'constant')
            mask_correlate = np.isin(data_correlate[:,:,k], (17, 18, 19, 20, 21, 22, 23, 35, 36, 37, 38, 39, 49, 50, 51, 52, 53, 54, 55, 68, 69, 70, 71, 81, 82, 83, 84, 85, 86, 87, 98, 99, 100, 101, 102, 103, 113, 114, 115, 117, 118, 119))
            mask_closed[:,:,k] = mask_closed[:,:,k] | mask_correlate
            data_correlate[:,:,k] = correlate(mask_closed[:,:,k].astype(np.uint16), kernel.T, mode = 'constant')
            mask_correlate = np.isin(data_correlate[:,:,k], (17, 18, 19, 20, 21, 22, 23, 35, 36, 37, 38, 39, 49, 50, 51, 52, 53, 54, 55, 68, 69, 70, 71, 81, 82, 83, 84, 85, 86, 87, 98, 99, 100, 101, 102, 103, 113, 114, 115, 117, 118, 119))
            mask_closed[:,:,k] = mask_closed[:,:,k] | mask_correlate            
            mask_closed[:,:,k] = binary_fill_holes(mask_closed[:,:,k])
            data_correlate[:,:,k] = correlate(mask_closed[:,:,k].astype(np.uint16), kernel_border, mode = 'constant')
            mask_border[data_correlate[:,:,k] == 511] = 1
            mask_zone1[:,:,k] = mask_closed[:,:,k] & ~data_lesion_binary[:,:,k] & mask_border
            
    functions.saveImage(mask_closed.astype(np.uint16), image, "mask_closed")
    functions.saveImage(data_lesion_binary.astype(np.uint16), image, "data_lesion_binary")
    #functions.saveImage(data_correlate.astype(np.uint16), image, "mask_correlate")
    
    # Stats
    print(f"min = {np.min(data_difference[mask_closed])}")
    print(f"percentil_5 = {np.percentile(data_difference[mask_closed], 5)}")
    print(f"percentil_10 = {np.percentile(data_difference[mask_closed], 10)}")
    print(f"percentil_15 = {np.percentile(data_difference[mask_closed], 15)}")
    print(f"percentil_20 = {np.percentile(data_difference[mask_closed], 20)}")
    
    s = pd.Series(data_difference[mask_closed])
    print(s.describe())
    
    threshold = np.percentile(data_difference[mask_closed], 15)
            
    mask_zone1[data_difference > threshold] = 0		
    mask_zone1 = functions.connectedComponents(binary_fill_holes(mask_zone1))
    mask_zone2 = mask_closed & ~mask_zone1
    mask_zone2 = functions.connectedComponents(mask_zone2)
		
    functions.saveImage(mask_zone1.astype(np.uint8), image, "mask_zone1")
    functions.saveImage(mask_zone2.astype(np.uint8), image, "mask_zone2")
    
    print(f"zone1 = {mask_zone1[mask_zone1].size * 0.3**3}")
    print(f"zone2 = {mask_zone2[mask_zone2].size * 0.3**3}")
    
    # Máscara do centro da lesão
		
    percentile_2 = np.percentile(data_T2_24[mask_zone1], 2)
    mask_center = (data_T2_24 < percentile_2) & (mask_zone1 == 1)
    mask_center = functions.connectedComponents(mask_center)
	#print(f"Percentil = {percentile_2}")
    functions.saveImage(mask_center.astype(np.uint8), image, "mask_center")
    
    # Preenchimento da zona 3
    mask = np.zeros(data_difference.shape, dtype=bool)
    mask_percentile = np.zeros(data_difference.shape, dtype=bool)
    mask_distance = np.zeros(data_difference.shape, dtype=bool)
    
    mask_percentile = binary_dilation(mask_closed, iterations = 3) & ~mask_closed
    
    print(f"percentil_50 = {np.percentile(data_difference[mask_percentile], 25)}")
    threshold_zone3 = np.percentile(data_difference[mask_percentile], 25)
	
    mask[data_difference > threshold_zone3] = 1
    mask[:,:,:kmin - 5] = 0
    mask[:,:,kmax + 4:] = 0
    mask_distance = functions.sphereMask(mask_center, 30)
    mask_zone3 = np.zeros(data_difference.shape)
    mask_zone3 = functions.connectedComponents(mask)    
    mask_zone3[mask_zone1 | mask_zone2 | ~mask_distance] = 0
    functions.saveImage(mask_zone3.astype(np.uint8), image, "mask_zone3")
	
	
	
	
	# for k in range(data_lesion_binary.shape[2]):
	  # contornos = measure.find_contours(np.abs(data_lesion_binary[:,:,k]), level=0.5)
	  # # Itera sobre cada contorno encontrado
	  # for contorno in contornos:
		  # # Obter as coordenadas dos contornos
		  # i = contorno[:, 0].astype(int)
		  # j = contorno[:, 1].astype(int)
		  # mask_contour[i, j, k] = 1
	  # mask_label[:,:,k], num_labels = measure.label(mask_contour[:,:,k], connectivity=2 ,return_num=True)
	  
	
		
	
	# # Preenchimento da zona 2
	# kmin = np.where(mask_label == 1)[2].min()
	# kmax = np.where(mask_label == 1)[2].max()
	# max_area = 0
	
	# for k in range (kmin, kmax):
		# mask_left = np.zeros(data_lesion_binary[:,:,k].shape, dtype=bool)
		# mask_right = np.zeros(data_lesion_binary[:,:,k].shape, dtype=bool)
		# mask_temp = np.zeros(data_lesion_binary[:,:,k].shape, dtype=np.uint8)
		# points = np.where(mask_label[:,:,k] == 1)
		# len_contour = points[0].size
		# for n in range (0, len_contour):
			# i = points[0][n]
			# j = points[1][n]
			# mask_left[:i,j] = 1
			# mask_right[i:,j] = 1
		# mask_temp[mask_left & mask_right] = 1
		# mask_filled[:,:,k] = mask_temp
	
	# # points = np.argwhere(mask_label[:,:,center_k] == 2)
	
	# # initial_values = np.array([1])
	# # res = least_squares(handleResidualsradius, initial_values, args=(points,center_i, center_j))
	# # radius_in = res.x[0]
	
	# # Preenchimento da zona 1
	# kmin = np.where(mask_label == 2)[2].min()
	# kmax = np.where(mask_label == 2)[2].max()
		
	# for k in range (kmin, kmax):
		# mask_left = np.zeros(data_lesion_binary[:,:,k].shape, dtype=bool)
		# mask_right = np.zeros(data_lesion_binary[:,:,k].shape, dtype=bool)
		# mask_temp = np.zeros(data_lesion_binary[:,:,k].shape, dtype=np.uint8)
		# points = np.where(mask_label[:,:,k] == 2)
		# len_contour = points[0].size
		# for n in range (0, len_contour):
			# i = points[0][n]
			# j = points[1][n]
			# mask_left[:i,j] = 1
			# mask_right[i:,j] = 1
		# mask_temp[mask_left & mask_right] = 1
		# mask_filled[:,:,k] = mask_filled[:,:,k] + mask_temp
		
	# kmin = np.where(mask_label > 2)[2].min()
	# kmax = np.where(mask_label > 2)[2].max()
		
	# for k in range (kmin, kmax):
		# mask_left = np.zeros(data_lesion_binary[:,:,k].shape, dtype=bool)
		# mask_right = np.zeros(data_lesion_binary[:,:,k].shape, dtype=bool)
		# mask_temp = np.zeros(data_lesion_binary[:,:,k].shape, dtype=np.uint8)
		# points = np.where(mask_label[:,:,k] > 2)
		# len_contour = points[0].size
		# for n in range (0, len_contour):
			# i = points[0][n]
			# j = points[1][n]
			# mask_left[:i,j] = 1
			# mask_right[i:,j] = 1
		# mask_temp[mask_left & mask_right] = 1
		# mask_filled[:,:,k] = mask_filled[:,:,k] + mask_temp
	
	# mask_zone1 = functions.connectedComponents(mask_filled == 2)
	# mask_zone2 = functions.connectedComponents(mask_filled == 1)
		
	# functions.saveImage(mask_label, image, "mask_label")
	# functions.saveImage(mask_zone1.astype(np.uint8), image, "mask_zone1")
	# functions.saveImage(mask_zone2.astype(np.uint8), image, "mask_zone2")
		
##### MAIN
## Load files

im_Contrast = nib.load("T2_raw_coreg_up.nii.gz") # Contrast gm/wm image before procedure
im_Contrast_24 = nib.load("T2_raw_24_coreg_resampled.nii.gz") # Contrast gm/wm image after procedure
im_T2_24 = nib.load("T2_raw_24_coreg_resampled.nii.gz")
im_csf = nib.load("5tt_coreg_csf_resampled.nii.gz") # CSF
im_rostral_lh = nib.load("ROI_rostral_lh_T2.nii.gz")
im_rostral_rh = nib.load("ROI_rostral_rh_T2.nii.gz")

print(".Files loaded")

## Extract data from image
data_Contrast = im_Contrast.get_fdata() 
data_Contrast_24 = im_Contrast_24.get_fdata() 
data_T2_24 = im_T2_24.get_fdata() 
data_csf = im_csf.get_fdata().astype(bool)
data_rostral_lh = im_rostral_lh.get_fdata().astype(bool) 
data_rostral_rh = im_rostral_rh.get_fdata().astype(bool) 
 
print(".Data loaded")

del im_Contrast_24, im_T2_24, im_csf, im_rostral_lh, im_rostral_rh # deletar as imagens da memória já que possuem resolução alta 

# Normalização (o uso do percentil ao invés do valor máximo é para ignorar possíveis outliers)
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

mask_sphere_lh = functions.sphereMask(data_rostral_lh, 40)
mask_sphere_rh = functions.sphereMask(data_rostral_rh, 40)
mask_sphere[mask_sphere_lh | mask_sphere_rh] = True

### Centro da lesão
data_difference[~mask_sphere] = 0
mask_lesion_float_initial, mask_lesion_binary_initial = handleLesionmask(data_difference, data_rostral_lh, data_rostral_rh, im_Contrast)
handleLesionzones(mask_lesion_binary_initial, data_T2_24, data_difference, im_Contrast)

# ####################### TESTE

# im_Contrast = nib.load("Contrast_difference.nii.gz")
# im_lesion = nib.load("mask_lesion_binary_initial.nii.gz")
# im_T2_24 = nib.load("T2_raw_24_coreg_resampled.nii.gz")
# im_rostral_lh = nib.load("ROI_rostral_lh_T2.nii.gz")
# im_rostral_rh = nib.load("ROI_rostral_rh_T2.nii.gz")
# print(".Files loaded")

# data_difference = im_Contrast.get_fdata() 
# mask_lesion_binary_initial = im_lesion.get_fdata().astype(bool)  
# data_T2_24 = im_T2_24.get_fdata() 
# data_rostral_lh = im_rostral_lh.get_fdata().astype(bool) 
# data_rostral_rh = im_rostral_rh.get_fdata().astype(bool) 
# print(".Data loaded")

# # Máscara em torno da região rostral do núcleo VL para reduzir o tempo de processamento
# mask_sphere = np.zeros(data_difference.shape, dtype = bool)

# mask_sphere_lh = functions.sphereMask(data_rostral_lh, 40)
# mask_sphere_rh = functions.sphereMask(data_rostral_rh, 40)
# mask_sphere[mask_sphere_lh | mask_sphere_rh] = True

# ### Centro da lesão
# data_difference[~mask_sphere] = 0
# #mask_lesion_float_initial, mask_lesion_binary_initial = handleLesionmask(data_difference, data_rostral_lh, data_rostral_rh, im_Contrast)
# handleLesionzones(mask_lesion_binary_initial, data_T2_24, data_difference, im_Contrast)
# # print(f"mean_left = {np.mean(data_difference[mask_sphere_lh])}, std_left = {np.std(data_difference[mask_sphere_lh])}")
# # print(f"mean_right = {np.mean(data_difference[mask_sphere_rh])}, std_right = {np.std(data_difference[mask_sphere_rh])}")



