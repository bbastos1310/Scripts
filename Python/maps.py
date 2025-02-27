# Local libraries
import functions


def handleMaps(data_map, image, data24_map, image_24, data_mask, name):
	map_treated = functions.mapTreatment(data_map, data_mask)
	map24_treated = functions.mapTreatment(data24_map, data_mask)
	name_pre = "../Results/" + name + "(PRE)"
	name_24 = "../Results/" + name + "(24H)"
	name_sub = "../Results/" + name + "(Subtraction)"
	functions.saveImage(map_treated, image, name_pre )
	functions.saveImage(map24_treated, image_24, name_24 )
	functions.saveImage(map24_treated-map_treated, image, name_sub)
	print(f"{name} saved") 	
