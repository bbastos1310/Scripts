#local libraries
import functions

#external libraries
import numpy as np
# from skimage import color, measure
import matplotlib.pyplot as plt
from skimage.morphology import square, closing
from scipy.ndimage import center_of_mass


def handleLesionmask(data_contrast, data_contrast_24, Contrast):
	# Normalização
	data_preNorm = data_contrast/np.abs(data_contrast).max()
	data_24Norm = data_contrast_24/np.abs(data_contrast_24).max()
	
	# Diferença entre as imagens
	data = data_24Norm - data_preNorm
	
	# Salvar a subtração das imagens
	functions.saveImage(data, Contrast, "../Results/Contrast_difference")
	print("-Imagem Contrast_difference.nii.gz salva")
	
	# Inicializa uma máscara binária com zeros
	mask = np.zeros(np.abs(data).shape, dtype=np.float32)
	
	# Verifica o contorno para cada corte a partir de um limiar
	for x in range(data.shape[0]):
	  contornos = measure.find_contours(np.abs(data[x,:,:]), level=0.3)
	  # Itera sobre cada contorno encontrado
	  for contorno in contornos:
		  # Obter as coordenadas dos contornos
		  r = contorno[:, 0].astype(int)
		  c = contorno[:, 1].astype(int)
		  mask[x, r, c] = 1
  
	plt.imshow(mask[:,113,:], cmap='gray')
	# Salvar a imagem em um arquivo
	plt.savefig("../Results/mask_contour.png")  # Salva como arquivo PNG
	# Fechar o plot para liberar memória
	plt.close()
	print("-Imagem mask_contour.png salva")
	
	# Closing
	mask_closed = np.zeros(data.shape)
	for x in range (data.shape[0]):
	  mask_closed[x,:,:] = closing(mask[x,:,:], square(4))
	
	# Labels
	label_mask, num_labels = measure.label(mask_closed,connectivity=1 ,return_num=True)
	
	# Define o limite mínimo de voxels para manter os labels
	min_voxels = 250  # Ajuste este valor conforme necessário
	
	# Itera sobre os labels e calcula as propriedades dos objetos rotulados
	labels_filtered = np.zeros_like(label_mask)
	for region in measure.regionprops(label_mask):
		if region.area >= min_voxels:  # `area` retorna o número de voxels
			labels_filtered[label_mask == region.label] = region.label
	
	plt.imshow(color.label2rgb(labels_filtered[:,113,:], bg_label=0))
	plt.savefig("../Results/filtered_labels.png")  # Salva como arquivo PNG
	plt.close
	print("-Imagem filtered_labels.png salva")
	
	# Lesion selection
	center_image = np.array(labels_filtered.shape) / 2
	closest_label = None
	min_distance = float('inf')
	
	print("-Cálculo do label mais próximo do centro, esse comando é um pouco demorado")
	# Calcular o centro de massa de cada label
	for label in range(1, num_labels + 1):  # Começa do label 1 até o número total de labels
		actual_label = (labels_filtered == label)  # Cria uma máscara para o label atual
		center = center_of_mass(actual_label)  # Calcula o centro de massa

		# Calcula a distância entre o centro do label e o centro da imagem
		distance_center = np.linalg.norm(np.array(center) - center_image)

		# Atualiza o label mais central se a distância for menor
		if distance_center < min_distance:
			min_distance = distance_center
			closest_label = label
			center_lesion = center
	
	# Voxels pertencentes à lesão
	mask_lesion = (labels_filtered == closest_label)
	lesion_index_tuple = np.where(mask_lesion == True)
	x_array = lesion_index_tuple[0]
	y_array = lesion_index_tuple[1]
	z_array = lesion_index_tuple[2]	
	num_points = len(x_array)
	lesion_coordinates = np.zeros((num_points, 3))
	for point in range(num_points):
	  lesion_coordinates[point] = [x_array[point], y_array[point], z_array[point]]
	
	# Criação de uma imagem da máscara da lesão
	lesion_coordinates = lesion_coordinates.astype(np.int32)
	lesion_data = np.zeros(data.shape)
	for point in range(num_points):
	  lesion_data[lesion_coordinates[point][0],lesion_coordinates[point][1],lesion_coordinates[point][2]] = 1
	functions.saveImage(lesion_data, Contrast, "../Results/mask_lesion")
	print("-Imagem mask_lesion.nii.gz salva")
	
	return lesion_coordinates
