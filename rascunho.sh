BASE_DIR="/mnt/HD_shared/Dados"
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

mrgrid ../Segmentation/Contrast_raw_coreg.nii.gz regrid -template T2_raw_coreg_up.nii.gz Contrast_raw_coreg_resampled.nii.gz -force
  
mrgrid ../Segmentation/Contrast_raw_coreg_24.nii.gz regrid -template T2_raw_coreg_up.nii.gz Contrast_raw_coreg_24_resampled.nii.gz -force
