# Local libraries
import functions
import roi_definition as roi

# External libraries
import nibabel as nib
import numpy as np

# Main
## Load files

out_freesurfer = nib.load("output_freesurfer.nii.gz") # saída da segmentação do freesurfer
im_segleft = nib.load("seg_left_resampled.nii.gz") # saída da segmentação do mri_histo (hemisfério esquerdo)
im_segright = nib.load("seg_right_resampled.nii.gz") # saída da segmentação do mri_histo (hemisfério direito)
#im_synthseg = nib.load("SynthSeg_resampled.nii.gz") # saída da segmentação do mri_histo (equivalente à segmentação subcortical do freesurfer)
im_Contrast = nib.load("Contrast_raw_coreg_resampled.nii.gz") # Contrast gm/wm image before procedure
im_Contrast_24 = nib.load("Contrast_raw_coreg_24.nii.gz") # Contrast gm/wm image after procedure
im_rostral_lh = nib.load("ROI_rostral_lh_Contrast.nii.gz")
im_rostral_rh = nib.load("ROI_rostral_rh_Contrast.nii.gz")
im_thalamus_lh = nib.load("thalamus_mask_lh.nii.gz")
im_thalamus_rh = nib.load("thalamus_mask_rh.nii.gz")
im_FAmap = nib.load("Maps/FAmap_up.nii.gz")
print(".Files loaded")

## Extract data from image
data_freesurfer = out_freesurfer.get_fdata().astype(np.uint16) # (256x256x256)
data_segleft = im_segleft.get_fdata().astype(np.uint16) # (640x640x640)
data_segright = im_segright.get_fdata().astype(np.uint16) # (640x640x640)
# data_synthseg = im_synthseg.get_fdata().astype(np.uint16) # (640x640x640)
data_Contrast = im_Contrast.get_fdata().astype(np.uint16) # (560x641x71)
data_Contrast_24 = im_Contrast_24.get_fdata().astype(np.uint16) # (560x641x71)
data_rostral_lh = im_rostral_lh.get_fdata().astype(bool) 
data_rostral_rh = im_rostral_rh.get_fdata().astype(bool)  
data_thalamus_lh = im_thalamus_lh.get_fdata().astype(bool) 
data_thalamus_rh = im_thalamus_rh.get_fdata().astype(bool) 
data_FAmap = im_FAmap.get_fdata().astype(np.uint8) 
print(".Data loaded")

# Armazenar o affine das imagens para uso posterior
affine_segleft = im_segleft.affine
affine_segright = im_segright.affine
# affine_synthseg = im_synthseg.affine

del im_segleft, im_segright, im_Contrast, im_Contrast_24 # deletar as imagens da memória já que possuem resolução alta 

# Matriz para armazenar as informações dos dois hemisférios juntos 
data_seg = np.zeros(data_segleft.shape, dtype=np.uint16)

# Criar uma máscara para os valores que devem ser mantidos
mask_right = (data_segright < 1000) & (data_segright != 0)
mask_left = (data_segleft < 1000) & (data_segleft != 0)

# Diferenciar os valores entre os hemisférios

data_seg[mask_right] = data_segright[mask_right] + 1000
data_seg[mask_left] = data_segleft[mask_left]

del mask_right, mask_left

# ## RIGHT HEMISPHERE

### Red Nucleus
map_RN_rh = np.array(np.where(data_seg == 1385, True, False), dtype=bool)
map_RN_rh_filtered = functions.connectedComponents(map_RN_rh)
print(f"Red Nucleus (Right hemisphere)")
print(f"{map_RN_rh_filtered[map_RN_rh_filtered == True].size} voxels.")

### Substantia nigra
map_SN_rh = np.array(np.where((data_seg == 1310) | (data_seg == 1352), True, False), dtype=bool)
map_SN_rh_filtered = functions.connectedComponents(map_SN_rh)
print(f"Substantia Nigra (Right hemisphere)")
print(f"{map_SN_rh_filtered[map_SN_rh_filtered == True].size} voxels.")

### Dentante nucleus
map_DN_rh = np.array(np.where(data_seg == 1721, True, False), dtype=bool)
filled_DN_rh = functions.fillConvex_hull_volume(map_DN_rh)
map_DN_rh_filtered = functions.connectedComponents(filled_DN_rh)
print(f"Dentate Nucleus (Right hemisphere)")
print(f"{map_DN_rh_filtered[map_DN_rh_filtered == True].size} voxels.")

### Subthalamic nucleus
map_STN_rh = np.array(np.where((data_seg == 1315) | (data_seg == 1316) | (data_seg == 1321), True, False), dtype=bool)
map_STN_rh_filtered = functions.connectedComponents(map_STN_rh)
print(f"Subthalamic nucleus (Right hemisphere)")
print(f"{map_STN_rh_filtered[map_STN_rh_filtered == True].size} voxels.")

### Rostral division of VL
map_rostral_rh = np.array(np.where((data_seg == 1314) , True, False), dtype=bool)
print(f"Rostral division of VL (Right hemisphere)")
print(f"{map_rostral_rh[map_rostral_rh == True].size} voxels.")

### White matter (forebrain)
map_WMf_rh = np.array(np.where((data_seg == 1007), True, False), dtype=bool)
print(f"White matter - forebrain (Right hemisphere)")
print(f"{map_WMf_rh[map_WMf_rh == True].size} voxels.")

### White matter (hindbrain)
map_WMh_rh = np.array(np.where((data_seg == 1611), True, False), dtype=bool)
print(f"White matter - hindbrain (Right hemisphere)")
print(f"{map_WMh_rh[map_WMh_rh == True].size} voxels.")

### White matter (cerebellum)
map_WMc_rh = np.array(np.where((data_seg == 1846), True, False), dtype=bool)
print(f"White matter - cerebellum (Right hemisphere)")
print(f"{map_WMc_rh[map_WMc_rh == True].size} voxels.")

### Brainstem
map_brainstem_rh = np.array(np.where((data_seg == 1414) | (data_seg == 1580) | (data_seg == 1662), True, False), dtype=bool)
print(f"Brainstem (Right hemisphere)")
print(f"{map_brainstem_rh[map_brainstem_rh == True].size} voxels.")

### Medial Lemniscus
map_ML_rh = roi.handleMediallemniscus(data_seg,map_RN_rh,"right")

### Cerebral Peduncle
map_CP_rh = roi.handleCerebralpeduncle(data_seg, data_synthseg, map_RN_rh_filtered, map_SN_rh_filtered,"right")
map_CP_rh_filtered = functions.connectedComponents(map_CP_rh)

### Posterior subthalamic area
map_PSA_rh = roi.handlePsa(data_seg,map_RN_rh_filtered, map_STN_rh_filtered,"right")
map_PSA_rh_filtered = functions.connectedComponents(map_PSA_rh)

### Posterior limb of internal capsule
map_PostLimb_rh = roi.handlePosteriorLimb(data_seg,data_FAmap, data_thalamus_rh, "right")
map_PostLimb_rh_filtered = functions.connectedComponents(map_PostLimb_rh)

## LEFT HEMISPHERE

### Red Nucleus
map_RN_lh = np.array(np.where(data_seg == 385, True, False), dtype=bool)
map_RN_lh_filtered = functions.connectedComponents(map_RN_lh)
print(f"Red Nucleus (Left hemisphere)")
print(f"{map_RN_lh_filtered[map_RN_lh_filtered == True].size} voxels.")

### Substantia nigra
map_SN_lh = np.array(np.where((data_seg == 310) | (data_seg == 352), True, False), dtype=bool)
map_SN_lh_filtered = functions.connectedComponents(map_SN_lh)
print(f"Substantia Nigra (Left hemisphere)")
print(f"{map_SN_lh_filtered[map_SN_lh_filtered == True].size} voxels.")

### Dentante nucleus
map_DN_lh = np.array(np.where(data_seg == 721, True, False), dtype=bool)
filled_DN_lh = functions.fillConvex_hull_volume(map_DN_lh)
map_DN_lh_filtered = functions.connectedComponents(filled_DN_lh)
print(f"Dentate Nucleus (Left hemisphere)")
print(f"{map_DN_lh_filtered[map_DN_lh_filtered == True].size} voxels.")

### Subthalamic nucleus
map_STN_lh = np.array(np.where((data_seg == 315) | (data_seg == 316) | (data_seg == 321), True, False), dtype=bool)
map_STN_lh_filtered = functions.connectedComponents(map_STN_lh)
print(f"Subthalamic Nucleus (Left hemisphere)")
print(f"{map_STN_lh_filtered[map_STN_lh_filtered == True].size} voxels.")

### Rostral division of VL
map_rostral_lh = np.array(np.where((data_seg == 314) , True, False), dtype=bool)
print(f"Rostral division of VL (Left hemisphere)")
print(f"{map_rostral_lh[map_rostral_lh == True].size} voxels.")

### White matter (forebrain)
map_WMf_lh = np.array(np.where((data_seg == 7), True, False), dtype=bool)
print(f"White matter - forebrain (Left hemisphere)")
print(f"{map_WMf_lh[map_WMf_lh == True].size} voxels.")

### White matter (hindbrain)
map_WMh_lh = np.array(np.where((data_seg == 611), True, False), dtype=bool)
print(f"White matter - hindbrain (Left hemisphere)")
print(f"{map_WMh_lh[map_WMh_lh == True].size} voxels.")

### White matter (cerebellum)
map_WMc_lh = np.array(np.where((data_seg == 846), True, False), dtype=bool)
print(f"White matter - cerebellum (Left hemisphere)")
print(f"{map_WMc_lh[map_WMc_lh == True].size} voxels.")

### Brainstem
map_brainstem_lh = np.array(np.where((data_seg == 414) | (data_seg == 580) | (data_seg == 662), True, False), dtype=bool)
print(f"Brainstem (Left hemisphere)")
print(f"{map_brainstem_lh[map_brainstem_lh == True].size} voxels.")

### Medial Lemniscus
map_ML_lh = roi.handleMediallemniscus(data_seg,map_RN_lh,"left")

### Cerebral Peduncle
map_CP_lh = roi.handleCerebralpeduncle(data_seg, data_synthseg, map_RN_lh_filtered, map_SN_lh_filtered,"left")
map_CP_lh_filtered = functions.connectedComponents(map_CP_lh)

### Posterior subthalamic area
map_PSA_lh = roi.handlePsa(data_seg,map_RN_lh_filtered, map_STN_lh_filtered,"left")
map_PSA_lh_filtered = functions.connectedComponents(map_PSA_lh)

### Posterior limb of internal capsule
map_PostLimb_lh = roi.handlePosteriorLimb(data_seg,data_FAmap, data_thalamus_lh, "left")
map_PostLimb_lh_filtered = functions.connectedComponents(map_PostLimb_lh)

### Lesion's mask
map_lesion_float, map_lesion_binary = roi.handleLesionmask(data_Contrast,data_Contrast_24,data_rostral_lh, data_rostral_rh,im_Contrast)

# # Matriz com as regiões de interesse 
data_roi = np.zeros(data_segleft.shape, dtype=np.uint16)
data_wm = np.zeros(data_segleft.shape, dtype=np.uint16)

data_roi[map_ML_lh == True] = 1210
data_roi[map_CP_lh_filtered == True] = 1211
data_roi[map_RN_lh_filtered == True] = 1212
data_roi[map_SN_lh_filtered == True] = 1213
data_roi[map_DN_lh_filtered == True] = 1214
data_roi[map_PSA_lh_filtered == True] = 1215
data_roi[map_STN_lh_filtered == True] = 1216
data_roi[map_PostLimb_lh_filtered == True] = 1217
data_roi[map_brainstem_lh == True] = 1218
data_wm[map_WMf_lh == True] = 1219
data_wm[map_WMh_lh == True] = 1220
data_wm[map_WMc_lh == True] = 1221

data_roi[map_ML_rh == True] = 2210
data_roi[map_CP_rh_filtered == True] = 2211
data_roi[map_RN_rh_filtered == True] = 2212
data_roi[map_SN_rh_filtered == True] = 2213
data_roi[map_DN_rh_filtered == True] = 2214
data_roi[map_PSA_rh_filtered == True] = 2215
data_roi[map_STN_rh_filtered == True] = 2216
data_roi[map_PostLimb_rh_filtered == True] = 2217
data_roi[map_brainstem_rh == True] = 2218
data_wm[map_WMf_rh == True] = 2219
data_wm[map_WMh_rh == True] = 2220
data_wm[map_WMc_rh == True] = 2221

data_nifti_subcortical = nib.Nifti1Image(data_seg, affine_segleft)
nib.save(data_nifti, "subcortical_nextbrain.nii.gz")
print("File subcortical_nextbrain.nii.gz saved")

data_nifti_roi = nib.Nifti1Image(data_roi, affine_segleft)
nib.save(data_nifti_roi, "ROIs_tracks.nii.gz")
print("File ROIs_tracks.nii.gz saved")

data_nifti_wm = nib.Nifti1Image(data_wm, affine_segleft)
nib.save(data_nifti_wm, "wm_nextbrain.nii.gz")
print("File wm_nextbrain.nii.gz saved")

data_cortical = np.where(data_freesurfer > 1000, data_freesurfer, 0) # Seleciona apenas as regiões corticais
data_cortical[data_cortical == 1148] = 0
data_cortical = np.zeros(data_freesurfer.shape, dtype=np.uint16)
mask = (data_freesurfer != 0) & (data_freesurfer > 1000)
data_cortical[mask] = data_freesurfer[mask] + 2000
functions.saveImage(data_cortical, out_freesurfer, "cortical_Julich")
print("File cortical_Julich.nii.gz saved")
