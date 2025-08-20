# Local libraries
import functions
import roi_definition as roi

# External libraries
import nibabel as nib
import numpy as np

# Main
## Load files

im_segleft = nib.load("seg_left_resampled.nii.gz") # saída da segmentação do mri_histo (hemisfério esquerdo)
im_segright = nib.load("seg_right_resampled.nii.gz") # saída da segmentação do mri_histo (hemisfério direito)
im_thalamus_lh = nib.load("thalamus_mask_lh.nii.gz")
im_thalamus_rh = nib.load("thalamus_mask_rh.nii.gz")
im_FAmap = nib.load("Maps/FAmap_up.nii.gz")
print(".Files loaded")

## Extract data from image
data_segleft = im_segleft.get_fdata().astype(np.uint16) # (640x640x640)
data_segright = im_segright.get_fdata().astype(np.uint16) # (640x640x640)
data_thalamus_lh = im_thalamus_lh.get_fdata().astype(bool) 
data_thalamus_rh = im_thalamus_rh.get_fdata().astype(bool) 
data_FAmap = im_FAmap.get_fdata().astype(np.uint8) 
print(".Data loaded")

# Armazenar o affine das imagens para uso posterior
affine_segleft = im_segleft.affine
affine_segright = im_segright.affine

# Matriz para armazenar as informações dos dois hemisférios juntos 
data_seg = np.zeros(data_segleft.shape, dtype=np.uint16)

# Criar uma máscara para os valores que devem ser mantidos
mask_right = (data_segright < 1000) & (data_segright != 0)
mask_left = (data_segleft < 1000) & (data_segleft != 0)

# Diferenciar os valores entre os hemisférios

data_seg[mask_right] = data_segright[mask_right] + 1000
data_seg[mask_left] = data_segleft[mask_left]

del mask_right, mask_left

# Normalizar FAmap
functions.normalizeFAmap(im_FAmap)
del data_FAmap, im_FAmap
im_FAmap = nib.load("Maps/FAmap_up_normalized.nii.gz")
data_FAmap = im_FAmap.get_fdata().astype(np.uint16)

## RIGHT HEMISPHERE

### Posterior limb of internal capsule
map_PostLimb_rh = roi.handlePosteriorLimb(data_seg,data_FAmap, data_thalamus_rh, "right")
map_PostLimb_rh_filtered = functions.connectedComponents(map_PostLimb_rh)

## LEFT HEMISPHERE

### Posterior limb of internal capsule
map_PostLimb_lh = roi.handlePosteriorLimb(data_seg,data_FAmap, data_thalamus_lh, "left")
map_PostLimb_lh_filtered = functions.connectedComponents(map_PostLimb_lh)

# Matriz com as regiões de interesse 
data_roi = np.zeros(data_segleft.shape, dtype=np.uint16)

data_roi[map_PostLimb_lh_filtered == True] = 1008

data_roi[map_PostLimb_rh_filtered == True] = 2008

data_nifti_roi = nib.Nifti1Image(data_roi, affine_segleft)
nib.save(data_nifti_roi, "ROIs_tracks_teste.nii.gz")
print("File ROIs_tracks_teste.nii.gz saved")




