#External libraries
import nibabel as nib
import matplotlib.pyplot as plt
import numpy as np
from skimage.morphology import square, closing
#from skimage.measure import label, regionprops
from skimage import color, measure
from scipy.ndimage import center_of_mass

#Local libraries
import functions
	
def handleMediallemniscus(data_seg,map_RN,hemisphere):
	print(f"Medial Lemniscus ({hemisphere} hemisphere)")
	mask_ML = np.zeros(data_seg.shape, dtype=bool)
	
	if hemisphere == 'left':
		
		# Limite de fatias axiais que contêm voxels do red nucleus
		kmin_RN = np.where(map_RN != 0)[2].min()
		kmax_RN = np.where(map_RN != 0)[2].max()
		
		for k in range (kmin_RN, kmin_RN + 5):
		  mask_temp_RN = np.zeros((640,640), dtype=bool)
		  mask_temp_midbrain = np.zeros((640,640), dtype=bool)
		  mask_temp_intersection = np.zeros((640,640), dtype=bool)
		  		  
		  imax_RN_temp = np.where(map_RN[:,:,k] != 0)[0].max()
		  mask_temp_RN[imax_RN_temp + 1:,:] = True
		  mask_temp_midbrain = np.where(data_seg[:,:,k] == 384, True, False)
		  mask_ML[:,:,k] = mask_temp_RN & mask_temp_midbrain
	
	if hemisphere == 'right':
		
		# Limite de fatias axiais que contêm voxels do red nucleus
		kmin_RN = np.where(map_RN != 0)[2].min()
		kmax_RN = np.where(map_RN != 0)[2].max()
		
		for k in range (kmin_RN, kmin_RN + 5):
		  mask_temp_RN = np.zeros((640,640), dtype=bool)
		  mask_temp_midbrain = np.zeros((640,640), dtype=bool)
		  mask_temp_intersection = np.zeros((640,640), dtype=bool)

		  imin_RN_temp = np.where(map_RN[:,:,k] != 0)[0].min()
		  mask_temp_RN[:imin_RN_temp,:] = True
		  mask_temp_midbrain = np.where(data_seg[:,:,k] == 1384, True, False)
		  mask_ML[:,:,k] = mask_temp_RN & mask_temp_midbrain
	
	print(f"{mask_ML[mask_ML == True].size} voxels.")
	return mask_ML	
	
def handleCerebralpeduncle(data_seg,data_synthseg,map_RN, map_SN,hemisphere):
	print(f"Cerebral peduncle ({hemisphere} hemisphere)")
	
	mask_temp_line = np.zeros((640,640), dtype=bool)
	mask_brainstem = np.zeros(data_synthseg.shape, dtype=bool)
	mask_brainstem_closed = np.zeros(data_synthseg.shape, dtype=bool)
	mask_slices = np.zeros(data_seg.shape, dtype=bool)
	mask_CP = np.zeros(data_seg.shape, dtype=bool)
	
	mask_brainstem[(data_synthseg[:,:,:] == 16) | (data_synthseg[:,:,:] == 28) | (data_synthseg[:,:,:] == 60)] = True
	map_RN_both = np.array(np.where((data_seg == 385) | (data_seg == 1385) , True, False), dtype=bool)
	kmin_RN = np.where(map_RN_both != 0)[2].min()
	kmax_RN = np.where(map_RN_both != 0)[2].max()
	x = np.arange(data_seg.shape[0])
	y = np.arange(data_seg.shape[1])
	i_grid, j_grid = np.meshgrid(x, y)	
	
	for k in range (kmin_RN, kmax_RN):
		mask_brainstem_closed[:,:,k] = closing(mask_brainstem[:,:,k], square(10))
	
	if hemisphere == 'left':
		kmin_RN = np.where(map_RN != 0)[2].min()
		kmax_RN = np.where(map_RN != 0)[2].max()
		mask_slices[:,:,kmin_RN:kmin_RN + 5] = True
		mask_lh_wmseg = (data_seg == 7) | (data_seg == 611)
		
		for k_slice in range (kmin_RN, kmin_RN + 5):
			i1_point = np.where(map_SN[:,:,k_slice] != 0)[1].max()
			j1_point = np.where(map_SN[:,i1_point,k_slice] != 0)[0].min()
			j2_point = np.where(map_SN[:,:,k_slice] != 0)[0].min()
			i2_point = np.where(map_SN[j2_point,:,k_slice] != 0)[0].min()
			j3_point = np.where(map_SN[:,:,k_slice] != 0)[0].max()
			i3_point = np.where(map_SN[j3_point,:,k_slice] != 0)[0].max()
			a,b = functions.linearfunctionPoints(i1_point,j1_point,i2_point,j2_point)
			b2 = functions.linearfunctionCoeficient(-1/a,i3_point,j3_point)
			mask_temp_line = (j_grid < (-1/a) * i_grid + b2)
			mask_CP[:,:,k_slice] = mask_brainstem_closed[:,:,k_slice] & mask_lh_wmseg[:,:,k_slice] & mask_slices[:,:,k_slice] & mask_temp_line
		mask_CP_filtered = functions.connectedComponents(mask_CP)
			
	if hemisphere == 'right':
		kmin_RN = np.where(map_RN != 0)[2].min()
		kmax_RN = np.where(map_RN != 0)[2].max()
		mask_slices[:,:,kmin_RN:kmin_RN + 5] = True
		mask_rh_wmseg = (data_seg == 1007) | (data_seg == 1611)
		
		for k_slice in range (kmin_RN, kmin_RN + 5):
			i1_point = np.where(map_SN[:,:,k_slice] != 0)[1].max()
			j1_point = np.where(map_SN[:,i1_point,k_slice] != 0)[0].max()
			j2_point = np.where(map_SN[:,:,k_slice] != 0)[0].max()
			i2_point = np.where(map_SN[j2_point,:,k_slice] != 0)[0].min()
			j3_point = np.where(map_SN[:,:,k_slice] != 0)[0].min()
			i3_point = np.where(map_SN[j3_point,:,k_slice] != 0)[0].max()
			a,b = functions.linearfunctionPoints(i1_point,j1_point,i2_point,j2_point)
			b2 = functions.linearfunctionCoeficient(-1/a,i3_point,j3_point)
			mask_temp_line = (j_grid > (-1/a) * i_grid + b2)
			mask_CP[:,:,k_slice] = mask_brainstem_closed[:,:,k_slice] & mask_rh_wmseg[:,:,k_slice] & mask_slices[:,:,k_slice] & mask_temp_line
		mask_CP_filtered = functions.connectedComponents(mask_CP)
	
	print(f"{mask_CP_filtered[mask_CP_filtered == True].size} voxels.")
	return mask_CP_filtered
	
def handlePsa(data_seg,map_RN, map_STN,hemisphere):
	print(f"Post Subthalamic Area ({hemisphere} hemisphere)")
	mask_temp_RN = np.zeros((640,640), dtype=bool)
	mask_temp_STN = np.zeros((640,640), dtype=bool)
	mask_temp_regions = np.zeros((640,640), dtype=bool)
	mask_temp_line = np.zeros((640,640), dtype=bool)
	mask_temp_side = np.zeros((640,640), dtype=bool)
	mask_PSA = np.zeros(data_seg.shape, dtype=bool)
	
	if hemisphere == 'left':
		kmin_RN = np.where(map_RN != 0)[2].min()
		kmax_RN = np.where(map_RN != 0)[2].max()
		
		kmin_STN = np.where(map_STN != 0)[2].min()
		kmax_STN = np.where(map_STN != 0)[2].max()
		
		min_k = max(kmin_RN, kmin_STN)
		max_k = min(kmax_RN, kmax_STN)
		
		for k_slice in range(min_k, max_k + 1):
			# min_dif = np.inf
			# for k in range(min_k, max_k + 1):
			  # len_RN = map_RN[:,:,k][map_RN[:,:,k] == True].size
			  # len_STN = map_STN[:,:,k][map_STN[:,:,k] == True].size
			  # dif = np.abs(len_RN - len_STN)
			  # if dif < min_dif:
				  # k_slice = k
				  # min_dif = dif	
		
			imin_RN = np.where(map_RN[:,:,k_slice])[0].min()
			jmax_RN = np.where(map_RN[:,:,k_slice])[1].max()
			mask_temp_RN[imin_RN:,:jmax_RN + 1] = True
			
			imax_STN = np.where(map_STN[:,:,k_slice])[0].max()
			jmin_STN = np.where(map_STN[:,:,k_slice])[1].min()
			mask_temp_STN[:imax_STN + 1,jmin_STN:] = True
			
			mask_temp_regions[data_seg[:,:,k_slice] == 435] = True
			mask_temp_regions[data_seg[:,:,k_slice] == 384] = True
			
			i1_point = np.where(map_STN[:,:,k_slice] != 0)[1].max()
			j1_point = np.where(map_STN[:,i1_point,k_slice] != 0)[0].min()
			j2_point = np.where(map_STN[:,:,k_slice] != 0)[0].min()
			i2_point = np.where(map_STN[j2_point,:,k_slice] != 0)[0].max()
			i3_point = np.where(map_RN[:,:,k_slice] != 0)[1].max()
			j3_point = np.where(map_RN[:,i3_point,k_slice] != 0)[0].max()
			i4_point = np.where(map_RN[:,:,k_slice] != 0)[1].min()
			j4_point = np.where(map_RN[:,i4_point,k_slice] != 0)[0].min()
			x = np.arange(data_seg.shape[0])
			y = np.arange(data_seg.shape[1])
			i_grid, j_grid = np.meshgrid(x, y)	
			if (i1_point != i2_point):
				a,b = functions.linearfunctionPoints(i1_point,j1_point,i2_point,j2_point)
				b2 = functions.linearfunctionCoeficient(-1/a,i3_point,j3_point)
				b3 = functions.linearfunctionCoeficient(-1/a,i4_point,j4_point)
				mask_temp_line = (j_grid < ((-1/a) * i_grid + b2)) & (j_grid > ((-1/a) * i_grid + b3))
			else:
				mask_temp_line = (i_grid < i1_point) & (i_grid > i3_point)
			
			jmin_slice = np.where(map_RN[:,:,k_slice] != 0)[1].min()
			jmax_slice = np.where(map_RN[:,:,k_slice] != 0)[1].max()

			for j in range(jmin_slice, jmax_slice + 1):
				try:
					imin_line = np.where(map_RN[:,j,k_slice] != 0)[0].min()
					mask_temp_side[:imin_line,j] = True
				except ValueError:
					imin_line = None
					mask_temp_side[:,j] = True
			  
			mask_PSA[:,:,k_slice] = mask_temp_RN & mask_temp_STN & mask_temp_regions & mask_temp_line & ~mask_temp_side & ~map_RN[:,:,k_slice]
	
	if hemisphere == 'right':
		kmin_RN = np.where(map_RN != 0)[2].min()
		kmax_RN = np.where(map_RN != 0)[2].max()
		
		kmin_STN = np.where(map_STN != 0)[2].min()
		kmax_STN = np.where(map_STN != 0)[2].max()
		
		min_k = max(kmin_RN, kmin_STN)
		max_k = min(kmax_RN, kmax_STN)
		
		for k_slice in range(min_k, max_k + 1):
			# min_dif = np.inf
			# for k in range(min_k, max_k + 1):
			  # len_RN = map_RN[:,:,k][map_RN[:,:,k] == True].size
			  # len_STN = map_STN[:,:,k][map_STN[:,:,k] == True].size
			  # dif = np.abs(len_RN - len_STN)
			  # if dif < min_dif:
				  # k_slice = k
				  # min_dif = dif

			imax_RN = np.where(map_RN[:,:,k_slice])[0].max()
			jmax_RN = np.where(map_RN[:,:,k_slice])[1].max()	
			mask_temp_RN[:imax_RN + 1,:jmax_RN + 1] = True

			imin_STN = np.where(map_STN[:,:,k_slice])[0].min()
			jmin_STN = np.where(map_STN[:,:,k_slice])[1].min()
			mask_temp_STN[imin_STN:,jmin_STN:] = True

			mask_temp_regions[data_seg[:,:,k_slice] == 1435] = True
			mask_temp_regions[data_seg[:,:,k_slice] == 1384] = True
			
			i1_point = np.where(map_STN[:,:,k_slice] != 0)[1].max()
			j1_point = np.where(map_STN[:,i1_point,k_slice] != 0)[0].max()
			j2_point = np.where(map_STN[:,:,k_slice] != 0)[0].max()
			i2_point = np.where(map_STN[j2_point,:,k_slice] != 0)[0].max()
			i3_point = np.where(map_RN[:,:,k_slice] != 0)[1].max()
			j3_point = np.where(map_RN[:,i3_point,k_slice] != 0)[0].min()
			i4_point = np.where(map_RN[:,:,k_slice] != 0)[1].min()
			j4_point = np.where(map_RN[:,i4_point,k_slice] != 0)[0].max()
			x = np.arange(data_seg.shape[0])
			y = np.arange(data_seg.shape[1])
			i_grid, j_grid = np.meshgrid(x, y)	
			if (i1_point != i2_point):
				a,b = functions.linearfunctionPoints(i1_point,j1_point,i2_point,j2_point)
				b2 = functions.linearfunctionCoeficient(-1/a,i3_point,j3_point)
				b3 = functions.linearfunctionCoeficient(-1/a,i4_point,j4_point)
				mask_temp_line = (j_grid > ((-1/a) * i_grid + b2)) & (j_grid < ((-1/a) * i_grid + b3))		
			else:
				mask_temp_line = (i_grid < i1_point) & (i_grid > i3_point)
			
			jmin_slice = np.where(map_RN[:,:,k_slice] != 0)[1].min()
			jmax_slice = np.where(map_RN[:,:,k_slice] != 0)[1].max()
			
			for j in range(jmin_slice, jmax_slice + 1):
				try:
					imax_line = np.where(map_RN[:,j,k_slice] != 0)[0].max()
					mask_temp_side[imax_line:,j] = True
				except ValueError:
					imax_line = None
					mask_temp_side[:,j] = True 
			  
			mask_PSA[:,:,k_slice] = mask_temp_RN & mask_temp_STN & mask_temp_regions & mask_temp_line & ~mask_temp_side & ~map_RN[:,:,k_slice]
	
	print(f"{mask_PSA[mask_PSA == True].size} voxels.")
	return mask_PSA
	
def handleLesionmask(data_Contrast, data_Contrast_24, data_rostral_lh, data_rostral_rh, Contrast):
	print(f"Lesion's mask")
	# Normalização
	data_preNorm = data_Contrast/np.abs(data_Contrast).max()
	data_24Norm = data_Contrast_24/np.abs(data_Contrast_24).max()
	
	# Diferença entre as imagens
	data = data_24Norm - data_preNorm
	
	# Salvar a subtração das imagens
	functions.saveImage(data, Contrast, "Contrast_difference")
	print("-Imagem Contrast_difference.nii.gz salva")
	
	# Inicializa uma máscara binária com zeros
	mask = np.zeros(np.abs(data).shape, dtype=np.float32)
	
	# Verifica o contorno para cada corte a partir de um limiar
	for x in range(data.shape[0]):
	  contornos = measure.find_contours(np.abs(data[x,:,:]), level=0.3)
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
	  mask_closed[x,:,:] = closing(mask[x,:,:], square(4))
	
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
	functions.saveImage(lesion_data_float, Contrast, "mask_lesion_float")
	functions.saveImage(lesion_data_binary, Contrast, "mask_lesion_binary")
	print("-mask_lesion.nii.gz salva")
	
	return lesion_data_float, lesion_data_binary

def handlePosteriorLimb(data_seg, data_FAmap, data_thalamus, hemisphere):
	print(f"Posterior limb Area ({hemisphere} hemisphere)")
	mask_threshold = np.zeros((640,640), dtype=bool)
	mask_limit = np.zeros((640,640), dtype=bool)
	mask_PostLimb = np.zeros(data_seg.shape, dtype=bool)
	mask_red = np.zeros((640,640), dtype=bool)
	mask_green = np.zeros((640,640), dtype=bool)
	mask_blue = np.zeros((640,640), dtype=bool)
	
	if hemisphere == 'left':
		
		map_globus_int = np.array(np.where((data_seg == 206), True, False), dtype=bool)
		map_globus_int_filtered = functions.connectedComponents(map_globus_int)
		map_midbrain = np.array(np.where((data_seg == 384), True, False), dtype=bool)
		map_midbrain_filtered = functions.connectedComponents(map_midbrain)	
		map_putamen = np.array(np.where((data_seg == 79), True, False), dtype=bool)
		map_wm = np.array(np.where((data_seg == 7), True, False), dtype=bool)
		
		#Inferior-superior limits:
		kmin = np.where(map_midbrain_filtered != 0)[2].max() + 1
		kmax = np.where(map_globus_int_filtered != 0)[2].max()
				
		for k_slice in range (kmin, kmax + 1):
			# Lateral limits
			imin = np.where(data_thalamus[:,:,k_slice] != 0)[0].min()
			imax = np.where(map_putamen[:,:,k_slice] != 0)[0].max()
			# Anterior-posterior limits
			jmin = np.where(map_globus_int_filtered[:,:,k_slice] != 0)[1].min()
			jmax = np.where(data_thalamus[:,:,k_slice] != 0)[1].max()
			# Limits mask
			mask_limit[imin:imax, jmin:jmax] = True
			# Threshold 
			mask_red = np.where(data_FAmap[:,:,k_slice,0] < 50, True, False).astype(bool)
			mask_green = np.where(data_FAmap[:,:,k_slice,1] < 50, True, False).astype(bool)
			mask_blue = np.where(data_FAmap[:,:,k_slice,2] > 70, True, False).astype(bool)
			mask_threshold = mask_red & mask_green & mask_blue
			# Intersection
			mask_PostLimb[:,:,k_slice] = mask_limit & mask_threshold & map_wm[:,:,k_slice]
			
	if hemisphere == 'right':
		
		map_globus_int = np.array(np.where((data_seg == 1206), True, False), dtype=bool)
		map_globus_int_filtered = functions.connectedComponents(map_globus_int)
		map_midbrain = np.array(np.where((data_seg == 1384), True, False), dtype=bool)
		map_midbrain_filtered = functions.connectedComponents(map_midbrain)	
		map_putamen = np.array(np.where((data_seg == 1079), True, False), dtype=bool)
		map_wm = np.array(np.where((data_seg == 1007), True, False), dtype=bool)
		
		#Inferior-superior limits:
		kmin = np.where(map_midbrain_filtered != 0)[2].max() + 1
		kmax = np.where(map_globus_int_filtered != 0)[2].max()
				
		for k_slice in range (kmin, kmax + 1):
			# Lateral limits
			imin = np.where(map_putamen[:,:,k_slice] != 0)[0].min()
			imax = np.where(data_thalamus[:,:,k_slice] != 0)[0].max()
			# Anterior-posterior limits
			jmin = np.where(map_globus_int_filtered[:,:,k_slice] != 0)[1].min()
			jmax = np.where(data_thalamus[:,:,k_slice] != 0)[1].max()
			# Limits mask
			mask_limit[imin:imax, jmin:jmax] = True
			# Threshold 
			mask_red = np.where(data_FAmap[:,:,k_slice,0] < 50, True, False).astype(bool)
			mask_green = np.where(data_FAmap[:,:,k_slice,1] < 50, True, False).astype(bool)
			mask_blue = np.where(data_FAmap[:,:,k_slice,2] > 70, True, False).astype(bool)
			mask_threshold = mask_red & mask_green & mask_blue
			# Intersection
			mask_PostLimb[:,:,k_slice] = mask_limit & mask_threshold & map_wm[:,:,k_slice]
	print(f"{mask_PostLimb[mask_PostLimb == True].size} voxels.")
	return mask_PostLimb	
		
