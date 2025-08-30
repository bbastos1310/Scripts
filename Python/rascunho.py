import numpy as np, nibabel as nib

# caminhos
mov = nib.load('ACPC/Contrast_raw_coreg_24_up_ACPC.nii.gz')   # imagem com grade 0.4 mm (por ex)
ref  = nib.load('ACPC/T1_raw_LPS_3D.nii')                # referência T1 1mm

A_mov = mov.affine     # affine atual da moving
A_ref = ref.affine

# centro em índices (voxel indices)
shape = np.array(mov.shape[:3])
center_vox = (shape - 1) / 2.0
center_vox_h = np.append(center_vox, 1.0)
print(center_vox_h)

# coordenada world do centro da moving (antes)
center_world_mov = A_mov.dot(center_vox_h)[:3]
# coordenada world do centro da referência
shape_ref = np.array(ref.shape[:3])
center_world_ref = A_ref.dot(np.append((shape_ref-1)/2.0,1.0))[:3]

print('center_world_mov:', center_world_mov)
print('center_world_ref:', center_world_ref)

def load_mrtrix_xfm(path):
    M = []
    with open(path,'r') as f:
        for line in f:
            line=line.strip()
            if not line or line.startswith('#'): continue
            vals = [float(v) for v in line.split()]
            if len(vals)==4: M.append(vals)
    M = np.array(M)
    assert M.shape==(4,4)
    return M
    

T = load_mrtrix_xfm('t12acpc_mrtrix.txt')

# aplicar T ao centro da moving:
center_world_mov = A_mov.dot(center_vox_h)
center_world_mapped = T.dot(center_world_mov)[:3]
# comparar com center_world_ref
print('mapped center:', center_world_mapped)
print('ref center :', center_world_ref)

