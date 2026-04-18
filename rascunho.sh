BASE_DIR="/mnt/HD_shared/Dados/"
SCRIPT_DIR="/mnt/HD_shared/Scripts"
FREESURFER_HOME_DEV="/media/brunobastos/linux_storage/freesurfer_dev/7-dev/"
FREESURFER_HOME_STAND="/usr/local/freesurfer/7.4.1"
N_THREADS=20
SUBJECTS_DIR="$BASE_DIR/fs_subjects"
ATLAS_DIR="$BASE_DIR/Atlas" 
ACPC_DIR="$BASE_DIR/acpc"
FREESURFER_HOME_DEV="/media/brunobastos/linux_storage/freesurfer_dev/7-dev/"
FREESURFER_HOME_STAND="/usr/local/freesurfer/7.4.1"
HISTO_DIR="$SUBJECTS_DIR/Pat549/next_brain_segmentation"
N_THREADS=20

cd "$OUT_PRE/Tractography"

mrtransform ../Segmentation/Contrast_raw_coreg.nii.gz -linear t12acpc_mrtrix.txt ACPC/Contrast_raw_coreg_ACPC_temp.nii.gz -force
mrtransform ACPC/Contrast_raw_coreg_ACPC_temp.nii.gz -template ACPC/T1_raw_ACPC.nii ACPC/Contrast_raw_coreg_ACPC.nii.gz -force
rm ACPC/Contrast_raw_coreg_ACPC_temp.nii.gz 
		
mrtransform ../Segmentation/Contrast_raw_coreg_24.nii.gz -linear t12acpc_mrtrix.txt ACPC/Contrast_raw_coreg_24_ACPC_temp.nii.gz -force
mrtransform ACPC/Contrast_raw_coreg_24_ACPC_temp.nii.gz -template ACPC/T1_raw_ACPC.nii ACPC/Contrast_raw_coreg_24_ACPC.nii.gz -force
rm ACPC/Contrast_raw_coreg_24_ACPC_temp.nii.gz
