BASE_DIR="/home/brunobastos/Mestrado/Dados"
SCRIPT_DIR="/home/brunobastos/Mestrado/Scripts"
SUBJECTS_DIR="$BASE_DIR/fs_subjects"
ATLAS_DIR="$BASE_DIR/Atlas" 
TESTE_DIR="$BASE_DIR/Teste"
PAT_DIR="$BASE_DIR/Pat547/Pat547_PRE/Output_tract"

 
time tckgen  \
				-act 5tt_coreg.mif \
				-backtrack \
				-seed_image ROIs/ROI_MO_rh.mif \
				-select 2000 \
				-seeds 100M \
				-include ROIs/ROI_CP_rh.mif \
				-include ROIs/ROI_PL_rh.mif \
				-include ROIs/ROI_PMC_rh.mif \
				-exclude ROIs/ROI_WMf_lh.mif \
				-exclude ROIs/ROI_WMh_lh.mif \
				-exclude ROIs/ROI_WMc_lh.mif \
				-exclude ROIs/ROI_WMc_rh.mif \
				-minlength 60 \
				-angle 20 \
				-cutoff 0.1 \
				-step 1 \
				-trials 500 \
				-max_attempts_per_seed 500 \
				-seed_direction 0,0,1 \
				-samples 2 \
				wmfod_norm.mif track_CST_rh_teste2.tck \
				-nthreads 20 \
				-info \
				-force

time tckgen  \
				-act 5tt_coreg.mif \
				-backtrack \
				-seed_gmwmi ROIs/ROI_PMC_rh.mif \
				-select 2000 \
				-seeds 100M \
				-include ROIs/ROI_PL_rh.mif \
				-include ROIs/ROI_CP_rh.mif \
				-include ROIs/ROI_MO_rh.mif \
				-exclude ROIs/ROI_WMf_lh.mif \
				-exclude ROIs/ROI_WMh_lh.mif \
				-exclude ROIs/ROI_WMc_lh.mif \
				-exclude ROIs/ROI_WMc_rh.mif \
				-minlength 60 \
				-angle 20 \
				-cutoff 0.1 \
				-step 1 \
				-trials 500 \
				-max_attempts_per_seed 500 \
				-seed_unidirectional \
				-samples 2 \
				wmfod_norm.mif track_CST_rh_teste.tck \
				-nthreads 20 \
				-info \
				-force
