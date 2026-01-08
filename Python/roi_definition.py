#External libraries
import nibabel as nib
import matplotlib.pyplot as plt
import numpy as np
from skimage.morphology import square, closing
#from skimage.measure import label, regionprops
from skimage import color, measure
from scipy.ndimage import center_of_mass
from scipy.spatial import ConvexHull
from scipy.ndimage import distance_transform_edt, binary_erosion
from scipy.spatial.distance import cdist


#Local libraries
import functions
	
def handleMediallemniscus(data_seg,map_RN,data_FAmap,hemisphere):
	print(f"Medial Lemniscus ({hemisphere} hemisphere)")
	mask_ML_region = np.zeros(data_seg.shape, dtype=bool)
	mask_ML = np.zeros(data_seg.shape, dtype=bool)
	
	if hemisphere == 'left':
	    threshold = 150
	    while (mask_ML[mask_ML == True].size < 300):
		
	      # Limite de fatias axiais que contêm voxels do red nucleus
	      kmin_RN = np.where(map_RN != 0)[2].min()
	      kmax_RN = np.where(map_RN != 0)[2].max()
	    
	      for k in range (kmin_RN + 2, kmax_RN - 2):
	        mask_temp_RN = np.zeros((640,640), dtype=bool)
	        mask_temp_midbrain = np.zeros((640,640), dtype=bool)
	      
	        # Region between RN and SN
	      	  
	        jmax_RN_temp = np.where(map_RN[:,:,k] != 0)[1].max()
	        imin_RN_temp = np.where(map_RN[:,jmax_RN_temp,k] != 0)[0].min()
	        mask_temp_RN[imin_RN_temp + 1:,:] = True
	        mask_temp_midbrain = np.where(data_seg[:,:,k] == 384, True, False)		
	        mask_blue = np.where(data_FAmap[:,:,k,2] > threshold, True, False).astype(bool)
	        mask_ML[:,:,k] = mask_temp_midbrain & mask_temp_RN & mask_blue
	      threshold = threshold - 20		 		
	
	if hemisphere == 'right':
		
		threshold = 150
		while (mask_ML[mask_ML == True].size < 300):
		  # Limite de fatias axiais que contêm voxels do red nucleus
		  kmin_RN = np.where(map_RN != 0)[2].min()
		  kmax_RN = np.where(map_RN != 0)[2].max()
		
		  for k in range (kmin_RN + 2, kmax_RN - 2):
		    mask_temp_RN = np.zeros((640,640), dtype=bool)
		    mask_temp_midbrain = np.zeros((640,640), dtype=bool)
		    mask_temp_intersection = np.zeros((640,640), dtype=bool)

		    # Region between RN and SN
		    jmax_RN_temp = np.where(map_RN[:,:,k] != 0)[1].max()
		    imax_RN_temp = np.where(map_RN[:,jmax_RN_temp,k] != 0)[0].max()
		    mask_temp_RN[:imax_RN_temp - 1,:] = True
		    mask_temp_midbrain = np.where(data_seg[:,:,k] == 1384, True, False)		
		    mask_blue = np.where(data_FAmap[:,:,k,2] > threshold, True, False).astype(bool)
		    mask_ML[:,:,k] = mask_temp_midbrain & mask_temp_RN & mask_blue
		  threshold = threshold - 20

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
		mask_slices[:,:,kmin_RN + 2:kmax_RN - 2] = True
		mask_lh_wmseg = (data_seg == 7) | (data_seg == 611)
		
		for k_slice in range (kmin_RN + 2, kmax_RN - 2):
			i1_point = np.where(map_SN[:,:,k_slice] != 0)[1].max()          #1: ponto mais abaixo e mais à esquerda (ponto de baixo)
			j1_point = np.where(map_SN[:,i1_point,k_slice] != 0)[0].min()
			j2_point = np.where(map_SN[:,:,k_slice] != 0)[0].min()          #2: ponto mais à esquerda e mais acima (ponto de cima)
			i2_point = np.where(map_SN[j2_point,:,k_slice] != 0)[0].min()
			i3_point = i2_point + (i1_point - i2_point)/3
			j3_point = j2_point + (j1_point - j2_point)/3
			j4_point = np.where(map_SN[:,:,k_slice] != 0)[0].max()
			i4_point = np.where(map_SN[j4_point,:,k_slice] != 0)[0].max()
			a,b = functions.linearfunctionPoints(i1_point,j1_point,i2_point,j2_point)
			b2 = functions.linearfunctionCoeficient(-1/a,i3_point,j3_point)
			b3 = functions.linearfunctionCoeficient(-1/a,i4_point,j4_point)
			mask_temp_line = (j_grid > (-1/a) * i_grid + b2) & (j_grid < (-1/a) * i_grid + b3)
			mask_CP[:,:,k_slice] = mask_brainstem_closed[:,:,k_slice] & mask_lh_wmseg[:,:,k_slice] & mask_slices[:,:,k_slice] & mask_temp_line
		mask_CP_filtered = functions.connectedComponents(mask_CP)
			
	if hemisphere == 'right':
		kmin_RN = np.where(map_RN != 0)[2].min()
		kmax_RN = np.where(map_RN != 0)[2].max()
		mask_slices[:,:,kmin_RN + 2:kmax_RN - 2] = True
		mask_rh_wmseg = (data_seg == 1007) | (data_seg == 1611)
		
		for k_slice in range (kmin_RN + 2, kmax_RN - 2):
			i1_point = np.where(map_SN[:,:,k_slice] != 0)[1].max()           #1: ponto mais abaixo e mais à direita (ponto de baixo)
			j1_point = np.where(map_SN[:,i1_point,k_slice] != 0)[0].max()    
			j2_point = np.where(map_SN[:,:,k_slice] != 0)[0].max()           #2: ponto mais à direita e mais acima (ponto de cima)
			i2_point = np.where(map_SN[j2_point,:,k_slice] != 0)[0].min()
			i3_point = i2_point - (i2_point - i1_point)/3
			j3_point = j2_point + (j1_point - j2_point)/3
			j4_point = np.where(map_SN[:,:,k_slice] != 0)[0].min()
			i4_point = np.where(map_SN[j4_point,:,k_slice] != 0)[0].max()
			a,b = functions.linearfunctionPoints(i1_point,j1_point,i2_point,j2_point)
			b2 = functions.linearfunctionCoeficient(-1/a,i3_point,j3_point)
			b3 = functions.linearfunctionCoeficient(-1/a,i4_point,j4_point)
			mask_temp_line = (j_grid < (-1/a) * i_grid + b2) & (j_grid > (-1/a) * i_grid + b3)
			mask_CP[:,:,k_slice] = mask_brainstem_closed[:,:,k_slice] & mask_rh_wmseg[:,:,k_slice] & mask_slices[:,:,k_slice] & mask_temp_line
			#mask_CP[:,:,k_slice] = mask_temp_line 
		mask_CP_filtered = functions.connectedComponents(mask_CP)
	
	print(f"{mask_CP_filtered[mask_CP_filtered == True].size} voxels.")
	return mask_CP_filtered

def auto_threshold(subA, subB):
	surfaceA = np.argwhere(subA & ~binary_erosion(subA))
	surfaceB = np.argwhere(subB & ~binary_erosion(subB))
	
	if len(surfaceA) == 0 or len(surfaceB) == 0:
		return 3.0
		
	# Calcular distância mínima com broadcasting (mais eficiente)
	diffs = surfaceA[:, np.newaxis, :] - surfaceB[np.newaxis, :, :]
	dists = np.sqrt(np.sum(diffs**2, axis=2))
	return np.min(dists) + 2.0

def handlePsa(maskA, maskB, hemisphere):
    print(f"Post Subthalamic Area ({hemisphere} hemisphere)")
    margin=10
    
    # 1. Determinar o bounding box combinado com margem de segurança
    combined = maskA | maskB
    coords = np.argwhere(combined)
    
    if len(coords) == 0:
        return np.zeros_like(maskA, dtype=bool)
    
    mins = np.maximum(coords.min(axis=0) - margin, 0)
    maxs = np.minimum(coords.max(axis=0) + margin + 1, maskA.shape)
    
    slices = tuple(slice(mins[i], maxs[i]) for i in range(3))
    maskA_bb = maskA[slices]
    maskB_bb = maskB[slices]
    distance_threshold = auto_threshold(maskA_bb, maskB_bb)
    
    distA_bb = distance_transform_edt(~maskA_bb)
    distB_bb = distance_transform_edt(~maskB_bb)
    
    proximity_mask_bb = (distA_bb <= distance_threshold) & (distB_bb <= distance_threshold)
    
    combined_bb = maskA_bb | maskB_bb
    ijk_bb = np.array(np.nonzero(combined_bb)).T
    
    if len(ijk_bb) < 4:
        hull_mask_bb = np.ones_like(combined_bb, dtype=bool)
    else:
        hull = ConvexHull(ijk_bb)
        
        # Criar grid apenas dentro do bounding box
        grid_shape = tuple(maxs - mins)
        grid_coords = np.array(np.indices(grid_shape)).reshape(3, -1).T
        
        # Testar pontos dentro do convex hull
        vals = hull.equations[:, :3].dot(grid_coords.T) + hull.equations[:, 3:4]
        inside = np.all(vals <= 0, axis=0)
        hull_mask_bb = inside.reshape(grid_shape)
    
    between_bb = hull_mask_bb & proximity_mask_bb & ~combined_bb
    
    between = np.zeros_like(maskA, dtype=bool)
    between[slices] = between_bb
    print(f"{between[between == True].size} voxels.")
    
    return between
    
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
			mask_red = np.where(data_FAmap[:,:,k_slice,0] < 150, True, False).astype(bool)
			mask_green = np.where(data_FAmap[:,:,k_slice,1] < 150, True, False).astype(bool)
			mask_blue = np.where(data_FAmap[:,:,k_slice,2] > 200, True, False).astype(bool)
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
			mask_red = np.where(data_FAmap[:,:,k_slice,0] < 150, True, False).astype(bool)
			mask_green = np.where(data_FAmap[:,:,k_slice,1] < 150, True, False).astype(bool)
			mask_blue = np.where(data_FAmap[:,:,k_slice,2] > 200, True, False).astype(bool)
			mask_threshold = mask_red & mask_green & mask_blue
			# Intersection
			mask_PostLimb[:,:,k_slice] = mask_limit & mask_threshold & map_wm[:,:,k_slice]
			
	print(f"{mask_PostLimb[mask_PostLimb == True].size} voxels.")
	return mask_PostLimb
		
