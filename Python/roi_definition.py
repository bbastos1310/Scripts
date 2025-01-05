#External libraries
import nibabel as nib
import matplotlib.pyplot as plt
import numpy as np
from skimage.morphology import square, closing

#Local libraries
import functions

def handleRednucleus(mean, data_freesurfer, data_NR, data_SN, ventral_value, hemisphere):
	print(f"Red nucleus ({hemisphere} hemisphere)")
	mean_NR = mean

	# Restrição dos voxels para uma região específica
	mask_midbrain = (data_freesurfer == 16) | (data_freesurfer == ventral_value)
	min_deviation = np.inf

	# Intervalo inicial para o threshold
	low = 0.3
	high = 1.0
	best_threshold = None
	map_NR = None

	# Busca binária
	while min_deviation > 10:  # Precisão desejada para o threshold
		mid = (low + high) / 2
		map_temp = np.zeros(data_freesurfer.shape, dtype=bool)
		data_NR_filtered = np.where(data_NR > mid, data_NR, 0)
		data_SN_filtered = np.where(data_SN > mid, data_SN, 0)
		mask_NR_higher = (data_NR_filtered >= data_SN_filtered) & (data_NR_filtered != 0)
		map_temp[mask_NR_higher & mask_midbrain] = True
		num_voxels = map_temp[map_temp == True].shape[0]
		deviation = np.abs(num_voxels - mean_NR)

		# Atualiza se o desvio atual for menor que o mínimo anterior
		if deviation < min_deviation:
			min_deviation = deviation
			best_threshold = mid
			map_NR = np.array(np.where(map_temp == True, map_temp, 0), dtype=bool)
			#print(map_NR[map_NR != 0].shape)

		# Ajusta os limites com base no número de voxels
		if num_voxels > mean_NR:
			low = mid  # Reduz o threshold mínimo
		else:
			high = mid  # Aumenta o threshold máximo

	print(f"Threshold:{best_threshold:.4f}.")
	print(f"{map_NR[map_NR != 0].size} voxels.")
	return map_NR

def handleSubstantianigra(mean,data_freesurfer,data_SN,data_NR,ventral_value,hemisphere):
	print(f"Substantia nigra ({hemisphere} hemisphere)")
	
	mean_SN = mean

	# Restrição dos voxels para uma região específica
	mask_midbrain = (data_freesurfer == 16) | (data_freesurfer == ventral_value)
	min_deviation = np.inf

	# Intervalo inicial para o threshold
	low = 0.3
	high = 1.0
	best_threshold = None
	map_SN = None

	# Busca binária
	while min_deviation > 10:  # Precisão desejada para o threshold
		mid = (low + high) / 2
		map_temp = np.zeros(data_freesurfer.shape, dtype=bool)
		data_NR_filtered = np.where(data_NR > mid, data_NR, 0)
		data_SN_filtered = np.where(data_SN > mid, data_SN, 0)
		mask_SN_higher = (data_SN_filtered > data_NR_filtered) & (data_SN_filtered != 0)
		map_temp[mask_SN_higher & mask_midbrain] = True
		num_voxels = map_temp[map_temp == True].shape[0]
		deviation = np.abs(num_voxels - mean_SN)

		# Atualiza se o desvio atual for menor que o mínimo anterior
		if deviation < min_deviation:
			min_deviation = deviation
			best_threshold = mid
			map_SN = np.array(np.where(map_temp == True, map_temp, 0), dtype=bool)
			#print(map_SN[map_SN != 0].shape)

		# Ajusta os limites com base no número de voxels
		if num_voxels > mean_SN:
			low = mid  # Reduz o threshold mínimo
		else:
			high = mid  # Aumenta o threshold máximo
	
	print(f"Threshold:{best_threshold:.4f}.")
	print(f"{map_SN[map_SN != 0].size} voxels.")
	return map_SN
	
def handleDentatenucleus(mean,data_freesurfer,data_DN,wm_value,hemisphere):
	print(f"Dentate nucleus ({hemisphere} hemisphere)")
	mean_DN = mean

	# Restrição dos voxels para uma região específica
	mask_wmcerebellum = (data_freesurfer == wm_value)
	min_deviation = np.inf

	# Intervalo inicial para o threshold
	low = 0.3
	high = 1.0
	best_threshold = None
	map_DN = None

	# Busca binária
	while min_deviation > 100:  # Precisão desejada para o threshold
		mid = (low + high) / 2
		map_temp = np.zeros(data_freesurfer.shape, dtype=bool)
		data_DN_filtered = np.where(data_DN > mid, data_DN, 0)
		mask_DN_higher = (data_DN_filtered != 0)
		map_temp[mask_DN_higher & mask_wmcerebellum] = True
		num_voxels = map_temp[map_temp == True].shape[0]
		deviation = np.abs(num_voxels - mean_DN)

		# Atualiza se o desvio atual for menor que o mínimo anterior
		if deviation < min_deviation:
			min_deviation = deviation
			best_threshold = mid
			map_DN = np.array(np.where(map_temp == True, map_temp, 0), dtype=bool)
			#print(map_DN[map_DN != 0].shape)

		# Ajusta os limites com base no número de voxels
		if num_voxels > mean_DN:
			low = mid  # Reduz o threshold mínimo
		else:
			high = mid  # Aumenta o threshold máximo

	print(f"Threshold:{best_threshold:.4f}.")
	print(f"{map_DN[map_DN != 0].size} voxels.")
	return map_DN

def handleMediallemniscus(data_freesurfer,map_NR,map_SN,ventral_value,hemisphere):
	print(f"Medial Lemniscus ({hemisphere} hemisphere)")

	map_ML = np.zeros(data_freesurfer.shape, dtype=bool)
	mask_ML = np.zeros(data_freesurfer.shape, dtype=bool)
	mask_kventricle = np.zeros(data_freesurfer.shape, dtype=bool)
	mask_jNR = np.zeros(data_freesurfer.shape, dtype=bool)
	mask_NR_region1 = np.zeros(data_freesurfer.shape, dtype=bool)
	mask_NR_region2 = np.zeros(data_freesurfer.shape, dtype=bool)
	mask_NR_SN = np.zeros(data_freesurfer.shape, dtype=bool)
	mask_brainstem = np.zeros(data_freesurfer.shape, dtype=bool)

	index_jmin_ventricle = np.where(data_freesurfer == 15)[1].argmin()
	k_ventricle = np.where(data_freesurfer == 15)[2][index_jmin_ventricle]
	jmin_NR = np.where(map_NR != 0)[1].min()
	jmax_NR = np.where(map_NR != 0)[1].max()

	for j in range (jmin_NR, jmax_NR): # loop para cada corte axial
	  if (np.where(map_NR[:,j,:] != 0)[0].size == 0):
		  continue
	  NR_lateral = np.where(map_NR[:,j,:] != 0)[0] # Corte com os valores laterais do red nucleus
	  SN_lateral = np.where(map_SN[:,j,:] != 0)[0] # Corte com os valores laterais da SN

	  # First region
	  mask_kventricle[:,j,k_ventricle:np.where(map_NR[:,j,:] != 0)[1].min()] = True    # máscara com todos voxels anteriores ao quarto ventrículo e posteriores ao red nucleus
	  if NR_lateral.size > 0 and SN_lateral.size > 0:
		  if (hemisphere == "right"):
			  mask_NR_region1[:NR_lateral.min(),j,:] = True
		  elif (hemisphere == "left"):
			  mask_NR_region1[NR_lateral.max() + 1:,j,:] = True
		  else:
			  print("invalid hemisphere")
			  break
		
	  mask_brainstem[:,j,:] = (data_freesurfer[:,j,:] == 16) | (data_freesurfer[:,j,:] == ventral_value)   # máscara com os voxels que pertencem ao brainstem ou ao ventral DC
	  map_ML[mask_kventricle & mask_NR_region1 & mask_brainstem] = True   # máscara com as interseções

	  # Second region
	  mask_NR_region2[:,j,np.where(map_NR[:,j,:] != 0)[1].min():np.where(map_NR[:,j,:] != 0)[1].max()] = True
	  if NR_lateral.size > 0 and SN_lateral.size > 0:
		  if (hemisphere == "right"):
			  mask_NR_SN[SN_lateral.min() + 1:NR_lateral.min() + 1,j,:] = True
		  elif (hemisphere == "left"):
			  mask_NR_SN[NR_lateral.max():SN_lateral.max(),j,:] = True
		  else:
			  print("invalid hemisphere")
			  break
		
	  map_ML[mask_NR_SN & mask_NR_region2 & mask_brainstem] = True
	  # print(map_ML[map_ML != 0].shape, end='')
	  # print(mask_NR_SN[:,j,:][mask_NR_SN[:,j,:] != 0].shape, end='')
	  # print(mask_NR_region2[:,j,:][mask_NR_region2[:,j,:] != 0].shape, end='')
	  # print(mask_brainstem[:,j,:][mask_brainstem[:,j,:] != 0].shape)

	map_ML[map_SN | map_NR] = False
	
	print(f"{map_ML[map_ML != 0].size} voxels.")
	return map_ML	
	
def handleCerebralpeduncle(data_freesurfer,map_NR,map_SN,wm_value,hemisphere):
	print(f"Cerebral peduncle ({hemisphere} hemisphere)")

	# Brainstem's closed mask
	mask_brainstem = np.zeros(data_freesurfer.shape, dtype=bool)
	mask_brainstem_closed = np.zeros(data_freesurfer.shape, dtype=bool)
	mask_brainstem[(data_freesurfer[:,:,:] == 16) | (data_freesurfer[:,:,:] == 28) | (data_freesurfer[:,:,:] == 60)] = True

	mask_wm_brainstem = np.zeros(data_freesurfer.shape, dtype=bool)
	map_CP = np.zeros(data_freesurfer.shape, dtype=bool)
	map_CP_temp = np.zeros(data_freesurfer.shape, dtype=bool)
	mask_function = np.zeros(data_freesurfer.shape, dtype=bool)
	mask_function2 = np.zeros(data_freesurfer.shape, dtype=bool)
	mask_function3 = np.zeros(data_freesurfer.shape, dtype=bool)
	
	jmin_NR = np.where(map_NR != 0)[1].min()
	jmax_NR = np.where(map_NR != 0)[1].max()
	for j in range (jmin_NR, jmax_NR):
		mask_brainstem_closed[:,j,:] = closing(mask_brainstem[:,j,:], square(4))
	mask_wm_brainstem[(mask_brainstem_closed) & (data_freesurfer == wm_value)] = True

	max_voxels = 0
	num_voxels = 0
	j_point = 0
	
	for j in range (jmin_NR, jmax_NR):
	  if (np.where(mask_wm_brainstem[:,j,:] != 0)[0].size == 0):
		  continue
	  num_voxels = np.where(map_SN[:,j,:] != 0)[1].shape[0]
	  if (num_voxels > max_voxels):
		  max_voxels = num_voxels
		  j_point = j

	i_point = np.where(mask_wm_brainstem[:,j_point,:] != 0)[0].min()
	k_point = np.where(mask_brainstem[i_point,j_point,:] != 0)[0].min()

	x = np.arange(data_freesurfer.shape[0])
	y = np.arange(data_freesurfer.shape[2])
	i_grid, k_grid = np.meshgrid(x, y)


	for j in range (jmin_NR + 3, jmax_NR-2):
		if (np.where(map_NR[:,j,:] != 0)[0].size == 0):
			continue
		#k2_point = np.where(map_SN[:,j,:])[1].max
		if np.where(map_SN[:,j,:])[1].size > 0:
			# Ponto da SN para montar a função linear
			k2_point = np.where(map_SN[:,j,:])[1].max()
			i2_point = np.where(map_SN[:,j,k2_point])[0].max()

			# Função linear com os dois pontos
			a,b = functions.linearfunctionPoints(k_point,i_point,k2_point, i2_point)
			if (hemisphere == "right"):
				mask_function[:,j,:] = k_grid < (a * i_grid + b)
			elif (hemisphere == "left"):
				mask_function[:,j,:] = k_grid > (a * i_grid + b)
			else:
				print("invalid hemisphere")
				break
			map_CP_temp[mask_function & mask_brainstem] = True    

			# Segunda função linear
			k_point_max = np.where(map_CP_temp[:,j,:])[1].max()
			i_point_max = np.where(map_CP_temp[:,j,k_point_max])[0].min()
			k_point_min = np.where(map_CP_temp[:,j,:])[1].min()
			i_point_min = np.where(map_CP_temp[:,j,k_point_min])[0].min()

			i_function2 = i_point_max + (i_point_min - i_point_max)/3
			k_function2 = k_point_max + (k_point_min - k_point_max)/3

			i_function3 = i_point_max + 2*(i_point_min - i_point_max)/3
			k_function3 = k_point_max + 2*(k_point_min - k_point_max)/3

			a_function2 = -1/a
			a_function3 = a_function2
			b_function2 = functions.linearfunctionCoeficient(a_function2,k_function2, i_function2)
			b_function3 = functions.linearfunctionCoeficient(a_function3,k_function3, i_function3)
			if (hemisphere == "right"):
				mask_function2[:,j,:] = k_grid < (a_function2 * i_grid + b_function2)
				mask_function3[:,j,:] = k_grid > (a_function3 * i_grid + b_function3)
			elif (hemisphere == "left"):
				mask_function2[:,j,:] = k_grid > (a_function2 * i_grid + b_function2)
				mask_function3[:,j,:] = k_grid < (a_function3 * i_grid + b_function3)
			else:
				print("invalid hemisphere")
				break
		
	map_CP[map_CP_temp & mask_function2 & mask_function3] = True

	  #   plt.imshow(mask_function3[:,j,:], cmap="gray", alpha=0.5)
	  #   plt.imshow(mask_brainstem[:,j,:], cmap="gray", alpha=0.5)
	  #   plt.show()
	  # break
	print(f"{map_CP[map_CP != 0].size} voxels.")
	return map_CP
