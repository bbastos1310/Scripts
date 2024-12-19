import nibabel as nib
import numpy as np
from scipy.ndimage import binary_erosion

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
          print(f"Outlier: data[{x},{y},{z}] = {data[x,y,z]}")
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
