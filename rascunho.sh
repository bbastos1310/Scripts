BASE_DIR="/home/brunobastos/Mestrado/Dados"
SCRIPT_DIR="/home/brunobastos/Mestrado/Scripts"
SUBJECTS_DIR="$BASE_DIR/fs_subjects"
ATLAS_DIR="$BASE_DIR/Atlas" 
TESTE_DIR="$BASE_DIR/Teste"
PAT_DIR="$BASE_DIR/Pat547/Pat547_PRE/Output_tract"
FREESURFER_HOME_DEV="/media/brunobastos/linux_storage/freesurfer_dev/7-dev/"
FREESURFER_HOME_STAND="/usr/local/freesurfer/7.4.1"
N_THREADS=20

(
export FREESURFER_HOME="$FREESURFER_HOME_STAND"
export SUBJECTS_DIR="$SUBJECTS_DIR"
source "$FREESURFER_HOME/SetUpFreeSurfer.sh"
freeview -v ACPC/Contrast_raw_coreg_24_up_ACPC.nii.gz \
		 -v ACPC/track_ndDRTT_lh_ACPC.nii.gz \
		 -v ACPC/track_dDRTT_lh_ACPC.nii.gz \
		 -v ACPC/track_CST_lh_ACPC.nii.gz \
		 -v ACPC/track_ML_lh_ACPC.nii.gz:colormap=LUT:lut="$ATLAS_DIR/LUT_tracks.txt" 
)
