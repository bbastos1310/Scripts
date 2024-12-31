# External libraries
import nibabel as nib
import matplotlib.pyplot as plt
import numpy as np
from skimage.morphology import square, closing
from scipy.ndimage import binary_dilation

# local libraries
import functions

def handleMaskextraction (data_freesurfer, out_freesurfer, name_midbrain, name_ventricle):
	
	# # Cerebellum extraction
	# ## Mask with cerebellum voxels
	# mask_cerebellum = np.zeros(data_freesurfer.shape, dtype = np.uint8)
	# #mask_cerebellum[(data_freesurfer == 8) | (data_freesurfer == 47)] = 1
	# mask_cerebellum[(data_freesurfer == 7) | (data_freesurfer == 46)] = 1
	
	# ## Dilation 
	# mask_cerebellum_dilated = np.zeros(data_freesurfer.shape, dtype = np.uint8)

	# kernel = np.ones((5, 5), dtype=bool)
	# for j in range (mask_cerebellum.shape[1]):
		# mask_cerebellum_dilated[:,j,:] = binary_dilation(mask_cerebellum[:,j,:], structure=kernel)
	
	# ## Closing
	# mask_cerebellum_closed = np.zeros(data_freesurfer.shape, dtype = np.uint8)
	# for j in range (mask_cerebellum.shape[1]):
		# mask_cerebellum_closed[:,j,:] = closing(mask_cerebellum_dilated[:,j,:], square(6))
	
	# functions.saveImage(mask_cerebellum_closed, out_freesurfer, "mask_cerebellum")
	# print(".File mask_cerebellum.nii.gz saved")
	
	## MIDBRAIN EXTRACTION
	brainstem_coordinadates = np.where(data_freesurfer == 16)
	left_ventralDC_coordinates = np.where(data_freesurfer == 28)
	right_ventralDC_coordinates = np.where(data_freesurfer == 60)	
	
	# Min and max values
	xmax_brainstem = brainstem_coordinadates[0].max()
	xmin_brainstem = brainstem_coordinadates[0].min()
	ymax_brainstem = brainstem_coordinadates[1].max()
	ymin_brainstem = brainstem_coordinadates[1].min()
	zmax_brainstem = brainstem_coordinadates[2].max()
	zmin_brainstem = brainstem_coordinadates[2].min()

	xmax_leftventralDC = left_ventralDC_coordinates[0].max()
	xmin_leftventralDC = left_ventralDC_coordinates[0].min()
	ymax_leftventralDC = left_ventralDC_coordinates[1].max()
	ymin_leftventralDC = left_ventralDC_coordinates[1].min()
	zmax_leftventralDC = left_ventralDC_coordinates[2].max()
	zmin_leftventralDC = left_ventralDC_coordinates[2].min()

	xmax_rightventralDC = right_ventralDC_coordinates[0].max()
	xmin_rightventralDC = right_ventralDC_coordinates[0].min()
	ymax_rightventralDC = right_ventralDC_coordinates[1].max()
	ymin_rightventralDC = right_ventralDC_coordinates[1].min()
	zmax_rightventralDC = right_ventralDC_coordinates[2].max()
	zmin_rightventralDC = right_ventralDC_coordinates[2].min()	
	
	# Region of midbrain
	mask_midbrain = np.zeros(data_freesurfer.shape, dtype = np.uint8)

	xmin = xmin_rightventralDC - 5
	xmax = xmax_leftventralDC + 5

	ymin = np.min((ymin_leftventralDC, ymin_rightventralDC)) - 5
	ymax = np.max((ymax_leftventralDC, ymax_rightventralDC)) + 5


	zmin = zmin_brainstem - 5
	zmax = np.max((zmax_leftventralDC, zmax_rightventralDC)) + 5
	
	# Mask of midbrain
	mask_midbrain[xmin:xmax, ymin:ymax, zmin:zmax] = 1
	
	functions.saveImage(mask_midbrain, out_freesurfer, name_midbrain)
	print(f"File {name_midbrain}.nii.gz salvo")
		
	## Mask with VentralDC voxels
	# mask_ventralDC = np.zeros(data_freesurfer.shape, dtype = np.uint8)
	# mask_ventralDC[(data_freesurfer == 28) | (data_freesurfer == 60)] = 1
	
	# ## Dilation 
	# mask_ventralDC_dilated = np.zeros(data_freesurfer.shape, dtype = np.uint8)

	# for j in range (mask_ventralDC.shape[1]):
		# mask_ventralDC_dilated[:,j,:] = binary_dilation(mask_ventralDC[:,j,:], structure=kernel)
	
	# ## Closing
	# mask_ventralDC_closed = np.zeros(data_freesurfer.shape, dtype = np.uint8)
	# for j in range (mask_ventralDC.shape[1]):
		# mask_ventralDC_closed[:,j,:] = closing(mask_ventralDC_dilated[:,j,:], square(6))
	
	# functions.saveImage(mask_ventralDC_closed, out_freesurfer, "mask_ventralDC_closed")
	# print(".File mask_ventralDC_closed.nii.gz saved")
	
	## MASK OF THE 4TH VENTRICLE
	ventricle_coordinadates = np.where(data_freesurfer == 15)
	
	# min and max values
	xmax_ventricle = ventricle_coordinadates[0].max()
	xmin_ventricle = ventricle_coordinadates[0].min()
	ymax_ventricle = ventricle_coordinadates[1].max()
	ymin_ventricle = ventricle_coordinadates[1].min()
	zmax_ventricle = ventricle_coordinadates[2].max()
	zmin_ventricle = ventricle_coordinadates[2].min()
	
	# Ventricles' region
	mask_ventricle = np.zeros(data_freesurfer.shape, dtype = np.uint8)

	xmin = xmin_ventricle - 10
	xmax = xmax_ventricle + 10

	ymin = ymin_ventricle + 5
	ymax = ymax_ventricle

	zmin = zmin_ventricle - 15
	zmax = zmax_ventricle + 5
	
	# Mask of the 4th ventricle
	mask_ventricle[xmin:xmax, ymin:ymax, zmin:zmax] = 1
	functions.saveImage(mask_ventricle, out_freesurfer, name_ventricle)
	print(f"File {name_ventricle}.nii.gz salvo")
		

# MAIN
## Load files
out_freesurfer = nib.load("output_freesurfer.nii.gz")
out_mni_freesurfer = nib.load("output_mni_freesurfer_coreg.nii.gz")
print(".Files loaded")

## Extract data from image
data_freesurfer = out_freesurfer.get_fdata().astype(np.int32)
data_mni = out_mni_freesurfer.get_fdata().astype(np.int32)
print(".Data loaded")

## Extract mask
handleMaskextraction(data_freesurfer, out_freesurfer, "mask_midbrain", "mask_ventricle")	
handleMaskextraction(data_mni, out_mni_freesurfer, "mask_midbrain_coreg", "mask_ventricle_coreg")
