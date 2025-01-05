# Local libraries
import functions
import roi_definition as roi

# External libraries
import nibabel as nib
import numpy as np

# Main
## Load files
out_freesurfer = nib.load("output_freesurfer.nii.gz")
NRp_lh = nib.load("NRp_lh_coreg_weighted_transformed.nii.gz")
NRp_rh = nib.load("NRp_rh_coreg_weighted_transformed.nii.gz")
NRm_lh = nib.load("NRm_lh_coreg_weighted_transformed.nii.gz")
NRm_rh = nib.load("NRm_rh_coreg_weighted_transformed.nii.gz")
SNc_lh = nib.load("SNc_lh_coreg_weighted_transformed.nii.gz")
SNc_rh = nib.load("SNc_rh_coreg_weighted_transformed.nii.gz")
SNr_lh = nib.load("SNr_lh_coreg_weighted_transformed.nii.gz")
SNr_rh = nib.load("SNr_rh_coreg_weighted_transformed.nii.gz")
DNd_lh = nib.load("DNd_lh_coreg_weighted_transformed.nii.gz")
DNd_rh = nib.load("DNd_rh_coreg_weighted_transformed.nii.gz")
DNv_lh = nib.load("DNv_lh_coreg_weighted_transformed.nii.gz")
DNv_rh = nib.load("DNv_rh_coreg_weighted_transformed.nii.gz")
print(".Files loaded")

## Extract data from image
data_freesurfer = out_freesurfer.get_fdata().astype(np.uint32)
data_NRpLh = NRp_lh.get_fdata()
data_NRpRh = NRp_rh.get_fdata()
data_NRmLh = NRm_lh.get_fdata()
data_NRmRh = NRm_rh.get_fdata()
data_SNcLh = SNc_lh.get_fdata()
data_SNcRh = SNc_rh.get_fdata()
data_SNrLh = SNr_lh.get_fdata()
data_SNrRh = SNr_rh.get_fdata()
data_DNdLh = DNd_lh.get_fdata()
data_DNdRh = DNd_rh.get_fdata()
data_DNvLh = DNv_lh.get_fdata()
data_DNvRh = DNv_rh.get_fdata()
print(".Data loaded")

## RIGHT HEMISPHERE

### Join regions of probabilistic atlas 
data_NR_rh = data_NRpRh + data_NRmRh
data_NR_rh[data_NR_rh > 1] = 1

data_SN_rh = data_SNcRh + data_SNrRh
data_SN_rh[data_SN_rh > 1] = 1

data_DN_rh = data_DNdRh + data_DNvRh
data_DN_rh[data_DN_rh > 1] = 1

### Red Nucleus
map_NR_rh = roi.handleRednucleus(150,data_freesurfer,data_NR_rh,data_SN_rh,60,"right")
### Substantia nigra
map_SN_rh = roi.handleSubstantianigra(130,data_freesurfer,data_SN_rh,data_NR_rh,60,"right")
### Dentante nucleus
map_DN_rh = roi.handleDentatenucleus(1400,data_freesurfer,data_DN_rh,46,"right")
### Medial Lemniscus
map_ML_rh = roi.handleMediallemniscus(data_freesurfer,map_NR_rh,map_SN_rh,60,"right")
### Cerebral Peduncle
map_CP_rh = roi.handleCerebralpeduncle(data_freesurfer,map_NR_rh,map_SN_rh,41,"right")

## LEFT HEMISPHERE

### Join regions of probabilistic atlas 
data_NR_lh = data_NRpLh + data_NRmLh
data_NR_lh[data_NR_lh > 1] = 1

data_SN_lh = data_SNcLh + data_SNrLh
data_SN_lh[data_SN_lh > 1] = 1

data_DN_lh = data_DNdLh + data_DNvLh
data_DN_lh[data_DN_lh > 1] = 1

### Red Nucleus
map_NR_lh = roi.handleRednucleus(150,data_freesurfer,data_NR_lh,data_SN_lh,28,"left")
### Substantia nigra
map_SN_lh = roi.handleSubstantianigra(130,data_freesurfer,data_SN_lh,data_NR_lh,28,"left")
### Dentante nucleus
map_DN_lh = roi.handleDentatenucleus(1400,data_freesurfer,data_DN_lh,7,"left")
### Medial Lemniscus
map_ML_lh = roi.handleMediallemniscus(data_freesurfer,map_NR_lh,map_SN_lh,28,"left")
### Cerebral Peduncle
map_CP_lh = roi.handleCerebralpeduncle(data_freesurfer,map_NR_lh,map_SN_lh,2,"left")

## Julich Parcels
julich_parcels = np.where(data_freesurfer > 1000, data_freesurfer, 0)
julich_parcels[julich_parcels == 1148] = 0
julich_parcels[map_ML_lh != 0] = 1210
julich_parcels[map_CP_lh != 0] = 1211
julich_parcels[map_NR_lh != 0] = 1212
julich_parcels[map_SN_lh != 0] = 1213
julich_parcels[map_DN_lh != 0] = 1214
julich_parcels[map_ML_rh != 0] = 2210
julich_parcels[map_CP_rh != 0] = 2211
julich_parcels[map_NR_rh != 0] = 2212
julich_parcels[map_SN_rh != 0] = 2213
julich_parcels[map_DN_rh != 0] = 2214

functions.saveImage(julich_parcels, out_freesurfer, "Julich_parcels_freesurfer")
print("File Julich_parcels_freesurfer.nii.gz saved")
