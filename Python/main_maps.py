# Local libraries
import functions

# External libraries
import nibabel as nib

# Main function
# Load Files
adc_map = nib.load("Maps/adc_map.nii.gz")
adc_map_24 = nib.load("Maps/adc_map_24.nii.gz")
ad_map = nib.load("Maps/ad_map.nii.gz")
ad_map_24 = nib.load("Maps/ad_map_24.nii.gz")
cl_map = nib.load("Maps/cl_map.nii.gz")
cl_map_24 = nib.load("Maps/cl_map_24.nii.gz")
cp_map = nib.load("Maps/cp_map.nii.gz")
cp_map_24 = nib.load("Maps/cp_map_24.nii.gz")
cs_map = nib.load("Maps/cs_map.nii.gz")
cs_map_24 = nib.load("Maps/cs_map_24.nii.gz")
fa_map = nib.load("Maps/fa_map_abs.nii.gz")
fa_map_24 = nib.load("Maps/fa_map_24_abs.nii.gz")
rd_map = nib.load("Maps/rd_map.nii.gz")
rd_map_24 = nib.load("Maps/rd_map_24.nii.gz")
mask_image = nib.load("dwi_mask_up_reg.nii.gz")
print("-Filed loaded")

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
data_mask = mask_image.get_fdata()
print("-Data loaded")

functions.handleMapsonechannel(data_adcmap, adc_map, data_adcmap24, adc_map_24, data_mask, "ADCmap")
functions.handleMapsonechannel(data_admap, ad_map, data_admap24, ad_map_24, data_mask, "ADmap")
functions.handleMapsonechannel(data_clmap, cl_map, data_clmap24, cl_map_24, data_mask, "CLmap")
functions.handleMapsonechannel(data_cpmap, cp_map, data_cpmap24, cp_map_24, data_mask, "CPmap")
functions.handleMapsonechannel(data_csmap, cs_map, data_csmap24, cs_map_24, data_mask, "CSmap")
functions.handleMapsthreechannel(data_famap[:,:,:,0], fa_map, data_famap24[:,:,:,0], fa_map_24, data_mask, "FAmap_Red")
functions.handleMapsthreechannel(data_famap[:,:,:,1], fa_map, data_famap24[:,:,:,1], fa_map_24, data_mask, "FAmap_Green")
functions.handleMapsthreechannel(data_famap[:,:,:,2], fa_map, data_famap24[:,:,:,2], fa_map_24, data_mask, "FAmap_Blue")
functions.handleMapsonechannel(data_rdmap, rd_map, data_rdmap24, rd_map_24, data_mask, "RDmap")		
