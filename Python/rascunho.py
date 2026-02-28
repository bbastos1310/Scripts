# Local libraries
import functions

# External libraries
import nibabel as nib
import numpy as np
from scipy.ndimage import correlate, binary_fill_holes, center_of_mass, generate_binary_structure, binary_dilation, binary_erosion, gaussian_filter, binary_closing
from scipy.optimize import least_squares
from skimage.morphology import footprint_rectangle, diamond, ball, closing, flood
from skimage.segmentation import find_boundaries, random_walker
from skimage import measure
from skimage import color


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
		
	# Labels
	label_mask, num_labels = measure.label(mask_closed, connectivity=1 ,return_num=True)
	
	# Define o limite mínimo de voxels para manter os labels
	min_voxels = 2000  # Ajuste este valor conforme necessário
	
	# Itera sobre os labels e calcula as propriedades dos objetos rotulados
	labels_filtered = np.zeros_like(label_mask)
	for region in measure.regionprops(label_mask):
		if region.area >= min_voxels:  # area retorna o número de voxels
			labels_filtered[label_mask == region.label] = region.label
	
	# plt.imshow(color.label2rgb(labels_filtered[:,:,265], bg_label=0))
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
	  lesion_data_float[lesion_coordinates[point][0],lesion_coordinates[point][1],lesion_coordinates[point][2]] = data[lesion_coordinates[point][0],lesion_coordinates[point][1],lesion_coordinates[point][2]]
	  lesion_data_binary[lesion_coordinates[point][0],lesion_coordinates[point][1],lesion_coordinates[point][2]] = 1
	functions.saveImage(lesion_data_float.astype(np.uint8), Contrast, "mask_lesion_float_initial")
	functions.saveImage(lesion_data_binary.astype(np.uint8), Contrast, "mask_lesion_binary_initial")
	
	with open("hemisphere.txt", "w") as file_hemisphere:
		file_hemisphere.write(lesion_hemisphere)
	
	print(f"lesion_hemisphere = {lesion_hemisphere}")
	
	return lesion_data_float, lesion_data_binary.astype(bool)
	
def closeHoles(data):
    mask_closed = np.zeros(data.shape, dtype=bool)
    kmin = np.where(data == 1)[2].min()
    kmax = np.where(data == 1)[2].max()
    
    for k in range (kmin, kmax):
        jmin = np.where(data[:,:,k] == 1)[1].min()
        jmax = np.where(data[:,:,k] == 1)[1].max()
        for j in range(jmin, jmax): #preenchimento de voxels entre os valores máximo e mínimo
            try:
                i_min = np.where(data[:,j,k] == 1)[0].min()
                i_max = np.where(data[:,j,k] == 1)[0].max()
                mask_closed[i_min:i_max,j,k] = 1
            except ValueError:
                pass
    return mask_closed


# def handleLesionzones(data_lesion_binary, data_T2_24, data_difference, image):
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
            #mask_zone1[:,:,k] = mask_closed[:,:,k] & ~data_lesion_binary[:,:,k] & mask_border
        elif num_labels > 1:
            mask_closed[:,:,k] = np.zeros(data_lesion_binary[:,:,k].shape)
			            
    functions.saveImage(functions.connectedComponents(mask_closed).astype(np.uint16), image, "mask_closed")
    return functions.connectedComponents(mask_closed)
    
	
def bbox_from_mask(mask, pad):
    # mask: bool (z,y,x)
    coords = np.array(np.where(mask))
    z0,y0,x0 = coords.min(axis=1)
    z1,y1,x1 = coords.max(axis=1) + 1
    z0 = max(z0-pad, 0); y0 = max(y0-pad, 0); x0 = max(x0-pad, 0)
    z1 = min(z1+pad, mask.shape[0]); y1 = min(y1+pad, mask.shape[1]); x1 = min(x1+pad, mask.shape[2])
    return (slice(z0,z1), slice(y0,y1), slice(x0,x1))
		
######################################### MAIN #######################################################

## Load Rostral e CSF

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

## Load T2

im_T2 = nib.load("T2_raw_coreg_up.nii.gz") 
im_T2_24 = nib.load("T2_raw_24_coreg_resampled.nii.gz")

## Extract data from image
data_T2 = im_T2.get_fdata() 
data_T2_24 = im_T2_24.get_fdata() 
data_T2_24 = im_T2_24.get_fdata() 
 
print(".Data loaded")

del im_T2_24

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
functions.saveImage(data_difference, im_T2, "T2_difference")

### Estimativa do local e de voxels da lesão
data_difference[~mask_sphere] = 0
mask_lesion_float_initial, mask_lesion_binary_initial = handleLesionmask(data_difference, data_rostral_lh, data_rostral_rh, im_T2)

data_T2_smooth = gaussian_filter(data_T2_24, sigma=1.0)

im_WMnull = nib.load("Contrast_raw_coreg_24_resampled.nii.gz")
data_WMnull = gaussian_filter(im_WMnull.get_fdata(), sigma=1.0)

del im_WMnull

mask_roi = handleLesionzones(mask_lesion_binary_initial, im_T2)

with open('../Segmentation/hemisphere.txt', 'r', encoding='utf-8') as file_hemisphere:
    hemisphere = file_hemisphere.read()  
print(f"{hemisphere} hemisphere")

if (hemisphere == 'left'):
	data_T2_smooth[~mask_sphere_lh] = 0
	box_coord = bbox_from_mask(mask_sphere_lh, pad=0)
	mask_sphere = mask_sphere_lh
elif (hemisphere == 'right'):
	data_T2_smooth[~mask_sphere_rh] = 0
	box_coord = bbox_from_mask(mask_sphere_rh, pad=0)
	mask_sphere = mask_sphere_rh

### BOX SPHERE
box_sphere = bbox_from_mask(mask_sphere, pad=0)
	
kmin = np.where(mask_roi == 1)[2].min()
kmax = np.where(mask_roi == 1)[2].max()

mask_bg = binary_dilation(mask_roi, iterations = 5) & ~binary_dilation(mask_roi, iterations = 3)
mask_bg[:,:,:kmin] = 0
mask_bg[:,:,kmax:] = 0

# functions.saveImage(mask_bg.astype(np.uint8), im_T2, "mask_teste")

### CROP E MARKERS
data_T2_smooth_crop = data_T2_smooth[box_sphere].astype(np.float32, copy=False)
mask_lesion_crop = mask_lesion_binary_initial[box_sphere]
mask_bg_crop = mask_bg[box_sphere]
mask_sphere_crop = mask_sphere[box_sphere]

markers = np.zeros(data_T2_smooth_crop.shape, dtype=np.int16)
markers[mask_lesion_crop] = 1
markers[~mask_sphere_crop] = 2
markers[mask_bg_crop] = 2

# functions.saveImage(markers, im_T2, "markers")

### RANDOM WALKER T2
beta = 100 # diminuir o beta deixa menos restritivo, tente a aumentar a área delimitada da zona 1
labels_T2_crop = random_walker(data_T2_smooth_crop, markers, beta=beta, mode="cg_mg", tol=1e-6, return_full_prob=True)

labels_T2 = np.zeros(data_T2_24.shape)
labels_T2[box_sphere] = labels_T2_crop[0]
# functions.saveImage(labels_T2, im_T2, "teste_random_T2")
# functions.saveImage(mask_zone2_T2.astype(np.uint8), im_T2, "mask_zone2_T2")

### RANDOM WALKER WMnull
data_WMnull_crop = data_WMnull[box_sphere].astype(np.float32, copy=False)
labels_WMnull_crop = random_walker(data_WMnull_crop, markers, beta=beta, mode="cg_mg", tol=1e-6, return_full_prob=True)

### ESTIMATIVA INICIAL ZONA 2
labels_WMnull = np.zeros(data_T2_24.shape)
labels_WMnull[box_sphere] = labels_WMnull_crop[0]
# functions.saveImage(labels_WMnull, im_T2, "teste_random_WMnull")
# functions.saveImage(mask_zone2_WMnull.astype(np.uint8), im_T2, "mask_zone2_WMnull")

labels_sum = labels_T2 + labels_WMnull
functions.saveImage(labels_sum ,im_T2, "labels_sum")

### ESTIMATIVA INICIAL ZONA 1
mask_zone1_initial = np.zeros(data_T2_24.shape)
k_slice = int(np.round((kmin + kmax)/2))
mask_zone1_initial[:,:,k_slice] = mask_roi[:,:,k_slice] & ~mask_lesion_binary_initial[:,:,k_slice]

### CROP
box_zone2 = bbox_from_mask(labels_sum, pad=3)
data_WMnull_crop = data_WMnull[box_zone2].astype(np.float32, copy=False)
labels_sum_crop = labels_sum[box_zone2]
mask_zone1_initial_crop = mask_zone1_initial[box_zone2]

### MARKER ZONA 1
markers_2 = np.zeros(data_WMnull_crop.shape, dtype=np.int16)
markers_2 = np.where(labels_sum_crop > 1.99, 2, 0)
markers_2 = np.where(mask_zone1_initial_crop == 1, 1, markers_2)

# mask_marker = np.zeros(data_T2_24.shape)
# mask_marker[box_zone2] = markers_2
# functions.saveImage(mask_marker, im_T2, "markers_2")

### RANDOM WALKER ZONA 1
labels_zone1_crop = random_walker(data_WMnull_crop, markers_2, beta=beta, mode="cg_mg", tol=1e-6, return_full_prob=True)

labels_zone1 = np.zeros(data_T2_24.shape)
labels_zone1[box_zone2] = labels_zone1_crop[0]
mask_zone1 = binary_closing(np.where(labels_zone1 > 0.1, 1, 0).astype(bool), structure=ball(3))
functions.saveImage(functions.connectedComponents(mask_zone1).astype(np.uint8), im_T2, "mask_zone1")
print(np.count_nonzero(mask_zone1))

mask_zone2_closed = closeHoles(labels_sum > 0.9)
mask_zone2 = functions.connectedComponents(mask_zone2_closed & ~mask_zone1)
functions.saveImage(mask_zone2.astype(np.uint8), im_T2, "mask_zone2")
print(np.count_nonzero(mask_zone2))

# ####################################### TESTE ###########################################
# im_rostral_lh = nib.load("ROI_rostral_lh_T2.nii.gz")
# im_rostral_rh = nib.load("ROI_rostral_rh_T2.nii.gz")
# im_csf = nib.load("5tt_coreg_csf_resampled.nii.gz") # CSF

# data_rostral_lh = im_rostral_lh.get_fdata().astype(bool) 
# data_rostral_rh = im_rostral_rh.get_fdata().astype(bool) 
# data_csf = im_csf.get_fdata().astype(bool)

# print("Rostral loaded")

# # Máscara em torno da região rostral do núcleo VL para reduzir o tempo de processamento
# mask_sphere = np.zeros(data_csf.shape, dtype = bool)

# mask_sphere_lh = functions.sphereMask(data_rostral_lh, 40)
# mask_sphere_rh = functions.sphereMask(data_rostral_rh, 40)
# mask_sphere[mask_sphere_lh | mask_sphere_rh] = True

# del im_csf, im_rostral_lh, im_rostral_rh

# im_T2 = nib.load("T2_raw_24_coreg_resampled.nii.gz")
# data_T2_24 = im_T2.get_fdata()

# im_mask_lesion = nib.load("mask_lesion_binary_initial.nii.gz")
# mask_lesion_binary_initial = im_mask_lesion.get_fdata().astype(bool)

# del im_mask_lesion

# data_T2_smooth = gaussian_filter(data_T2_24, sigma=1.0)
# # data_T2_smooth = data_T2_24

# im_WMnull = nib.load("Contrast_raw_coreg_24_resampled.nii.gz")
# data_WMnull = gaussian_filter(im_WMnull.get_fdata(), sigma=1.0)
# # data_WMnull = im_WMnull.get_fdata()

# del im_WMnull

# mask_roi = handleLesionzones(mask_lesion_binary_initial, im_T2)

# with open('../Segmentation/hemisphere.txt', 'r', encoding='utf-8') as file_hemisphere:
    # hemisphere = file_hemisphere.read()  
# print(f"{hemisphere} hemisphere")

# if (hemisphere == 'left'):
	# data_T2_smooth[~mask_sphere_lh] = 0
	# box_coord = bbox_from_mask(mask_sphere_lh, pad=0)
	# mask_sphere = mask_sphere_lh
# elif (hemisphere == 'right'):
	# data_T2_smooth[~mask_sphere_rh] = 0
	# box_coord = bbox_from_mask(mask_sphere_rh, pad=0)
	# mask_sphere = mask_sphere_rh

# ### BOX SPHERE
# box_sphere = bbox_from_mask(mask_sphere, pad=0)
	
# kmin = np.where(mask_roi == 1)[2].min()
# kmax = np.where(mask_roi == 1)[2].max()

# mask_bg = binary_dilation(mask_roi, iterations = 5) & ~binary_dilation(mask_roi, iterations = 3)
# mask_bg[:,:,:kmin] = 0
# mask_bg[:,:,kmax:] = 0

# # functions.saveImage(mask_bg.astype(np.uint8), im_T2, "mask_teste")

# ### CROP E MARKERS
# data_T2_smooth_crop = data_T2_smooth[box_sphere].astype(np.float32, copy=False)
# mask_lesion_crop = mask_lesion_binary_initial[box_sphere]
# mask_bg_crop = mask_bg[box_sphere]
# mask_sphere_crop = mask_sphere[box_sphere]

# markers = np.zeros(data_T2_smooth_crop.shape, dtype=np.int16)
# markers[mask_lesion_crop] = 1
# markers[~mask_sphere_crop] = 2
# markers[mask_bg_crop] = 2

# # functions.saveImage(markers, im_T2, "markers")

# ### RANDOM WALKER T2
# beta = 100 # diminuir o beta deixa menos restritivo, tente a aumentar a área delimitada da zona 1
# labels_T2_crop = random_walker(data_T2_smooth_crop, markers, beta=beta, mode="cg_mg", tol=1e-6, return_full_prob=True)

# labels_T2 = np.zeros(data_T2_24.shape)
# labels_T2[box_sphere] = labels_T2_crop[0]
# # functions.saveImage(labels_T2, im_T2, "teste_random_T2")
# # functions.saveImage(mask_zone2_T2.astype(np.uint8), im_T2, "mask_zone2_T2")

# ### RANDOM WALKER WMnull
# data_WMnull_crop = data_WMnull[box_sphere].astype(np.float32, copy=False)
# labels_WMnull_crop = random_walker(data_WMnull_crop, markers, beta=beta, mode="cg_mg", tol=1e-6, return_full_prob=True)

# ### ESTIMATIVA INICIAL ZONA 2
# labels_WMnull = np.zeros(data_T2_24.shape)
# labels_WMnull[box_sphere] = labels_WMnull_crop[0]
# # functions.saveImage(labels_WMnull, im_T2, "teste_random_WMnull")
# # functions.saveImage(mask_zone2_WMnull.astype(np.uint8), im_T2, "mask_zone2_WMnull")

# labels_sum = labels_T2 + labels_WMnull
# functions.saveImage(labels_sum ,im_T2, "labels_sum")

# ### ESTIMATIVA INICIAL ZONA 1
# mask_zone1_initial = np.zeros(data_T2_24.shape)
# k_slice = int(np.round((kmin + kmax)/2))
# mask_zone1_initial[:,:,k_slice] = mask_roi[:,:,k_slice] & ~mask_lesion_binary_initial[:,:,k_slice]

# ### CROP
# box_zone2 = bbox_from_mask(labels_sum, pad=3)
# data_WMnull_crop = data_WMnull[box_zone2].astype(np.float32, copy=False)
# labels_sum_crop = labels_sum[box_zone2]
# mask_zone1_initial_crop = mask_zone1_initial[box_zone2]

# ### MARKER ZONA 1
# markers_2 = np.zeros(data_WMnull_crop.shape, dtype=np.int16)
# markers_2 = np.where(labels_sum_crop > 1.99, 2, 0)
# markers_2 = np.where(mask_zone1_initial_crop == 1, 1, markers_2)

# # mask_marker = np.zeros(data_T2_24.shape)
# # mask_marker[box_zone2] = markers_2
# # functions.saveImage(mask_marker, im_T2, "markers_2")

# ### RANDOM WALKER ZONA 1
# labels_zone1_crop = random_walker(data_WMnull_crop, markers_2, beta=beta, mode="cg_mg", tol=1e-6, return_full_prob=True)

# labels_zone1 = np.zeros(data_T2_24.shape)
# labels_zone1[box_zone2] = labels_zone1_crop[0]
# mask_zone1 = binary_closing(np.where(labels_zone1 > 0.1, 1, 0).astype(bool), structure=ball(3))
# functions.saveImage(functions.connectedComponents(mask_zone1).astype(np.uint8), im_T2, "mask_zone1")
# print(np.count_nonzero(mask_zone1))

# mask_zone2_closed = closeHoles(labels_sum > 0.9)
# mask_zone2 = functions.connectedComponents(mask_zone2_closed & ~mask_zone1)
# functions.saveImage(mask_zone2.astype(np.uint8), im_T2, "mask_zone2")
# print(np.count_nonzero(mask_zone2))





