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
HISTO_DIR="$SUBJECTS_DIR/Pat549/next_brain_segmentation"
N_THREADS=20

cd "$OUT_PRE/Rascunho"

echo $PAT_NUM
export PAT_NUM BASE_DIR 

python "$SCRIPT_DIR/Python/rascunho.py"

