BASE_DIR="/home/brunobastos/Mestrado/Dados"
SCRIPT_DIR="/home/brunobastos/Mestrado/Scripts"
SUBJECTS_DIR="$BASE_DIR/fs_subjects"
ATLAS_DIR="$BASE_DIR/Atlas" 
TESTE_DIR="$BASE_DIR/Teste"
PAT_DIR="$BASE_DIR/Pat547/Pat547_PRE/Output_tract"
ACPC_DIR="$BASE_DIR/acpc"
FREESURFER_HOME_DEV="/media/brunobastos/linux_storage/freesurfer_dev/7-dev/"
FREESURFER_HOME_STAND="/usr/local/freesurfer/7.4.1"
N_THREADS=20

#(
#export FREESURFER_HOME="$FREESURFER_HOME_STAND"
#export SUBJECTS_DIR="$SUBJECTS_DIR"
#source "$FREESURFER_HOME/SetUpFreeSurfer.sh"
#freeview -v ACPC/Contrast_raw_coreg_24_up_ACPC.nii.gz \
		 #-v ACPC/track_ndDRTT_lh_ACPC.nii.gz \
		 #-v ACPC/track_dDRTT_lh_ACPC.nii.gz \
		 #-v ACPC/track_CST_lh_ACPC.nii.gz \
		 #-v ACPC/track_ML_lh_ACPC.nii.gz:colormap=LUT:lut="$ATLAS_DIR/LUT_tracks.txt" 
##)

mrconvert ACPC/T1_raw_LPS.nii -coord 3 0 -axes 0,1,2 ACPC/T1_raw_LPS_3D.nii -force

flirt -in T1_raw.nii -ref ACPC/T1_raw_LPS_3D.nii -dof 6 -omat t12acpc.mat
transformconvert t12acpc.mat T1_raw.nii ACPC/T1_raw_LPS_3D.nii flirt_import t12acpc_mrtrix.txt -force
mrtransform T1_raw.nii -linear t12acpc_mrtrix.txt ACPC/T1_raw_ACPC.nii -force
mrtransform ACPC/T1_raw_ACPC.nii -template ACPC/T1_raw_LPS_3D.nii ACPC/T1_raw_ACPC_aligned.nii -datatype float32 -force
mrgrid ACPC/T1_raw_ACPC_aligned.nii regrid -voxel 0.4 ACPC/T1_raw_ACPC_aligned_up.nii

mrtransform Contrast_raw_coreg_24_up.nii.gz -linear t12acpc_mrtrix.txt ACPC/Contrast_raw_coreg_24_up_ACPC.nii.gz -force
mrtransform ACPC/Contrast_raw_coreg_24_up_ACPC.nii.gz -template ACPC/T1_raw_ACPC_aligned_up.nii ACPC/Contrast_raw_coreg_24_up_ACPC_aligned.nii.gz -datatype float32 -force

mrtransform mask_lesion_float_up.nii.gz -linear t12acpc_mrtrix.txt ACPC/mask_lesion_float_up_ACPC.nii.gz -force
mrtransform ACPC/mask_lesion_float_up_ACPC.nii.gz -template ACPC/T1_raw_ACPC_aligned_up.nii ACPC/mask_lesion_float_up_ACPC_aligned.nii.gz -datatype float32 -force

mrtransform track_ndDRTT_rh.nii.gz -linear t12acpc_mrtrix.txt ACPC/track_ndDRTT_rh_ACPC.nii.gz -force
mrtransform ACPC/track_ndDRTT_rh_ACPC.nii.gz -template ACPC/T1_raw_ACPC_aligned_up.nii ACPC/track_ndDRTT_rh_ACPC_aligned.nii.gz -datatype float32 -force

mrtransform track_dDRTT_rh.nii.gz -linear t12acpc_mrtrix.txt ACPC/track_dDRTT_rh_ACPC.nii.gz -force
mrtransform ACPC/track_dDRTT_rh_ACPC.nii.gz -template ACPC/T1_raw_ACPC_aligned_up.nii ACPC/track_dDRTT_rh_ACPC_aligned.nii.gz -datatype float32 -force

mrtransform track_CST_rh.nii.gz -linear t12acpc_mrtrix.txt ACPC/track_CST_rh_ACPC.nii.gz -force
mrtransform ACPC/track_CST_rh_ACPC.nii.gz -template ACPC/T1_raw_ACPC_aligned_up.nii ACPC/track_CST_rh_ACPC_aligned.nii.gz -datatype float32 -force

mrtransform track_ML_rh.nii.gz -linear t12acpc_mrtrix.txt ACPC/track_ML_rh_ACPC.nii.gz -force
mrtransform ACPC/track_ML_rh_ACPC.nii.gz -template ACPC/T1_raw_ACPC_aligned_up.nii ACPC/track_ML_rh_ACPC_aligned.nii.gz -datatype float32 -force





