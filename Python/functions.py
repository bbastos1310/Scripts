import nibabel as nib
import numpy as np
from scipy.ndimage import binary_erosion
from skimage.measure import label, regionprops
from scipy.spatial import ConvexHull
from skimage.draw import polygon

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
  upper_bound = Q3 + 5 * IQR

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

  return data_norm

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
		print("Nenhum componente encontrado.")
		mask_filtered = np.zeros_like(mask, dtype=bool)
	
	return mask_filtered
