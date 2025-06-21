import numpy as np
import nibabel as nib
import os
from dipy.io.streamline import load_tractogram
from dipy.io.streamline import save_tractogram
from dipy.io.stateful_tractogram import StatefulTractogram, Space
from scipy.spatial.distance import euclidean
from scipy.stats import zscore
from scipy.spatial import ConvexHull
from scipy.spatial import QhullError
from scipy.ndimage import gaussian_filter
from collections import defaultdict
from itertools import combinations
from joblib import Parallel, delayed
from tqdm import tqdm

#Local libraries
import functions

def handleStreamlinefilter(track, im_ref, data_thalamus, hemisphere, limiar):
	
	data_ref = im_ref.get_fdata().astype(np.uint16)
	mask_tract = np.zeros(data_ref.shape, dtype=np.uint16)
	
	if (hemisphere == 'left'):
		hem = 'lh'
	elif (hemisphere == 'right'):
		hem = 'rh'
	else:
		print("hemisphere must be left or right")
	
	# Limites inferior e superior
	kmin = np.where(data_thalamus != 0)[2].min()
	kmax = np.where(data_thalamus != 0)[2].max()
	
	# Affine
	affine = img_ref.affine
	inv_affine = np.linalg.inv(affine)
	
	# Carregar streamlines 
	tractogram = load_tractogram("track_" + track + "_" + hem + ".tck", img_ref)
	streamlines = tractogram.streamlines
	print("Streamlines loaded")
	
	# Converter pontos para coordenadas de voxel
	def to_voxel_coords(streamline):
		return nib.affines.apply_affine(inv_affine, streamline)
	streamlines_vox = [to_voxel_coords(s) for s in streamlines]
	
	centroides, z_scores = handleDistancescore(streamlines_vox, kmin, kmax)
	
	streamlines_filtered = [
		streamlines[i] for i in range(len(streamlines_vox)) if z_scores[i] < limiar
	]
	
	sft = StatefulTractogram(
		streamlines_filtered,
		reference=img_ref,
		space=Space.RASMM
	)

	save_tractogram(sft, "track_" + track + "_" + hem + "_filtered.tck")
	print(f"File track_{track}_{hem}_filtered.tck saved")
	
	n_filtered = 0
	for idx in range(len(streamlines_vox)):
		if z_scores[idx] < limiar:
			n_filtered += 1
			for k in centroides[idx]:
				for i,j in centroides[idx][k]:
					mask_tract[i,j,k] = 1
					
	print(f"{n_filtered} streamlines after the process({track})")
	
	# #Axial
	# mask_tract_filtered = np.zeros(data_ref.shape, dtype=np.uint16)
	# print(f"{data_ref.shape[2]} axial slices")
	# for k in range (data_ref.shape[2]):
		# label_mask, num_labels = label(mask_tract[:,:,k],connectivity=1 ,return_num=True)
		# if(num_labels != 0):
			# for n in range (1, num_labels + 1):
				# label_temp = np.zeros(mask_tract[:,:,k].shape, dtype=np.uint16)
				# label_temp[label_mask == n] = True
				# # if k > kmax:	
					# # if (np.sum(label_temp) > 2):
						# # try:
							# # label_temp_filled = functions.fillConvex_hull_slice(label_temp)
							# # mask_tract_filtered[:,:,k] = np.logical_or(mask_tract_filtered[:,:,k],label_temp_filled)
						# # except QhullError:
							# # mask_tract_filtered[:,:,k] = np.logical_or(mask_tract_filtered[:,:,k],label_temp)
					# # else:
						# # mask_tract_filtered[:,:,k] = np.logical_or(mask_tract_filtered[:,:,k],label_temp)
				# # else:
				# if (np.sum(label_temp) > 10):
					# try:
						# label_temp_filled = functions.fillConvex_hull_slice(label_temp)
						# mask_tract_filtered[:,:,k] = np.logical_or(mask_tract_filtered[:,:,k],label_temp_filled)
					# except QhullError:
						# mask_tract_filtered[:,:,k] = np.logical_or(mask_tract_filtered[:,:,k],label_temp)
	
	chunk_size = 64
	chunks = [
		mask_tract[i:i+chunk_size, j:j+chunk_size, k:k+chunk_size]
		for i in range(0, 640, chunk_size)
		for j in range(0, 640, chunk_size)
		for k in range(0, 640, chunk_size)
	]

	# Processa chunks em paralelo
	results = Parallel(n_jobs=os.cpu_count())(
		delayed(functions.process_chunk)(chunk) for chunk in chunks
	)

	# Recompõe a imagem
	filled_data = np.zeros_like(mask_tract)
	idx = 0
	for i in range(0, 640, chunk_size):
		for j in range(0, 640, chunk_size):
			for k in range(0, 640, chunk_size):
				filled_data[
					i:i+chunk_size, 
					j:j+chunk_size, 
					k:k+chunk_size
				] = results[idx]
				idx += 1
				
	# Suavização Gaussiana
	smoothed = gaussian_filter(filled_data.astype(float), sigma=2)
	smoothed_binary = (smoothed > 0.5).astype(np.uint8)

	# Salva como NIfTI
	nifti_tract = nib.Nifti1Image(smoothed_binary, im_ref.affine)
	nib.save(nifti_tract,f"track_{track}_{hem}.nii.gz")

def handleDistancescore(streamlines_vox, kmin, kmax):
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

	n = len(streamlines_vox)
	distancias_totais = np.zeros(n)
	
	# 1. Pré-processamento de dados
	print("Pré-processando centroides...")
	centroides_array = np.zeros((n, kmax+1, 2), dtype=np.float32)  # [streamline, fatia, coord]
	fatias_validas = [set() for _ in range(n)]

	for i in range(len(centroides_por_fatia)):
		for k in centroides_por_fatia[i]:
			#if kmin < k < kmax:
			if k < kmax:
				centroides_array[i,k] = centroides_por_fatia[i][k]
				fatias_validas[i].add(k)

	# 2. Cálculo otimizado por pares únicos
	print("Calculando distâncias...")
	distancias_totais = np.zeros(n, dtype=np.float32)
	pares = list(combinations(range(n), 2))

	for i, j in tqdm(pares, desc="Processando pares"):
		common_slices = fatias_validas[i] & fatias_validas[j]
		if not common_slices:
			continue
			
		# 3. Cálculo vetorizado
		slice_vec = np.array(list(common_slices))
		dist = np.linalg.norm(centroides_array[i,slice_vec] - centroides_array[j,slice_vec], axis=1)
		total = np.sum(dist)
		
		distancias_totais[i] += total
		distancias_totais[j] += total  # Simetria


	# Média das distâncias (para normalização)
	distancias_medias = distancias_totais / (n - 1)
	
	z_scores = np.abs(zscore(distancias_medias))
	
	return centroides, z_scores

	
def handleStreamlinefilterDRTT(im_ref, data_thalamus, hemisphere, limiar):
	
	data_ref = im_ref.get_fdata().astype(np.uint16)
	mask_tract = np.zeros(data_ref.shape, dtype=np.uint16)
	
	if (hemisphere == 'left'):
		hem = 'lh'
	elif (hemisphere == 'right'):
		hem = 'rh'
	else:
		print("hemisphere must be left or right")
	
	# Limites inferior e superior
	kmin = np.where(data_thalamus != 0)[2].min()
	kmax = np.where(data_thalamus != 0)[2].max()
	
	# Affine
	affine = img_ref.affine
	inv_affine = np.linalg.inv(affine)
	
	# Converter pontos para coordenadas de voxel
	def to_voxel_coords(streamline):
		return nib.affines.apply_affine(inv_affine, streamline)
	
	# Carregar streamlines ndDRTT
	tractogram = load_tractogram("track_ndDRTT_" + hem + ".tck", img_ref)
	streamlines = tractogram.streamlines
	print("Streamlines ndDRTT loaded")
	
	# Definição dos voxels
	streamlines_vox = [to_voxel_coords(s) for s in streamlines]
	
	centroides, z_scores = handleDistancescore(streamlines_vox, kmin, kmax)

	streamlines_filtered = [
		streamlines[i] for i in range(len(streamlines_vox)) if z_scores[i] < limiar
	]
	
	sft = StatefulTractogram(
		streamlines_filtered,
		reference=img_ref,
		space=Space.RASMM
	)

	save_tractogram(sft, "track_ndDRTT_" + hem + "_filtered.tck")
	print(f"File track_ndDRTT_{hem}_filtered.tck saved")
	
	n_filtered = 0
	for idx in range(len(streamlines_vox)):
		if z_scores[idx] < limiar:
			n_filtered += 1
			for k in centroides[idx]:
				for i,j in centroides[idx][k]:
					mask_tract[i,j,k] = 1
					
	print(f"{n_filtered} streamlines after the process (ndDRTT)")
	
	del tractogram, streamlines, streamlines_vox, z_scores, streamlines_filtered
	
	# Carregar streamlines dDRTT
	tractogram = load_tractogram("track_DRTT_" + hem + ".tck", img_ref)
	streamlines = tractogram.streamlines
	print("Streamlines DRTT loaded")
	
	# Definição dos voxels
	streamlines_vox = [to_voxel_coords(s) for s in streamlines]
	
	centroides, z_scores = handleDistancescore(streamlines_vox, kmin, kmax)

	streamlines_filtered = [
		streamlines[i] for i in range(len(streamlines_vox)) if z_scores[i] < limiar
	]
	
	sft = StatefulTractogram(
		streamlines_filtered,
		reference=img_ref,
		space=Space.RASMM
	)

	save_tractogram(sft, "track_dDRTT_" + hem + "_filtered.tck")
	print(f"File track_dDRTT_{hem}_filtered.tck saved")
	
	n_filtered = 0
	for idx in range(len(streamlines_vox)):
		if z_scores[idx] < limiar:
			n_filtered += 1
			for k in centroides[idx]:
				for i,j in centroides[idx][k]:
					mask_tract[i,j,k] = 1
					
	print(f"{n_filtered} streamlines after the process (dDRTT)")
	
	chunk_size = 64
	chunks = [
		mask_tract[i:i+chunk_size, j:j+chunk_size, k:k+chunk_size]
		for i in range(0, 640, chunk_size)
		for j in range(0, 640, chunk_size)
		for k in range(0, 640, chunk_size)
	]

	# Processa chunks em paralelo
	results = Parallel(n_jobs=os.cpu_count())(
		delayed(functions.process_chunk)(chunk) for chunk in chunks
	)

	# Recompõe a imagem
	filled_data = np.zeros_like(mask_tract)
	idx = 0
	for i in range(0, 640, chunk_size):
		for j in range(0, 640, chunk_size):
			for k in range(0, 640, chunk_size):
				filled_data[
					i:i+chunk_size, 
					j:j+chunk_size, 
					k:k+chunk_size
				] = results[idx]
				idx += 1
				
	# Suavização Gaussiana
	smoothed = gaussian_filter(filled_data.astype(float), sigma=2)
	smoothed_binary = (smoothed > 0.5).astype(np.uint8)

	# Salva como NIfTI
	nifti_tract = nib.Nifti1Image(smoothed_binary, im_ref.affine)
	nib.save(nifti_tract,f"track_DRTT_{hem}.nii.gz")

# Main
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
	handleStreamlinefilterDRTT(img_ref, data_thalamus_lh, hemisphere, 2)
	handleStreamlinefilter("CST", img_ref, data_thalamus_lh, hemisphere, 2)
	handleStreamlinefilter("ML", img_ref, data_thalamus_lh, hemisphere, 2)

elif (hemisphere == 'right'):
	img_ref = nib.load("../Segmentation/thalamus_mask_rh.nii.gz")
	im_thalamus_rh = nib.load("../Segmentation/thalamus_mask_dwi_rh.nii.gz")
	data_thalamus_rh = img_ref.get_fdata().astype(bool) 
	del im_thalamus_rh
	print("Data loaded")
	handleStreamlinefilterDRTT(img_ref, data_thalamus_rh, hemisphere, 2)
	handleStreamlinefilter("CST", img_ref, data_thalamus_rh, hemisphere, 2)
	handleStreamlinefilter("ML", img_ref, data_thalamus_rh, hemisphere, 2)


# handleStreamlinefilter("ndDRTT", img_ref, data_thalamus_lh, hemisphere, 2)
# handleStreamlinefilter("DRTT", img_ref, data_thalamus_lh, hemisphere, 2)
# handleStreamlinefilter("CST", img_ref, data_thalamus_lh, hemisphere, 2)
# handleStreamlinefilter("ML", img_ref, data_thalamus_lh, hemisphere, 2)

