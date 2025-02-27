#External libraries
import nibabel as nib
import matplotlib.pyplot as plt
import numpy as np
from skimage.morphology import square, closing
from skimage.measure import label, regionprops

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
	
def handleCerebralpeduncle(data_seg,data_synthseg,map_RN,hemisphere):
	print(f"Cerebral peduncle ({hemisphere} hemisphere)")
	
	mask_brainstem = np.zeros(data_synthseg.shape, dtype=bool)
	mask_brainstem_closed = np.zeros(data_synthseg.shape, dtype=bool)
	mask_slices = np.zeros(data_seg.shape, dtype=bool)
	
	mask_brainstem[(data_synthseg[:,:,:] == 16) | (data_synthseg[:,:,:] == 28) | (data_synthseg[:,:,:] == 60)] = True
	map_RN_both = np.array(np.where((data_seg == 385) | (data_seg == 1385) , True, False), dtype=bool)
	kmin_RN = np.where(map_RN_both != 0)[2].min()
	kmax_RN = np.where(map_RN_both != 0)[2].max()
	
	for k in range (kmin_RN, kmax_RN):
		mask_brainstem_closed[:,:,k] = closing(mask_brainstem[:,:,k], square(10))
	
	if hemisphere == 'left':
		kmin_RN = np.where(map_RN != 0)[2].min()
		kmax_RN = np.where(map_RN != 0)[2].max()
	
		mask_lh_wmseg = (data_seg == 7) | (data_seg == 611)
		mask_slices[:,:,kmin_RN:kmin_RN + 5] = True
		mask_CP = mask_brainstem_closed & mask_lh_wmseg & mask_slices

		# Identificar componentes conectados
		labeled_lh_CP = label(mask_CP, connectivity=1)  
		# Calcular propriedades das regiões 
		regions = regionprops(labeled_lh_CP)
		# Encontrar a região com maior número de voxels
		if regions:  
			largest_region = max(regions, key=lambda x: x.area)
			mask_CP_filtered = (labeled_lh_CP == largest_region.label)
		else:
			print("Nenhum componente encontrado.")
			mask_CP_filtered = np.zeros_like(mask_CP, dtype=bool)	
			
	if hemisphere == 'right':
		kmin_RN = np.where(map_RN != 0)[2].min()
		kmax_RN = np.where(map_RN != 0)[2].max()
	
		mask_lh_wmseg = (data_seg == 1007) | (data_seg == 1611)
		mask_slices[:,:,kmin_RN:kmin_RN + 5] = True
		mask_CP = mask_brainstem_closed & mask_lh_wmseg & mask_slices

		# Identificar componentes conectados
		labeled_lh_CP = label(mask_CP, connectivity=1)  
		# Calcular propriedades das regiões 
		regions = regionprops(labeled_lh_CP)
		# Encontrar a região com maior número de voxels
		if regions:  
			largest_region = max(regions, key=lambda x: x.area)
			mask_CP_filtered = (labeled_lh_CP == largest_region.label)
		else:
			print("Nenhum componente encontrado.")
			mask_CP_filtered = np.zeros_like(mask_CP, dtype=bool)	
	
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
		
		min_dif = np.inf
		for k in range(min_k, max_k + 1):
		  len_RN = map_RN[:,:,k][map_RN[:,:,k] == True].size
		  len_STN = map_STN[:,:,k][map_STN[:,:,k] == True].size
		  dif = np.abs(len_RN - len_STN)
		  if dif < min_dif:
			  k_slice = k
			  min_dif = dif	
	
		imin_RN = np.where(map_RN[:,:,k_slice])[0].min()
		jmax_RN = np.where(map_RN[:,:,k_slice])[1].max()
		mask_temp_RN[imin_RN:,:jmax_RN + 1] = True
		
		imax_STN = np.where(map_STN[:,:,k_slice])[0].max()
		jmin_STN = np.where(map_STN[:,:,k_slice])[1].min()
		mask_temp_STN[:imax_STN + 1,jmin_STN:] = True
		
		mask_temp_regions[data_seg[:,:,k_slice] == 435] = True
		mask_temp_regions[data_seg[:,:,k_slice] == 384] = True
		
		i1_point = np.where(map_RN[:,:,k_slice] != 0)[1].max()
		j1_point = np.where(map_RN[:,i1_point,k_slice] != 0)[0].max()
		j2_point = np.where(map_STN[:,:,k_slice] != 0)[0].max()
		i2_point = np.where(map_STN[j2_point,:,k_slice] != 0)[0].max()
		a,b = functions.linearfunctionPoints(i1_point,j1_point,i2_point,j2_point)
		i3_point = np.where(map_RN[:,:,k_slice] != 0)[1].min()
		j3_point = np.where(map_RN[:,i3_point,k_slice] != 0)[0].min()
		b3 = functions.linearfunctionCoeficient(a,i3_point,j3_point)

		x = np.arange(data_seg.shape[0])
		y = np.arange(data_seg.shape[1])
		i_grid, j_grid = np.meshgrid(x, y)	
		mask_temp_line = (j_grid < (a * i_grid + b)) & (j_grid > (a * i_grid + b3))
		
		jmin_slice = np.where(map_RN[:,:,k_slice] != 0)[1].min()
		jmax_slice = np.where(map_RN[:,:,k_slice] != 0)[1].max()

		for j in range(jmin_slice, jmax_slice + 1):
		  imin_line = np.where(map_RN[:,j,k_slice] != 0)[0].min()
		  mask_temp_side[:imin_line,j] = True
		  
		mask_PSA[:,:,k_slice] = mask_temp_RN & mask_temp_STN & mask_temp_regions & mask_temp_line & ~mask_temp_side
	
	if hemisphere == 'right':
		kmin_RN = np.where(map_RN != 0)[2].min()
		kmax_RN = np.where(map_RN != 0)[2].max()
		
		kmin_STN = np.where(map_STN != 0)[2].min()
		kmax_STN = np.where(map_STN != 0)[2].max()
		
		min_k = max(kmin_RN, kmin_STN)
		max_k = min(kmax_RN, kmax_STN)

		min_dif = np.inf
		for k in range(min_k, max_k + 1):
		  len_RN = map_RN[:,:,k][map_RN[:,:,k] == True].size
		  len_STN = map_STN[:,:,k][map_STN[:,:,k] == True].size
		  dif = np.abs(len_RN - len_STN)
		  if dif < min_dif:
			  k_slice = k
			  min_dif = dif

		imax_RN = np.where(map_RN[:,:,k_slice])[0].max()
		jmax_RN = np.where(map_RN[:,:,k_slice])[1].max()	
		mask_temp_RN[:imax_RN + 1,:jmax_RN + 1] = True

		imin_STN = np.where(map_STN[:,:,k_slice])[0].min()
		jmin_STN = np.where(map_STN[:,:,k_slice])[1].min()
		mask_temp_STN[imin_STN:,jmin_STN:] = True

		mask_temp_regions[data_seg[:,:,k_slice] == 1435] = True
		mask_temp_regions[data_seg[:,:,k_slice] == 1384] = True
		
		i1_point = np.where(map_RN[:,:,k_slice] != 0)[1].max()
		j1_point = np.where(map_RN[:,i1_point,k_slice] != 0)[0].min()
		j2_point = np.where(map_STN[:,:,k_slice] != 0)[0].min()
		i2_point = np.where(map_STN[j2_point,:,k_slice] != 0)[0].max()
		a,b = functions.linearfunctionPoints(i1_point,j1_point,i2_point,j2_point)
		i3_point = np.where(map_RN[:,:,k_slice] != 0)[1].min()
		j3_point = np.where(map_RN[:,i3_point,k_slice] != 0)[0].max()
		b3 = functions.linearfunctionCoeficient(a,i3_point,j3_point)	
		
		x = np.arange(data_seg.shape[0])
		y = np.arange(data_seg.shape[1])
		i_grid, j_grid = np.meshgrid(x, y)
		mask_temp_line = (j_grid > (a * i_grid + b)) & (j_grid < (a * i_grid + b3))	
		
		jmin_slice = np.where(map_RN[:,:,k_slice] != 0)[1].min()
		jmax_slice = np.where(map_RN[:,:,k_slice] != 0)[1].max()
		for j in range(jmin_slice, jmax_slice + 1):
		  imax_line = np.where(map_RN[:,j,k_slice] != 0)[0].max()
		  mask_temp_side[imax_line:,j] = True	
		  
		mask_PSA[:,:,k_slice] = mask_temp_RN & mask_temp_STN & mask_temp_regions & mask_temp_line & ~mask_temp_side

	
	print(f"{mask_PSA[mask_PSA == True].size} voxels.")
	return mask_PSA
