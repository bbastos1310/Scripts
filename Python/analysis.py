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

def handleWeightedintersection (data_reference, data_compare):
	
	data_intersection = np.zeros(data_reference.shape)
	data_intersection = data_compare[data_reference == True]
	weighted_intersection = data_intersection.sum()*(0.4)**3
	
	return weighted_intersection
	
	
def handleMintrackdistance(data_center, data_track):
	data_binary = np.zeros(data_track.shape, dtype=bool)
	data_binary = functions.connectedComponents(np.where(data_track > 0.4, 1, 0))
		
	data_distances = functions.minDistance(data_center, data_binary)
	#functions.saveImage(data_distances,image,"distances")
	min_distance = data_distances[data_center == True].min() * 0.4
	
	return min_distance
	

	
def read_number(prompt):  
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Erro: Digite um número válido")
		
		
		
############################### MAIN ####################################################

score_pre = read_number("Digite o score pré procedimento: ")
score_24 = read_number("Digite o score pós procedimento: ")

with open('../Segmentation/hemisphere.txt', 'r', encoding='utf-8') as file_hemisphere:
    hemisphere = file_hemisphere.read()  
print(f"{hemisphere} hemisphere")

dict_tracks = ["ndDRTT", "dDRTT", "ML", "CST"]

if (hemisphere == 'left'):
    mask_zone1 = nib.load("ACPC/mask_zone1_ACPC.nii.gz")
    mask_zone2 = nib.load("ACPC/mask_zone2_ACPC.nii.gz")
	
    data_zone1 = mask_zone1.get_fdata().astype(bool)
    data_zone2 = mask_zone2.get_fdata().astype(bool)
    
    del mask_zone2
    
    # Volume da lesão separado por zona
    vol_zone1 = (data_zone1[data_zone1].size)*(0.4)**3
    vol_zone2 = (data_zone2[data_zone2].size)*(0.4)**3
    vol_lesion = vol_zone1 + vol_zone2
    
    intersec_1 = np.zeros((4))
    intersec_2 = np.zeros((4))
    intersec_total = np.zeros((4))
    
    weighted_intersec_1 = np.zeros((4))
    weighted_intersec_2 = np.zeros((4))
    weighted_intersec_total = np.zeros((4))
    
    min_distance = np.zeros((4))
    
    for track_number in range (len(dict_tracks)):
        track = nib.load("ACPC/track_" + dict_tracks[track_number] + "_lh_ACPC.nii.gz")
        data_track = track.get_fdata()
        del track
		
        data_binary = np.zeros(data_track.shape, dtype=bool)
        data_binary = np.where(data_track > 0.01, 1, 0)
        
        # Interseção entre os tratos e as zonas da lesão
        intersec_1[track_number] = handleAbsoluteintersection(data_zone1, data_binary)
        intersec_2[track_number] = handleAbsoluteintersection(data_zone2, data_binary)
        intersec_total[track_number] = intersec_1[track_number] + intersec_2[track_number] 
        
        weighted_intersec_1[track_number] = handleWeightedintersection(data_zone1, data_track)
        weighted_intersec_2[track_number] = handleWeightedintersection(data_zone2, data_track)
        weighted_intersec_total[track_number] = weighted_intersec_1[track_number] + weighted_intersec_2[track_number] 
		
        min_distance[track_number] = handleMintrackdistance(data_zone1, data_track)
        
if (hemisphere == 'right'):
    mask_zone1 = nib.load("ACPC/mask_zone1_ACPC.nii.gz")
    mask_zone2 = nib.load("ACPC/mask_zone2_ACPC.nii.gz")
	
    data_zone1 = mask_zone1.get_fdata().astype(bool)
    data_zone2 = mask_zone2.get_fdata().astype(bool)
    
    del mask_zone2
    
    # Volume da lesão separado por zona
    vol_zone1 = (data_zone1[data_zone1].size)*(0.4)**3
    vol_zone2 = (data_zone2[data_zone2].size)*(0.4)**3
    vol_lesion = vol_zone1 + vol_zone2
    
    intersec_1 = np.zeros((4))
    intersec_2 = np.zeros((4))
    intersec_total = np.zeros((4))
    
    weighted_intersec_1 = np.zeros((4))
    weighted_intersec_2 = np.zeros((4))
    weighted_intersec_total = np.zeros((4))
    
    min_distance = np.zeros((4))
    
    for track_number in range (len(dict_tracks)):
        track = nib.load("ACPC/track_" + dict_tracks[track_number] + "_rh_ACPC.nii.gz")
        data_track = track.get_fdata()
        del track
		
        data_binary = np.zeros(data_track.shape, dtype=bool)
        data_binary = np.where(data_track > 0.01, 1, 0)
        
        # Interseção entre os tratos e as zonas da lesão
        intersec_1[track_number] = handleAbsoluteintersection(data_zone1, data_binary)
        intersec_2[track_number] = handleAbsoluteintersection(data_zone2, data_binary)
        intersec_total[track_number] = intersec_1[track_number] + intersec_2[track_number] 
        
        weighted_intersec_1[track_number] = handleWeightedintersection(data_zone1, data_track)
        weighted_intersec_2[track_number] = handleWeightedintersection(data_zone2, data_track)
        weighted_intersec_total[track_number] = weighted_intersec_1[track_number] + weighted_intersec_2[track_number] 
		
        min_distance[track_number] = handleMintrackdistance(data_zone1, data_track)

mean_confluence = (weighted_intersec_1[0] + weighted_intersec_1[1])/(data_zone1[data_zone1].size*(0.4)**3)
improvement = (score_pre - score_24)/score_pre

# Número do paciente
pat = os.environ["PAT_NUM"]
pat_num = pat[3:]

# Arquivo CSV para leitura e escrita dos dados dos pacientes
location = os.environ["BASE_DIR"] + "/stats.csv"

FIELDNAMES = [
    "PatNum", "hemisphere", "vol_zone1", "vol_zone2", "vol(zone_1+zone_2)",
    "intersec_ndDRTT_zone1", "intersec_ndDRTT_zone2", "intersec_ndDRTT(zone_1+zone_2)",
    "weighted_ndDRTT_zone1", "weighted_ndDRTT_zone2", "weighted_ndDRTT(zone_1+zone_2)",
    "min_distance_ndDRTT",
    
    "intersec_dDRTT_zone1", "intersec_dDRTT_zone2", "intersec_dDRTT(zone_1+zone_2)",
    "weighted_dDRTT_zone1", "weighted_dDRTT_zone2", "weighted_dDRTT(zone_1+zone_2)",
    "min_distance_dDRTT",
    
    "intersec_ML_zone1", "intersec_ML_zone2", "intersec_ML(zone_1+zone_2)",
    "weighted_ML_zone1", "weighted_ML_zone2", "weighted_ML(zone_1+zone_2)",
    "min_distance_ML",
    
    "intersec_CST_zone1", "intersec_CST_zone2", "intersec_CST(zone_1+zone_2)",
    "weighted_CST_zone1", "weighted_CST_zone2", "weighted_CST(zone_1+zone_2)",
    "min_distance_CST",    
    
    "mean_confluence", "score_PRE", "score_24", "improvement"
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
    "vol_zone1": vol_zone1,
    "vol_zone2": vol_zone2, 
    "vol(zone_1+zone_2)": vol_lesion,
    
    "intersec_ndDRTT_zone1": intersec_1[0],
    "intersec_ndDRTT_zone2": intersec_2[0],
    "intersec_ndDRTT(zone_1+zone_2)": intersec_total[0],
    "weighted_ndDRTT_zone1": weighted_intersec_1[0],
    "weighted_ndDRTT_zone2": weighted_intersec_2[0],
    "weighted_ndDRTT(zone_1+zone_2)": weighted_intersec_total[0],
    "min_distance_ndDRTT": min_distance[0],    
    
    "intersec_dDRTT_zone1": intersec_1[1],
    "intersec_dDRTT_zone2": intersec_2[1],
    "intersec_dDRTT(zone_1+zone_2)": intersec_total[1],
    "weighted_dDRTT_zone1": weighted_intersec_1[1],
    "weighted_dDRTT_zone2": weighted_intersec_2[1],
    "weighted_dDRTT(zone_1+zone_2)": weighted_intersec_total[1],
    "min_distance_dDRTT": min_distance[1],
    
    "intersec_ML_zone1": intersec_1[2],
    "intersec_ML_zone2": intersec_2[2],
    "intersec_ML(zone_1+zone_2)": intersec_total[2],
    "weighted_ML_zone1": weighted_intersec_1[2],
    "weighted_ML_zone2": weighted_intersec_2[2],
    "weighted_ML(zone_1+zone_2)": weighted_intersec_total[2],
    "min_distance_ML": min_distance[2],
    
    "intersec_CST_zone1": intersec_1[3],
    "intersec_CST_zone2": intersec_2[3],
    "intersec_CST(zone_1+zone_2)": intersec_total[3],
    "weighted_CST_zone1": weighted_intersec_1[3],
    "weighted_CST_zone2": weighted_intersec_2[3],
    "weighted_CST(zone_1+zone_2)": weighted_intersec_total[3],
    "min_distance_CST": min_distance[3],
    
    "mean_confluence": mean_confluence,
    "score_PRE": score_pre,
    "score_24": score_24,
    "improvement": improvement
}

filtered_pat.append(new_patient)
filtered_pat = sorted(filtered_pat, key=lambda x: int(x["PatNum"]))

with open(location, "w", newline='', encoding='utf-8') as file_stats:
    writer = csv.DictWriter(file_stats, fieldnames=FIELDNAMES)
    writer.writeheader()
    writer.writerows(filtered_pat)

print("Arquivo stats.csv atualizado.")
		





