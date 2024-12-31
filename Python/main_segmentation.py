# Local libraries
import mask_extraction
import numpy as np

# External libraries
import nibabel as nib

# Main
## Load files
out_freesurfer = nib.load("output_freesurfer.nii.gz")
print(".Files loaded")

## Extract data from image
data_freesurfer = out_freesurfer.get_fdata().astype(np.int32)
print(".Data loaded")

## Extract mask
mask_extraction.handleMaskextraction(data_freesurfer, out_freesurfer)
