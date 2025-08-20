# Local libraries
import functions

# External libraries
import nibabel as nib
import numpy as np
from scipy.ndimage import binary_erosion
from skimage.measure import label, regionprops
from scipy.spatial import ConvexHull, Delaunay, KDTree
from skimage.draw import polygon
#import pandas as pd
import matplotlib.pyplot as plt
from skimage import measure
import cv2

# save nifti image
def saveImage(data, image, name):
  data_nifti = nib.Nifti1Image(data, image.affine)
  nib.save(data_nifti, name + ".nii.gz")

# Remove mask contour
def removeContour(data, mask, n_iter):

  # Aplicar erosão para remover os contornos externos
  # O parâmetro iterations controla quantas camadas externas serão removidas
  eroded_mask = binary_erosion(mask, iterations = n_iter)

  # Aplicar a máscara erodida à imagem original
  eroded_data = data * eroded_mask

  return eroded_data

# Upper bound for outliers
def upperBound(data):
  Q1 = np.percentile(data [data != 0], 25)
  Q3 = np.percentile(data [data != 0], 75)
  IQR = Q3 - Q1

  # Limite superior
  upper_bound = Q3 + 10 * IQR

  return upper_bound

# Maps treatment
def mapTreatment(data, mask):
  data = removeContour(data, mask, 2)
  data [data < 0] = 0
  data [np.isnan(data)] = 0
  upper_limit = upperBound(data)

  outliers = np.zeros(data.shape)

  # Identificar os índices dos outliers
  outliers[data > upper_limit ] = True

  # Troca os outliers pela mediana dos voxels vizinhos
  num_outliers = 0
  for x in range(outliers.shape[0]):
    for y in range(outliers.shape[1]):
      for z in range(outliers.shape[2]):
        if (outliers[x, y, z] == True):
          #print(f"Outlier: data[{x},{y},{z}] = {data[x,y,z]}")
          data[x,y,z] = np.median(data[x-2:x+1, y-2:y+1, z-2:z+1])
          num_outliers = num_outliers + 1

  data_norm = data/np.max(np.abs(data))
  data_rgb = data_norm * 255

  return data_norm, data_rgb

def handleMapsonechannel(data_map, image, data24_map, image_24, data_mask, name):
	map_treated, _ = functions.mapTreatment(data_map, data_mask)
	map24_treated, _ = functions.mapTreatment(data24_map, data_mask)
	map_subtraction = map24_treated-map_treated
	map_subtraction_norm = map_subtraction/np.max(np.abs(map_subtraction))
	name_pre = "Maps/" + name + "(PRE)"
	name_24 = "Maps/" + name + "(24H)"
	name_sub = "Maps/" + name + "(Subtraction)"
	functions.saveImage(map_treated, image, name_pre )
	functions.saveImage(map24_treated, image_24, name_24 )
	functions.saveImage(map_subtraction_norm, image, name_sub)
	print(f"{name} saved") 	

def handleMapsthreechannel(data_map, image, data24_map, image_24, data_mask, name):
	_, map_treated = functions.mapTreatment(data_map, data_mask)
	_, map24_treated = functions.mapTreatment(data24_map, data_mask)
	map_subtraction = map24_treated-map_treated
	map_subtraction_norm = map_subtraction*255/np.max(np.abs(map_subtraction))
	name_pre = "Maps/" + name + "(PRE)"
	name_24 = "Maps/" + name + "(24H)"
	name_sub = "Maps/" + name + "(Subtraction)"
	functions.saveImage(map_treated, image, name_pre )
	functions.saveImage(map24_treated, image_24, name_24 )
	functions.saveImage(map_subtraction_norm, image, name_sub)
	print(f"{name} saved") 	
	
def plotMaps(data_PRE, data_24, name):
  plt.figure(figsize=(15,5))

  plt.subplot(1,3,1)
  plt.imshow(np.rot90(data_PRE[:,69,:], k=1), cmap='gray')
  plt.colorbar()
  plt.title(name + " (PRE)")

  plt.subplot(1,3,2)
  plt.imshow(np.rot90(data_24[:,69,:], k=1),cmap='gray')
  plt.colorbar()
  plt.title( name + " (24H)")

  plt.subplot(1,3,3)
  plt.imshow(np.rot90(data_24[:,69,:]-data_PRE[:,69,:], k=1),cmap='seismic')
  plt.colorbar()
  plt.title( name + " (Subtraction)")

  plt.tight_layout()
  plt.close
  
def normalizeFAmap(img):
	data = img.get_fdata()
	normalized_data = np.zeros_like(data)
	
	# Calcular percentil 99 para cada volume e normalizar
	for vol_idx in range(data.shape[3]):
		volume_data = data[:, :, :, vol_idx]
		p99 = np.percentile(volume_data, 99)
		print(f"Volume {vol_idx}: p99 = {p99}")
		
		normalized_volume = volume_data*100 / p99
		normalized_data[:, :, :, vol_idx] = normalized_volume

	normalized_img = nib.Nifti1Image(normalized_data, img.affine, img.header)
	output_path = 'Maps/FAmap_up_normalized.nii.gz'
	nib.save(normalized_img, output_path)
	print(f"Imagem FAmap normalizada salva como: {output_path}")
  
def linearfunctionPoints(x1,y1,x2,y2):
	a = (y1-y2)/(x1-x2)
	b = y1 - a*x1
	return a,b

def linearfunctionCoeficient(a,x1,y1):
	b = y1 - a*x1
	return b
	
def fillConvex_hull_slice(slice_2d):
    """
    Extrai o convex hull dos pontos ativos no slice e preenche o interior.

    Args:
        slice_2d (np.ndarray): Slice binário 2D (0s e 1s).

    Returns:
        np.ndarray: Slice preenchido com o convex hull.
    """
    # Encontra as coordenadas (y, x) dos pontos ativos (1s)
    points = np.column_stack(np.where(slice_2d == 1))

    if len(points) < 3:
        # Não há pontos suficientes para formar um convex hull
        return slice_2d

    # Calcula o convex hull
    hull = ConvexHull(points)
    hull_points = points[hull.vertices]  # Pontos do contorno convexo

    # Ordena os pontos no sentido horário para desenhar o polígono
    hull_points = hull_points[:, ::-1]  # Inverte para (x, y)
    hull_points = np.vstack((hull_points, hull_points[0]))  # Fecha o polígono

    # Cria uma máscara preenchida do convex hull
    mask = np.zeros_like(slice_2d)
    rr, cc = polygon(hull_points[:, 0], hull_points[:, 1], mask.shape)
    mask[cc, rr] = 1

    return mask
    
def fillConvex_hull_volume(volume_3d):
    filled_volume = np.zeros_like(volume_3d)

    kmin = np.where(volume_3d == True)[2].min()
    kmax = np.where(volume_3d == True)[2].max()

    for k in range(kmin, kmax + 1):
        slice_2d = volume_3d[:,:,k]
        filled_slice = fillConvex_hull_slice(slice_2d)
        filled_volume[:,:,k] = filled_slice

    return filled_volume

def connectedComponents(mask):
	# Identificar componentes conectados
	labeled_mask = label(mask, connectivity=1)  
	# Calcular propriedades das regiões 
	regions = regionprops(labeled_mask)
	# Encontrar a região com maior número de voxels
	if regions:  
		largest_region = max(regions, key=lambda x: x.area)
		mask_filtered = (labeled_mask == largest_region.label)
	else:
		mask_filtered = np.zeros_like(mask, dtype=bool)
	
	return mask_filtered

def handleMatrixcreation(matrix_PRE, matrix_24):
	matrixPRE_norm = matrix_PRE/matrix_PRE.values.max()
	matrix24_norm = matrix_24/matrix_24.values.max()

	plt.figure(figsize=(14,5))

	plt.subplot(1,2,1)
	plt.imshow(matrixPRE_norm.values, cmap = "YlGnBu_r", vmax=0.1)
	plt.title("Connection before procedure")
	plt.colorbar(cmap = 'YlBuGn_r')

	plt.subplot(1,2,2)
	plt.imshow(matrix24_norm.values, cmap = "YlGnBu_r", vmax=0.1)
	plt.title("Connection 24 hours after procedure")
	plt.colorbar(cmap = 'YlBuGn_r')	
	
	plt.savefig("../Results/connectivitymatrix.png") 
	plt.close
	
def process_chunk(chunk, level=0.5):
    """Aplica Marching Cubes e preenchimento em um chunk com tratamento de chunks uniformes."""
    # Verifica se o chunk não é uniforme
    chunk_min = chunk.min()
    chunk_max = chunk.max()
    
    if chunk_min == chunk_max:
        # Chunk totalmente vazio ou preenchido
        return np.zeros_like(chunk, dtype=bool)
    
    # Ajusta o level para estar dentro do intervalo do chunk
    adjusted_level = np.clip(level, chunk_min + 1e-6, chunk_max - 1e-6)
    
    try:
        verts, faces, _, _ = measure.marching_cubes(
            chunk.astype(float),  # Garante dados float para suavização posterior
            level=adjusted_level,
            allow_degenerate=False
        )
    except ValueError as e:
        print(f"Erro no chunk: {e}. Retornando máscara vazia.")
        return np.zeros_like(chunk, dtype=bool)
    
    # Gera grid de coordenadas apenas para os pontos ativos
    grid_coords = np.array(np.where(chunk)).T
    
    if len(grid_coords) == 0:
        return np.zeros_like(chunk, dtype=bool)
    
    # Verifica se há geometria válida
    if len(verts) < 4:  # Mínimo 4 vértices para um tetraedro
        return np.zeros_like(chunk, dtype=bool)
    
    # Cria máscara preenchida
    try:
        tri = Delaunay(verts)
        inside = tri.find_simplex(grid_coords) >= 0
        mask = np.zeros_like(chunk, dtype=bool)
        mask[tuple(grid_coords[inside].T)] = True
    except:
        mask = np.zeros_like(chunk, dtype=bool)
    
    return mask

# def contourSlice(mask_slice):
    # # Converte para uint8 (OpenCV requer esse tipo)
    # slice_uint8 = (mask_slice * 255).astype(np.uint8)
    
    # # Detecta contornos
    # contours, _ = cv2.findContours(
        # slice_uint8, 
        # mode=cv2.RETR_EXTERNAL,
        # method=cv2.CHAIN_APPROX_SIMPLE
    # )
    
    # # Cria máscara de contornos (garantindo tipo e contiguidade)
    # mask = np.zeros_like(slice_uint8, dtype=np.uint8)
    
    # # Desenha contornos apenas se existirem
    # if contours:  # Verifica se há contornos detectados
        # # Garante que o array é contíguo (evita erro de layout)
        # mask = np.ascontiguousarray(mask)
        # cv2.drawContours(
            # image=mask,
            # contours=contours,
            # contourIdx=-1,
            # color=255,
            # thickness=1
        # )
    
    # return (mask > 0).astype(np.uint8)  # Binário 0/1

def minDistance(mask_points, mask_target):
	mask_points_int = mask_points.astype(np.uint8)
	mask_target_int = mask_target.astype(np.uint8)
	
	coords_points = np.argwhere(mask_points_int == 1)
	coords_target = np.argwhere(mask_target_int == 1)
	
	tree = KDTree(coords_target)
	distances, _ = tree.query(coords_points, k=1) 
	
	distances_array = np.zeros_like(mask_points_int, dtype=np.float32)
	distances_array[tuple(coords_points.T)] = distances
	
	return distances_array	
