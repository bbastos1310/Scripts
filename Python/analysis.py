import nibabel as nib
import matplotlib.pyplot as plt
import numpy as np
import os
import csv
from scipy.ndimage import gaussian_filter, binary_fill_holes
from skimage import measure
from skimage.morphology import binary_closing
from skimage.segmentation import find_boundaries
import functions

def handleAbsoluteintersection (data_reference, data_compare):
	# Função para quantificar a interseção do parâmetro analisado com a lesão, leva em consideração a intensidade da lesão em cada voxel ("Análogo a uma média ponderada")
	
	mask_intersection = np.zeros(data_reference.shape, dtype=bool)
	mask_intersection = ((data_reference != 0) & (data_compare != 0))
	intersection = (mask_intersection[mask_intersection == True].size)*(0.4)**3
	
	return intersection
	
def handleMintrackdistance(data_center, data_track):
	
	data_distances = functions.minDistance(data_center, data_track)
	#functions.saveImage(data_distances,image,"distances")
	min_distance = data_distances[data_center == True].min() * 0.4
	
	return min_distance
	
def read_number(prompt):  
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Erro: Digite um número válido")
		
		
		
## MAIN
# Score do paciente fornecido pelo usuário
score_pre = read_number("Digite o score pré procedimento: ")
score_24 = read_number("Digite o score pós procedimento: ")

with open('../Segmentation/hemisphere.txt', 'r', encoding='utf-8') as file_hemisphere:
    hemisphere = file_hemisphere.read()  
print(f"{hemisphere} hemisphere")

if (hemisphere == 'left'):
	track_ndDRTT_ACPC = nib.load("ACPC/track_ndDRTT_lh_ACPC.nii.gz") 
	track_dDRTT_ACPC = nib.load("ACPC/track_dDRTT_lh_ACPC.nii.gz") 
	track_CST_ACPC = nib.load("ACPC/track_CST_lh_ACPC.nii.gz") 
	track_ML_ACPC = nib.load("ACPC/track_ML_lh_ACPC.nii.gz") 
	mask_zone1 = nib.load("ACPC/mask_zone1_ACPC.nii.gz")
	mask_zone2 = nib.load("ACPC/mask_zone2_ACPC.nii.gz")
	mask_zone3 = nib.load("ACPC/mask_zone3_ACPC.nii.gz")
	mask_center = nib.load("ACPC/mask_center_ACPC.nii.gz")

elif (hemisphere == 'right'):
	track_ndDRTT_ACPC = nib.load("ACPC/track_ndDRTT_rh_ACPC.nii.gz") 
	track_dDRTT_ACPC = nib.load("ACPC/track_dDRTT_rh_ACPC.nii.gz") 
	track_CST_ACPC = nib.load("ACPC/track_CST_rh_ACPC.nii.gz") 
	track_ML_ACPC = nib.load("ACPC/track_ML_rh_ACPC.nii.gz") 
	mask_zone1 = nib.load("ACPC/mask_zone1_ACPC.nii.gz")
	mask_zone2 = nib.load("ACPC/mask_zone2_ACPC.nii.gz")
	mask_zone3 = nib.load("ACPC/mask_zone3_ACPC.nii.gz")
	mask_center = nib.load("ACPC/mask_center_ACPC.nii.gz")

print(".Files loaded (ACPC)")

## Extract data from image
data_ndDRTT_ACPC = track_ndDRTT_ACPC.get_fdata().astype(bool) 
data_dDRTT_ACPC = track_dDRTT_ACPC.get_fdata().astype(bool) 
data_CST_ACPC = track_CST_ACPC.get_fdata().astype(bool) 
data_ML_ACPC = track_ML_ACPC.get_fdata().astype(bool) 
data_zone1 = mask_zone1.get_fdata().astype(bool)
data_zone2 = mask_zone2.get_fdata().astype(bool)
data_zone3 = mask_zone3.get_fdata().astype(bool)

print(".Data loaded(ACPC)")

del track_ndDRTT_ACPC, track_dDRTT_ACPC, track_CST_ACPC, track_ML_ACPC, mask_zone1, mask_zone2, mask_zone3, mask_center

# Volume da lesão separado por zona
vol_zone1 = (data_zone1[data_zone1 == 1].size)*(0.4)**3

vol_zone2 = (data_zone2[data_zone2].size)*(0.4)**3

vol_zone3 = (data_zone3[data_zone3].size)*(0.4)**3

# Interseção entre os tratos e as zonas da lesão
intersec_ndDRTT_1 = handleAbsoluteintersection(data_zone1, data_ndDRTT_ACPC)
intersec_dDRTT_1 = handleAbsoluteintersection(data_zone1, data_dDRTT_ACPC)
intersec_CST_1 = handleAbsoluteintersection(data_zone1, data_CST_ACPC)
intersec_ML_1 = handleAbsoluteintersection(data_zone1, data_ML_ACPC)

intersec_ndDRTT_2 = handleAbsoluteintersection(data_zone2, data_ndDRTT_ACPC)
intersec_dDRTT_2 = handleAbsoluteintersection(data_zone2, data_dDRTT_ACPC)
intersec_CST_2 = handleAbsoluteintersection(data_zone2, data_CST_ACPC)
intersec_ML_2 = handleAbsoluteintersection(data_zone2, data_ML_ACPC)

intersec_ndDRTT_3 = handleAbsoluteintersection(data_zone3, data_ndDRTT_ACPC)
intersec_dDRTT_3 = handleAbsoluteintersection(data_zone3, data_dDRTT_ACPC)
intersec_CST_3 = handleAbsoluteintersection(data_zone3, data_CST_ACPC)
intersec_ML_3 = handleAbsoluteintersection(data_zone3, data_ML_ACPC)

# Mínima distância dos tratos CST e ML para a zona 1 da lesão
min_distance_CST = handleMintrackdistance(data_zone1, data_CST_ACPC)
min_distance_ML = handleMintrackdistance(data_zone1, data_ML_ACPC)

# Número do paciente
pat = os.environ["PAT_NUM"]
pat_num = pat[3:]

# Arquivo CSV para leitura e escrita dos dados dos pacientes
location = os.environ["BASE_DIR"] + "/stats.csv"

FIELDNAMES = [
    "PatNum", "hemisphere", "vol_zona1", "vol_zona2", "vol_zona3", 
    "intersec_ndDRTT_1", "intersec_dDRTT_1", "intersec_CST_1", "intersec_ML_1",
    "intersec_ndDRTT_2", "intersec_dDRTT_2", "intersec_CST_2", "intersec_ML_2",
    "intersec_ndDRTT_3", "intersec_dDRTT_3", "intersec_CST_3", "intersec_ML_3",
    "score_PRE", "score_24", "min_distance_CST", "min_distance_ML"
]

try:
    # Leitura do CSV (caso exista)
    patients = []
    
    #if os.path.exists(location):
    with open(location, "r", encoding='utf-8') as file_stats:
        reader = csv.DictReader(file_stats)
        patients = list(reader)
    
    # Verifica se o paciente já está listado, caso esteja apaga os dados antigos para a inserção dos novos dados
    filtered_pat = [p for p in patients if p.get("PatNum") != pat_num]
    
    # Salvar resultado
    with open(location, "w", newline='', encoding='utf-8') as file_stats:
        writer = csv.DictWriter(file_stats, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(filtered_pat)
    
except FileNotFoundError:
    # Criar arquivo e adicionar Pat549 (campos vazios)
    print("File stats.csv not found")
    
    with open(location, "w", newline='', encoding='utf-8') as new_file_stats:
        writer = csv.DictWriter(new_file_stats, fieldnames=FIELDNAMES)
        writer.writeheader()

# Adiciona o paciente
new_patient = {
    "PatNum": pat_num,
    "hemisphere": hemisphere,
    "vol_zona1": vol_zone1,
    "vol_zona2": vol_zone2, 
    "vol_zona3": vol_zone3,
    "intersec_ndDRTT_1": intersec_ndDRTT_1,
    "intersec_dDRTT_1": intersec_dDRTT_1,
    "intersec_CST_1": intersec_CST_1,
    "intersec_ML_1": intersec_ML_1,
    "intersec_ndDRTT_2": intersec_ndDRTT_2,
    "intersec_dDRTT_2": intersec_dDRTT_2,
    "intersec_CST_2": intersec_CST_2,
    "intersec_ML_2": intersec_ML_2,
    "intersec_ndDRTT_3": intersec_ndDRTT_3,
    "intersec_dDRTT_3": intersec_dDRTT_3,
    "intersec_CST_3": intersec_CST_3,
    "intersec_ML_3": intersec_ML_3,
    "score_PRE": score_pre,
    "score_24": score_24,
    "min_distance_CST": min_distance_CST,
    "min_distance_ML": min_distance_ML
}

# Adicionar ao arquivo
with open(location, "a", newline='', encoding='utf-8') as file_stats:
    writer = csv.DictWriter(file_stats, fieldnames=FIELDNAMES)
    writer.writerow(new_patient)

print("Arquivo stats.csv atualizado.")
# with open(location, "r") as file_stats:
    # reader = csv.DictReader(file_stats)
    # for pat in reader:
        # if pat["PatNum"] == "549":
            # print(f"Vol Zona1: {pat['vol_zona1']}")
            # print(f"Score PRE: {pat['score_PRE']}")
