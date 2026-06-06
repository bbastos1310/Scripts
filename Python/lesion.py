# Local libraries
import functions

# External libraries
import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt
from scipy.ndimage import correlate, binary_fill_holes, center_of_mass, generate_binary_structure, binary_dilation, binary_erosion, gaussian_filter, binary_closing, binary_opening
from scipy.optimize import least_squares
from skimage.morphology import footprint_rectangle, octahedron, diamond, ball, closing, flood, opening
from skimage.segmentation import find_boundaries, random_walker
from skimage import measure
from skimage import color


def handleLesionmask(data_full, data_rostral_lh, data_rostral_rh, box_sphere, image, image_type):
	print(f"Lesion's mask")
	
	data = data_full[box_sphere].copy()
	
	# Inicializa uma máscara binária com zeros
	mask = np.zeros(np.abs(data).shape, dtype=bool)
	
	if (image_type == "T2"):
		mask[data > 0.2] = 1
	elif (image_type == "WMnull"):
		mask[data > 0.2] = 1
	else:
		print("Tipo de imagem não reconhecido")
		exit()
  
	# Closing
	mask_closed = np.zeros(data.shape)
	kmin = np.where(data != 0)[2].min()
	kmax = np.where(data != 0)[2].max()
	
	for k in range (kmin, kmax + 1):
		mask_closed_temp = np.zeros(mask[:,:,k].shape, dtype=np.uint8)
		mask_closed_temp = closing(mask[:,:,k])
		mask_closed[:,:,k] = mask_closed_temp
		#mask_closed[:,:,k] = functions.connectedComponents(mask_closed_temp)
		
	# Labels
	label_mask, num_labels = measure.label(mask_closed, connectivity=1 ,return_num=True)
	
	# Define o limite mínimo de voxels para manter os labels
	min_voxels = 3000  # Ajuste este valor conforme necessário
	
	# Itera sobre os labels e calcula as propriedades dos objetos rotulados
	labels_filtered = np.zeros_like(label_mask)
	for region in measure.regionprops(label_mask):
		if region.area >= min_voxels:  # area retorna o número de voxels
			labels_filtered[label_mask == region.label] = region.label
	
	# plt.imshow(color.label2rgb(labels_filtered[:,:,262], bg_label=0))
	# plt.savefig("filtered_labels.png")  # Salva como arquivo PNG
	# plt.close
	# print("-Imagem filtered_labels.png salva")
	
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
		lesion_data_float_full = np.zeros(data_full.shape)
		lesion_data_binary_full = np.zeros(data_full.shape)

		lesion_data_float[lesion_coordinates[point][0],lesion_coordinates[point][1],lesion_coordinates[point][2]] = data[lesion_coordinates[point][0],lesion_coordinates[point][1],lesion_coordinates[point][2]]
		lesion_data_binary[lesion_coordinates[point][0],lesion_coordinates[point][1],lesion_coordinates[point][2]] = 1
		lesion_data_float_full[box_sphere] = lesion_data_float
		lesion_data_binary_full[box_sphere] = lesion_data_binary
	
	if (image_type == "T2"): 
		functions.saveImage(lesion_data_float_full.astype(np.uint8), image, "mask_lesion_float_initial_T2")
		functions.saveImage(lesion_data_binary_full.astype(np.uint8), image, "mask_lesion_binary_initial_T2")
		with open("hemisphere.txt", "w") as file_hemisphere:
			file_hemisphere.write(lesion_hemisphere)
		print(f"lesion_hemisphere = {lesion_hemisphere}")
	elif (image_type == "WMnull"): 
		functions.saveImage(lesion_data_float_full.astype(np.uint8), image, "mask_lesion_float_initial_WMnull")
		functions.saveImage(lesion_data_binary_full.astype(np.uint8), image, "mask_lesion_binary_initial_WMnull")
	else:
		print("Tipo de imagem não reconhecido")
	
	return lesion_data_float_full, lesion_data_binary_full.astype(bool)
	
def closeHoles(data, axis):
    mask_closed = np.zeros(data.shape, dtype=bool)
    mask_closed = data.copy()
    dict_axis = axis
    
    for axis in range (len(dict_axis)):
        if dict_axis[axis] == "i":
            try: 
                imin = np.where(mask_closed == 1)[0].min()
                imax = np.where(mask_closed == 1)[0].max()
                for i in range (imin, imax + 1):
                    mask_closed[i,:,:] = binary_fill_holes(mask_closed[i,:,:])
            except ValueError:
                pass
        
        if dict_axis[axis] == "j":
            try:		
                jmin = np.where(mask_closed == 1)[1].min()
                jmax = np.where(mask_closed == 1)[1].max()
                for j in range (jmin, jmax + 1):
                    mask_closed[:,j,:] = binary_fill_holes(mask_closed[:,j,:])
            except ValueError:
                pass
                
        if dict_axis[axis] == "k":
            try:
                kmin = np.where(mask_closed == 1)[2].min()
                kmax = np.where(mask_closed == 1)[2].max()
                for k in range (kmin, kmax + 1):
                    mask_closed[:,:,k] = binary_fill_holes(mask_closed[:,:,k])
            except ValueError:
                pass
                
    return mask_closed


def handleLesionzones(data_lesion_binary, image):
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
	
    for k in range (kmin, kmax + 1):
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
            for j in range(jmin, jmax + 1): #preenchimento de voxels entre os valores máximo e mínimo
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
            #mask_zone1[:,:,k] = mask_closed[:,:,k] & ~data_lesion_binary[:,:,k] & mask_border
        elif num_labels > 1:
            mask_closed[:,:,k] = np.zeros(data_lesion_binary[:,:,k].shape)
			            
    functions.saveImage(functions.connectedComponents(mask_closed).astype(np.uint16), image, "mask_closed")
    return functions.connectedComponents(mask_closed)

# def handleSliceinterval(data, value):
      # kmin = np.where(data == value)[2].min()
      # kmax = np.where(data == value)[2].max()
      
      # k_slice_min = int(np.round(kmin + (kmax - kmin)/5))
      # k_slice_max = int(np.round(kmax - (kmax - kmin)/5))
      
      # return k_slice_min, k_slice_max
	
def bbox_from_mask(mask, pad):
    # mask: bool (i,j,k)
    coords = np.array(np.where(mask))
    i0,j0,k0 = coords.min(axis=1)
    i1,j1,k1 = coords.max(axis=1) + 1
    i0 = max(i0-pad, 0); j0 = max(j0-pad, 0); k0 = max(k0-pad, 0)
    i1 = min(i1+pad, mask.shape[0]); j1 = min(j1+pad, mask.shape[1]); k1 = min(k1+pad, mask.shape[2])
    return (slice(i0,i1), slice(j0,j1), slice(k0,k1))
		
######################################### MAIN #######################################################

#####################  imagens rostral e CSF ######################

im_rostral_lh = nib.load("ROI_rostral_lh_T2.nii.gz")
im_rostral_rh = nib.load("ROI_rostral_rh_T2.nii.gz")
im_csf = nib.load("5tt_coreg_csf_resampled.nii.gz") # CSF

data_rostral_lh = im_rostral_lh.get_fdata().astype(bool) 
data_rostral_rh = im_rostral_rh.get_fdata().astype(bool) 
data_csf = im_csf.get_fdata().astype(bool)

print("Rostral loaded")

# Máscara em torno da região rostral do núcleo VL para reduzir o tempo de processamento
mask_sphere = np.zeros(data_csf.shape, dtype = bool)

mask_sphere_lh = functions.sphereMask(data_rostral_lh, 40)
mask_sphere_rh = functions.sphereMask(data_rostral_rh, 40)
mask_sphere[mask_sphere_lh | mask_sphere_rh] = True

del im_csf, im_rostral_lh, im_rostral_rh

### BOX SPHERE
box_sphere = bbox_from_mask(mask_sphere, pad=0)

#####################  imagem T2 ######################

## Load T2

im_T2 = nib.load("T2_raw_coreg_up.nii.gz") 
im_T2_24 = nib.load("T2_raw_24_coreg_resampled.nii.gz")

## Extract data from image
data_T2 = im_T2.get_fdata() 
data_T2_24 = im_T2_24.get_fdata() 
 
print(".Data loaded")

del im_T2_24

#####################  Normalização e diferença entre imagens T2 ######################

# Normalização (o uso do percentil ao invés do valor máximo é para ignorar possíveis outliers)
percentile_pre = np.percentile(data_T2, 99)
data_preNorm = data_T2/percentile_pre
mean_pre = np.mean(data_preNorm[data_csf])
std_pre = np.std(data_preNorm[data_csf])

percentile_24 = np.percentile(data_T2_24, 99)
data_24 = data_T2_24/percentile_24
mean_24 = np.mean(data_24[data_csf])
std_24 = np.std(data_24[data_csf])

data_24Norm = (data_24 - mean_24) * (std_pre/std_24) + mean_pre

# Diferença entre as imagens
data_difference = (data_24Norm - data_preNorm)**2

# Salvar a subtração das imagens
data_difference[~mask_sphere] = 0
data_difference[box_sphere] = data_difference[box_sphere]/data_difference[box_sphere].max()
functions.saveImage(data_difference, im_T2, "T2_difference")

#####################  Estimativa inicial de voxels da lesão para imagem T2 ######################

### Estimativa do local e de voxels da lesão
mask_lesion_float_initial_T2, mask_lesion_binary_initial_T2 = handleLesionmask(data_difference, data_rostral_lh[box_sphere], data_rostral_rh[box_sphere], box_sphere, im_T2, "T2")

#####################  imagem WMnull ######################

## Load WMnull

im_WMnull = nib.load("Contrast_raw_coreg_resampled.nii.gz") 
im_WMnull_24 = nib.load("Contrast_raw_coreg_24_resampled.nii.gz")

## Extract data from image
data_WMnull = im_WMnull.get_fdata() 
data_WMnull_24 = im_WMnull_24.get_fdata() 
 
print(".Data loaded")

del im_WMnull, im_WMnull_24

#####################  Normalização e diferença entre imagens Wmnull ######################

with open('../Segmentation/hemisphere.txt', 'r', encoding='utf-8') as file_hemisphere:
    hemisphere = file_hemisphere.read()  

if (hemisphere == 'left'):
	box_coord = bbox_from_mask(mask_sphere_lh, pad=0)
	mask_sphere = mask_sphere_lh
elif (hemisphere == 'right'):
	box_coord = bbox_from_mask(mask_sphere_rh, pad=0)
	mask_sphere = mask_sphere_rh
	
# Normalização (o uso do percentil ao invés do valor máximo é para ignorar possíveis outliers)
percentile_pre = np.percentile(data_WMnull, 99)
data_preNorm = data_WMnull/percentile_pre
mean_pre = np.mean(data_preNorm[data_csf])
std_pre = np.std(data_preNorm[data_csf])

percentile_24 = np.percentile(data_WMnull_24, 99)
data_24 = data_WMnull_24/percentile_24
mean_24 = np.mean(data_24[data_csf])
std_24 = np.std(data_24[data_csf])

data_24Norm = (data_24 - mean_24) * (std_pre/std_24) + mean_pre

# Diferença entre as imagens
data_difference = (data_24Norm - data_preNorm)**2

# Salvar a subtração das imagens
data_difference[~mask_sphere] = 0
data_difference[box_sphere] = data_difference[box_sphere]/data_difference[box_sphere].max()
functions.saveImage(data_difference, im_T2, "WMnull_difference")

#####################  Estimativa inicial de voxels da lesão para imagem WMnull ######################

### Estimativa do local e de voxels da lesão
mask_lesion_float_initial_WMnull, mask_lesion_binary_initial_WMnull = handleLesionmask(data_difference, data_rostral_lh[box_sphere], data_rostral_rh[box_sphere], box_sphere, im_T2, "WMnull")

# ####################################### MÓDULO 1 (INÍCIO) ###########################################
# # im_rostral_lh = nib.load("ROI_rostral_lh_T2.nii.gz")
# # im_rostral_rh = nib.load("ROI_rostral_rh_T2.nii.gz")
# im_csf = nib.load("5tt_coreg_csf_resampled.nii.gz") # CSF

# # data_rostral_lh = im_rostral_lh.get_fdata().astype(bool) 
# # data_rostral_rh = im_rostral_rh.get_fdata().astype(bool) 
# data_csf = im_csf.get_fdata().astype(bool)

# print("Rostral loaded")

# im_T2 = nib.load("T2_raw_24_coreg_resampled.nii.gz")
# data_T2_24 = im_T2.get_fdata()

# im_mask_lesion_T2 = nib.load("mask_lesion_binary_initial_T2.nii.gz")
# mask_lesion_binary_initial_T2 = im_mask_lesion_T2.get_fdata().astype(bool)

# im_mask_lesion_WMnull = nib.load("mask_lesion_binary_initial_WMnull.nii.gz")
# mask_lesion_binary_initial_WMnull = im_mask_lesion_WMnull.get_fdata().astype(bool)

# del im_mask_lesion_T2, im_mask_lesion_WMnull

# ####################################### MÓDULO 1 (FINAL) ###########################################

# Máscara em torno da região da lesão para reduzir o tempo de processamento
mask_sphere = np.zeros(data_csf.shape, dtype = bool)
mask_sphere = functions.sphereMask(mask_lesion_binary_initial_T2, 40)

# del im_csf, im_rostral_lh, im_rostral_rh

data_T2_smooth = gaussian_filter(data_T2_24, sigma=1.0)
data_T2_smooth = data_T2_24

# functions.saveImage(data_T2_smooth, im_T2, "T2_smooth")
im_WMnull_24 = nib.load("Contrast_raw_coreg_24_resampled.nii.gz")
data_WMnull = gaussian_filter(im_WMnull_24.get_fdata(), sigma=1.0)

del im_WMnull_24

with open('../Segmentation/hemisphere.txt', 'r', encoding='utf-8') as file_hemisphere:
    hemisphere = file_hemisphere.read()  
print(f"{hemisphere} hemisphere")

### BOX SPHERE
box_sphere = bbox_from_mask(mask_sphere, pad=0)  # delimita uma região para aplicação do algoritmo (reduz processamento)

# ### CROP E MARCADORES	
data_T2_smooth_crop_sphere = data_T2_smooth[box_sphere].astype(np.float32, copy=False)
data_WMnull_crop_sphere = data_WMnull[box_sphere].astype(np.float32, copy=False)

mask_lesion_crop_WMnull = mask_lesion_binary_initial_WMnull[box_sphere]
mask_lesion_crop_T2 = mask_lesion_binary_initial_T2[box_sphere]
mask_sphere_crop = mask_sphere[box_sphere]

###################
markers = np.zeros(data_T2_smooth_crop_sphere.shape, dtype=np.int16)
markers[mask_lesion_crop_T2] = 1    # seleciona os voxels da estimativa inicial da lesão
markers[~mask_sphere_crop] = 2   # seleciona os voxels fora da esfera

mask_markers = np.zeros(data_T2_24.shape, dtype=np.int16)
mask_markers[box_sphere] = markers
functions.saveImage(mask_markers, im_T2, "mask_markers_T2")

######## RANDOM WALKER - PRIMEIRA ESTIMATIVA DA ZONA 1 ##################
tol = 1e-4

mask_open_crop = np.zeros(data_T2_smooth_crop_sphere.shape).astype(bool)
mask_zone1_initial_crop = np.ones(data_T2_smooth_crop_sphere.shape).astype(bool)
dict_axis = ["k"]
size_zone1_initial = 0

print("Primeira estimativa da zona 1")
for beta in range (20, 401, 20): # diminuir o beta deixa menos restritivo, tende a aumentar a área delimitada 
	print(f"testing beta {beta}")
	mask_zone1_initial_crop_temp = np.ones(data_T2_smooth_crop_sphere.shape).astype(bool)
	labels_T2_crop_sphere_temp = random_walker(data_T2_smooth_crop_sphere, markers, beta=beta, mode="cg_mg", tol=tol, return_full_prob=True)
	mask_open_crop = np.where(labels_T2_crop_sphere_temp[0] > 0.9, 1, 0)
	for axis in range(len(dict_axis)):
		mask_closed_crop = np.zeros(data_T2_smooth_crop_sphere.shape).astype(bool)
		mask_closed_crop = closeHoles(mask_open_crop, dict_axis[axis])
		mask_zone1_initial_crop_temp = mask_zone1_initial_crop_temp & mask_closed_crop & ~mask_open_crop
		size_temp = np.count_nonzero(mask_zone1_initial_crop_temp)
		## print(f"size_temp = {size_temp}")
	mask_zone1_initial_crop_temp = functions.connectedComponents(mask_zone1_initial_crop_temp)
	size = np.count_nonzero(mask_zone1_initial_crop_temp)
	## print(f"size = {size}")
	if (size > size_zone1_initial):
		ideal_beta = beta
		size_zone1_initial = size
		print(f"new beta = {beta}")
		mask_zone1_initial_crop = mask_zone1_initial_crop_temp
		labels_T2_crop_sphere = labels_T2_crop_sphere_temp

labels_prob_initial_T2 = np.zeros(data_T2_24.shape)
labels_prob_initial_T2[box_sphere] = labels_T2_crop_sphere[0] 
functions.saveImage(labels_prob_initial_T2 ,im_T2, "labels_prob_initial_T2")

mask_zone1_initial = np.zeros(data_T2_24.shape).astype(bool)
mask_zone1_initial[box_sphere] = mask_zone1_initial_crop
functions.saveImage(mask_zone1_initial.astype(np.uint8) ,im_T2, "mask_zone1_initial")

####################### ESTIMATIVA DA ZONA 2 ###########################
mask_zone2_initial = binary_dilation(mask_zone1_initial[box_sphere], iterations = 4) & ~binary_dilation(mask_zone1_initial[box_sphere], iterations = 3) # voxels mais externos à zona 1 definidos como voxels da zona 2
markers_zone2 = np.zeros(data_T2_smooth_crop_sphere.shape, dtype=np.int16)
markers_zone2[mask_zone2_initial] = 1    # seleciona os voxels da pertencentes à zona 2 externos à zona 1

#### background
markers_zone2[~mask_sphere_crop] = 2   # seleciona os voxels fora da esfera

mask_zone1_initial_sphere = binary_erosion(mask_zone1_initial[box_sphere]) 
markers_zone2[mask_zone1_initial_sphere] = 2 # define voxels centrais da zona 1 como fundo da zona 2
size = 0

print("Primeira estimativa da zona 2")
for beta in range (20, 401, 20): # diminuir o beta deixa menos restritivo, tende a aumentar a área delimitada 
	print(f"testing beta {beta}")
	labels_zone2_crop_sphere_WMnull_temp = random_walker(data_WMnull_crop_sphere, markers_zone2, beta=beta, mode="cg_mg", tol=tol, return_full_prob=True)
	mask_zone2_temp = np.where(labels_zone2_crop_sphere_WMnull_temp[0] > 0.9 , 1, 0).astype(bool)
	size_temp = np.count_nonzero(mask_zone2_temp)
	## print(f"size_temp: {size_temp}")
	if (size_temp > size):
		labels_zone2_crop_sphere_WMnull = labels_zone2_crop_sphere_WMnull_temp
		size = size_temp
		print(f"new_beta = {beta}")
	
labels_zone2_initial = np.zeros(data_T2_24.shape)
# labels_zone2_initial[box_sphere] = labels_zone2_crop_sphere_T2[0]
labels_zone2_initial[box_sphere] = labels_zone2_crop_sphere_WMnull[0]
# labels_zone2_initial[box_sphere] = (labels_zone2_crop_sphere_T2[0] + labels_zone2_crop_sphere_WMnull[0])/2
mask_zone2_temp = np.where(labels_zone2_initial > 0.9, 1, 0).astype(bool) # voxels com probabilidade maior que 90%

functions.saveImage(labels_zone2_initial, im_T2, "labels_zone2_initial") 

# ######################################################## MÓDULO 2 (INÍCIO) ##################################################
# im_zone1_initial = nib.load("mask_zone1_initial.nii.gz")
# mask_zone1_initial = im_zone1_initial.get_fdata()
# mask_zone1_initial_crop = mask_zone1_initial[box_sphere]

# im_labels_zone2_initial = nib.load("labels_zone2_initial.nii.gz")
# labels_zone2_initial = im_labels_zone2_initial.get_fdata()
# mask_zone2_temp = np.where(labels_zone2_initial > 0.9, 1, 0).astype(bool)

# tol = 1e-4
# ideal_beta = 260  #Pat545
# # ideal_beta = 20 #Pat546
# ######################################################## MÓDULO 2 (FINAL) ###################################################3

#################### ESTIMATIVA FINAL DA ZONA 1 ####################################

markers_zone1 = np.zeros(data_T2_smooth_crop_sphere.shape, dtype=np.int16)
markers_zone1[binary_erosion(mask_zone1_initial_crop)] = 1
mask_zone2_temp_crop = mask_zone2_temp[box_sphere]
markers_zone1[binary_erosion(mask_zone2_temp_crop, iterations = 2)] = 2

print("Estimativa final da zona 1")
labels_zone1_crop_sphere_T2 = random_walker(data_T2_smooth_crop_sphere, markers_zone1, beta=ideal_beta, mode="cg_mg", tol=tol, return_full_prob=True)

labels_zone1 = np.zeros(data_T2_24.shape)
labels_zone1[box_sphere] = labels_zone1_crop_sphere_T2[0]
functions.saveImage(labels_zone1, im_T2, "labels_zone1") 

mask_zone1 = np.where(labels_zone1 > 0.1, 1, 0).astype(bool)
mask_zone1 = binary_opening(mask_zone1)
mask_zone1 = functions.connectedComponents(mask_zone1)
mask_zone1 = closeHoles(mask_zone1, ["i", "j", "k"])
functions.saveImage(mask_zone1.astype(np.uint8), im_T2, "mask_zone1") 

#################### ESTIMATIVA FINAL DA ZONA 2 ####################################
markers_zone2 = np.zeros(data_T2_smooth_crop_sphere.shape, dtype=np.int16)
markers_zone2[binary_erosion(mask_zone2_temp_crop, iterations = 2)] = 1
markers_zone2[~mask_sphere_crop] = 2
size = 0

print("Estimativa final da zona 2")
for beta in range (20, 401, 20): # diminuir o beta deixa menos restritivo, tende a aumentar a área delimitada 
	print(f"testing beta {beta}")
	labels_zone2_crop_sphere_T2_temp = random_walker(data_T2_smooth_crop_sphere, markers_zone2, beta=beta, mode="cg_mg", tol=tol, return_full_prob=True)
	mask_zone2_temp = np.where(labels_zone2_crop_sphere_T2_temp[0] > 0.9 , 1, 0).astype(bool)
	size_temp = np.count_nonzero(mask_zone2_temp)
	# print(f"size_temp: {size_temp}")
	if (size_temp > size):
		labels_zone2_crop_sphere_T2 = labels_zone2_crop_sphere_T2_temp
		size = size_temp
		print(f"new_beta = {beta}")

# labels_zone2_crop_sphere_T2 = random_walker(data_T2_smooth_crop_sphere, markers_zone2, beta=ideal_beta, mode="cg_mg", tol=tol, return_full_prob=True)

labels_zone2 = np.zeros(data_T2_24.shape)
labels_zone2[box_sphere] = labels_zone2_crop_sphere_T2[0]
functions.saveImage(labels_zone2, im_T2, "labels_zone2") 

mask_zone2 = np.where(labels_zone2 > 0.9, 1, 0).astype(bool)
mask_zone2 = binary_opening(mask_zone2)
mask_zone2 = functions.connectedComponents(mask_zone2)
mask_zone2 = closeHoles(mask_zone2, ["i","j","k"])
mask_zone2 = mask_zone2 & ~mask_zone1
functions.saveImage(mask_zone2.astype(np.uint8), im_T2, "mask_zone2") 









