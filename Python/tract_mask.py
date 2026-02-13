import numpy as np
import nibabel as nib
import os
from dipy.io.streamline import load_tractogram
from dipy.io.streamline import save_tractogram
from dipy.io.stateful_tractogram import StatefulTractogram, Space
from collections import defaultdict
import sys

def handleStreamlinemask(track, im_ref, data_thalamus, hemisphere):
	data_ref = im_ref.get_fdata().astype(np.uint16)
	mask_tract = np.zeros(data_ref.shape, dtype=np.uint16)
	mask_inf_sup = np.zeros(data_ref.shape, dtype=np.uint16)
	
	if (hemisphere == 'left'):
		hem = 'lh'
	elif (hemisphere == 'right'):
		hem = 'rh'
	else:
		print("hemisphere must be left or right")
	
	# Carregar streamlines 
	tractogram = load_tractogram("track_" + track + "_" + hem + "_tmp.tck", img_ref)
	streamlines = tractogram.streamlines
	print("Streamlines loaded")
	
	# Limites inferior e superior
	kmin = np.where(data_thalamus != 0)[2].min()
	kmax = np.where(data_thalamus != 0)[2].max()
	
	# Converter pontos para coordenadas de voxel
	affine = img_ref.affine
	inv_affine = np.linalg.inv(affine)
	def to_voxel_coords(streamline):
		return nib.affines.apply_affine(inv_affine, streamline)
	streamlines_vox = [to_voxel_coords(s) for s in streamlines]
	print(len(streamlines_vox))
	
	# Estrutura para armazenar centroides por fatia (k)
	centroides = [defaultdict(list) for _ in streamlines_vox]

	for idx, streamline in enumerate(streamlines_vox):
		for point in streamline:
			i, j, k = np.round(point).astype(int)  # Arredonda para índice de voxel
			centroides[idx][k].append((i, j))  # Agrupa por fatia k

	# Calcular centroide médio por fatia para cada streamline
	centroides_por_fatia = []
	for idx in range(len(streamlines_vox)):
		centroides_streamline = {}
		for k in centroides[idx]:
		  pontos_k = centroides[idx][k]
		  if pontos_k != "":
			  centroide_k = np.mean(pontos_k, axis=0)
			  centroides_streamline[k] = centroide_k
		  else:
			  print(f'streamline = {idx}, fatia = {k}')
		centroides_por_fatia.append(centroides_streamline)
	print("Centro por fatia")
	
	#for k in range (kmin, kmax):
	for k in range (0, kmax):
		sum_k_iaxis = 0
		sum_k_jaxis = 0
		count = 0
		for streamline in range(len(streamlines_vox)):
			if k in centroides_por_fatia[streamline]:
				sum_k_iaxis = sum_k_iaxis + centroides_por_fatia[streamline][k][0]	
				sum_k_jaxis = sum_k_jaxis + centroides_por_fatia[streamline][k][1]
				count += 1
		if count != 0:
			avg_iaxis = np.round(sum_k_iaxis/count).astype(int)
			avg_jaxis = np.round(sum_k_jaxis/count).astype(int)
			mask_tract[avg_iaxis,avg_jaxis,k] = 1
	
	data_nifti_tract = nib.Nifti1Image(mask_tract, affine)
	nib.save(data_nifti_tract, f"mask_track_{track}_{hem}.nii.gz")
	print(f"File mask_track_{track}_{hem}_tmp.nii.gz saved")
	
	mask_inf_sup[:,:,:kmax] = 1
	
	data_nifti_inf_sup = nib.Nifti1Image(mask_inf_sup, affine)
	nib.save(data_nifti_inf_sup, f"mask_inf_sup.nii.gz")


# Main
## Definição do trato
if len(sys.argv) > 1:
    track = sys.argv[1]
    print(f"Track: {track}")
else:
    print("Nenhum argumento fornecido")

## Leitura do hemisfério
with open('../Segmentation/hemisphere.txt', 'r', encoding='utf-8') as file_hemisphere:
    hemisphere = file_hemisphere.read()  
print(f"{hemisphere} hemisphere")

if (hemisphere == 'left'):
	img_ref = nib.load("../Segmentation/thalamus_mask_lh.nii.gz")
	im_thalamus_lh = nib.load("../Segmentation/thalamus_mask_dwi_lh.nii.gz")
	data_thalamus_lh = img_ref.get_fdata().astype(bool) 
	del im_thalamus_lh
	print("Data loaded")
	handleStreamlinemask(track,im_ref,data_thalamus_lh,hemisphere)
	
elif (hemisphere == 'right'):
	img_ref = nib.load("../Segmentation/thalamus_mask_rh.nii.gz")
	im_thalamus_rh = nib.load("../Segmentation/thalamus_mask_dwi_rh.nii.gz")
	data_thalamus_rh = img_ref.get_fdata().astype(bool) 
	del im_thalamus_rh
	print("Data loaded")
	handleStreamlinemask(track,img_ref,data_thalamus_rh,hemisphere)
else:
	print("hemisphere must be left or right")


