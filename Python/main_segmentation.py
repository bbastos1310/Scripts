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
im_synthseg = nib.load("SynthSeg_resampled.nii.gz") # saída da segmentação do mri_histo (equivalente à segmentação subcortical do freesurfer)
print(".Files loaded")

## Extract data from image
data_freesurfer = out_freesurfer.get_fdata().astype(np.uint16) # (256x256x256)
data_segleft = im_segleft.get_fdata().astype(np.uint16) # (640x640x640)
data_segright = im_segright.get_fdata().astype(np.uint16) # (640x640x640)
data_synthseg = im_synthseg.get_fdata().astype(np.uint16) # (640x640x640)
print(".Data loaded")

# Armazenar o affine das imagens para uso posterior
affine_segleft = im_segleft.affine
affine_segright = im_segright.affine
affine_synthseg = im_synthseg.affine

del im_segleft, im_segright, im_synthseg # deletar as imagens da memória já que possuem resolução alta 

# Matriz para armazenar as informações dos dois hemisférios juntos 
data_seg = np.zeros(data_segleft.shape, dtype=np.uint16)

# Criar uma máscara para os valores que devem ser mantidos
mask_right = (data_segright < 1000) & (data_segright != 0)
mask_left = (data_segleft < 1000) & (data_segleft != 0)

# Substituir os valores fora da máscara por 0
data_seg[mask_right] = data_segright[mask_right] + 1000
data_seg[mask_left] = data_segleft[mask_left]

del mask_right, mask_left

## RIGHT HEMISPHERE

### Red Nucleus
map_RN_rh = np.array(np.where(data_seg == 1385, True, False), dtype=bool)
### Substantia nigra
map_SN_rh = np.array(np.where((data_seg == 1310) | (data_seg == 1352), True, False), dtype=bool)
### Dentante nucleus
map_DN_rh = np.array(np.where(data_seg == 1721, True, False), dtype=bool)
### Subthalamic nucleus
map_STN_rh = np.array(np.where((data_seg == 1315) | (data_seg == 1316) | (data_seg == 1321), True, False), dtype=bool)
### Medial Lemniscus
map_ML_rh = roi.handleMediallemniscus(data_seg,map_RN_rh,"right")
### Cerebral Peduncle
map_CP_rh = roi.handleCerebralpeduncle(data_seg, data_synthseg, map_RN_rh,"right")
### Posterior subthalamic area
map_PSA_rh = roi.handlePsa(data_seg,map_RN_rh, map_STN_rh,"right")

# ## LEFT HEMISPHERE

### Red Nucleus
map_RN_lh = np.array(np.where(data_seg == 385, True, False), dtype=bool)
### Substantia nigra
map_SN_lh = np.array(np.where((data_seg == 310) | (data_seg == 352), True, False), dtype=bool)
### Dentante nucleus
map_DN_lh = np.array(np.where(data_seg == 721, True, False), dtype=bool)
### Subthalamic nucleus
map_STN_lh = np.array(np.where((data_seg == 315) | (data_seg == 316) | (data_seg == 321), True, False), dtype=bool)
### Medial Lemniscus
map_ML_lh = roi.handleMediallemniscus(data_seg,map_RN_lh,"left")
### Cerebral Peduncle
map_CP_lh = roi.handleCerebralpeduncle(data_seg, data_synthseg, map_RN_lh,"left")
### Posterior subthalamic area
map_PSA_lh = roi.handlePsa(data_seg,map_RN_lh, map_STN_lh,"left")

# Matriz com as regiões de interesse 
data_roi = np.zeros(data_segleft.shape, dtype=np.uint16)

data_roi[map_ML_lh == True] = 1210
data_roi[map_CP_lh == True] = 1211
data_roi[map_RN_lh == True] = 1212
data_roi[map_SN_lh == True] = 1213
data_roi[map_DN_lh == True] = 1214
data_roi[map_PSA_lh == True] = 1215

data_roi[map_ML_rh == True] = 2210
data_roi[map_CP_rh == True] = 2211
data_roi[map_RN_rh == True] = 2212
data_roi[map_SN_rh == True] = 2213
data_roi[map_DN_rh == True] = 2214
data_roi[map_PSA_rh == True] = 2215

data_nifti = nib.Nifti1Image(data_roi, affine_segleft)
nib.save(data_nifti, "mask_ROI_teste.nii.gz")

## Julich Parcels
julich_parcels = np.where(data_freesurfer > 1000, data_freesurfer, 0) # Seleciona apenas as regiões corticais
julich_parcels[julich_parcels == 1148] = 0

functions.saveImage(julich_parcels, out_freesurfer, "Julich_parcels_freesurfer")
print("File Julich_parcels_freesurfer.nii.gz saved")
