BASE_DIR="/media/brunobastos/linux_storage/Mestrado/Dados"
SCRIPT_DIR="/media/brunobastos/linux_storage/Mestrado/Scripts"
FREESURFER_HOME_DEV="/media/brunobastos/linux_storage/freesurfer_dev/7-dev/"
FREESURFER_HOME_STAND="/usr/local/freesurfer/7.4.1"
N_THREADS=20
SUBJECTS_DIR="$BASE_DIR/fs_subjects"
ATLAS_DIR="$BASE_DIR/Atlas" 
ACPC_DIR="$BASE_DIR/acpc"
FREESURFER_HOME_DEV="/media/brunobastos/linux_storage/freesurfer_dev/7-dev/"
FREESURFER_HOME_STAND="/usr/local/freesurfer/7.4.1"
N_THREADS=20

cd "$OUT_PRE/Rascunho"

#mrgrid T2_raw_24_coreg.nii.gz regrid -template T2_raw_coreg.nii.gz T2_raw_24_coreg_resampled.nii.gz -force
#mrgrid Contrast_raw_coreg.nii.gz regrid -template T2_raw_coreg.nii.gz Contrast_raw_coreg_resampled.nii.gz -force
#mrgrid Contrast_raw_coreg_24.nii.gz regrid -template Contrast_raw_coreg.nii.gz Contrast_raw_coreg_24_resampled.nii.gz -force
#mrgrid ROI_rostral_lh_Contrast.nii.gz regrid -template Contrast_raw_coreg.nii.gz ROI_rostral_lh_Contrast_resampled.nii.gz -force
#mrgrid ROI_rostral_rh_Contrast.nii.gz regrid -template Contrast_raw_coreg.nii.gz ROI_rostral_rh_Contrast_resampled.nii.gz -force

#mrconvert ../Preprocess/5tt_coreg.mif -coord 3 3 -axes 0,1,2 5tt_coreg_csf.mif -force
#mrcalc 5tt_coreg_csf.mif 0 -gt 5tt_coreg_csf_bool.mif -force
#mrgrid 5tt_coreg_csf_bool.mif regrid -template Contrast_raw_coreg.nii.gz -datatype uint8 -oversample 1,1,1 5tt_coreg_csf_resampled.nii.gz -force

python "$SCRIPT_DIR/Python/rascunho.py"
