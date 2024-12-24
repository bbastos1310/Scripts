# Local libraries
import functions
import lesionDetection
import maps
import matrix

# External libraries
import nibabel as nib
import pandas as pd

# Main function
# Load Files
adc_map = nib.load("adc_map.nii.gz")
adc_map_24 = nib.load("adc_map_24.nii.gz")
ad_map = nib.load("ad_map.nii.gz")
ad_map_24 = nib.load("ad_map_24.nii.gz")
cl_map = nib.load("cl_map.nii.gz")
cl_map_24 = nib.load("cl_map_24.nii.gz")
cp_map = nib.load("cp_map.nii.gz")
cp_map_24 = nib.load("cp_map_24.nii.gz")
cs_map = nib.load("cs_map.nii.gz")
cs_map_24 = nib.load("cs_map_24.nii.gz")
fa_map = nib.load("fa_map_abs.nii.gz")
fa_map_24 = nib.load("fa_map_24_abs.nii.gz")
rd_map = nib.load("rd_map.nii.gz")
rd_map_24 = nib.load("rd_map_24.nii.gz")
T1_raw = nib.load("T1.nii.gz")
T1_raw_24 = nib.load("T1_24_coreg.nii.gz")
T1_seg = nib.load("Julich_parcels_ordered.nii.gz")
mask_image = nib.load("dwi_mask_up_reg.nii.gz")
Contrast = nib.load("Contrast_coreg_resampled.nii.gz")
Contrast_24 = nib.load("Contrast_24_coreg_resampled.nii.gz")
matrix_PRE = pd.read_csv("Julich.csv", header = None, sep = " ")
matrix_24 = pd.read_csv("Julich_24.csv", header = None, sep = " ")
print("-Arquivos carregados")

# Extract data
data_adcmap = adc_map.get_fdata()
data_adcmap24 = adc_map_24.get_fdata()
data_admap = ad_map.get_fdata()
data_admap24 = ad_map_24.get_fdata()
data_clmap = cl_map.get_fdata()
data_clmap24 = cl_map_24.get_fdata()
data_cpmap = cp_map.get_fdata()
data_cpmap24 = cp_map_24.get_fdata()
data_csmap = cs_map.get_fdata()
data_csmap24 = cs_map_24.get_fdata()
data_famap = fa_map.get_fdata()
data_famap24 = fa_map_24.get_fdata()
data_rdmap = rd_map.get_fdata()
data_rdmap24 = rd_map_24.get_fdata()
data_T1 = T1_raw.get_fdata()
data_T1_24 = T1_raw_24.get_fdata()
data_T1seg = T1_seg.get_fdata()
data_mask = mask_image.get_fdata()
data_contrast = Contrast.get_fdata()
data_contrast_24 = Contrast_24.get_fdata () 
print("-Dados extraídos")

# Run lesion detection
lesion_coordinates = lesionDetection.handleLesionmask(data_contrast, data_contrast_24, Contrast)
maps.handleMaps(data_adcmap, adc_map, data_adcmap24, adc_map_24, data_mask, "ADCmap")
matrix.handleMatrixcreation(matrix_PRE, matrix_24)
		
