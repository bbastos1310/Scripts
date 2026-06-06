import pydicom

def identificar_sequencia(dicom_file):

    ds = pydicom.dcmread(dicom_file, stop_before_pixels=True)
	
    texto = " ".join([
        str(ds.get("SeriesDescription", "")),
        str(ds.get("ProtocolName", "")),
        str(ds.get("SequenceName", ""))
    ]).upper()
    
    # print(texto)

    if "MPRAGE AX T1" in texto:
        return "T1"

    if "DTI_ORIG" in texto:
        return "DWI"

    if "AX_P2_ISO WMN" in texto:
        return "WMNULL"

    if "AX T2 2MM" in texto:
        return "T2"
    
    if "AX DTI RPA_ORIG" in texto:
        return "DWI_PA"

    return "Desconhecida"


print(identificar_sequencia("I_001.dcm"))
