import nibabel as nib
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
from scipy.ndimage import gaussian_filter, binary_fill_holes
from skimage import measure
from skimage.morphology import binary_closing
from skimage.segmentation import find_boundaries
import functions

def handleStd(df, field):
	mean = df[field].mean()
	std = df[field].std()
	return mean, std
	
################################ MAIN ################################3

# Arquivo CSV para leitura dos dados dos pacientes
location = os.environ["BASE_DIR"] + "/stats.csv"

df = pd.read_csv(location)

handleStd(df, "intersec_ndDRTT_zone1")
