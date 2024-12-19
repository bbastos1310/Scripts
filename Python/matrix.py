# local libraries

# external libraries
import pandas as pd
import matplotlib.pyplot as plt

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
