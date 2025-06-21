BASE_DIR="/home/brunobastos/Mestrado/Dados"
SCRIPT_DIR="/home/brunobastos/Mestrado/Scripts"
SUBJECTS_DIR="$BASE_DIR/fs_subjects"
ATLAS_DIR="$BASE_DIR/Atlas" 
TESTE_DIR="$BASE_DIR/Teste"
PAT_DIR="$BASE_DIR/Pat547/Pat547_PRE/Output_tract"

 
cd $PAT_DIR/Tractography
maskfilter mask_track_ndDRTT_rh.nii.gz dilate mask_dilated.nii.gz -npass 25 -force
mrcalc mask_dilated.nii.gz 0 -eq mask_inf_sup.nii.gz 1 -eq -and mask_exclude_ndDRTT.mif -datatype uint8 -force

#hemisphere=$(< ../Segmentation/hemisphere.txt)

#echo "Conteúdo da variável:"
#echo "$conteudo"


mrcalc $SUBJECTS_DIR/Pat547/next_brain_segmentation/seg_right.nii.gz 2024 -eq ROIs/ROI_PRECG_nextbrain_rh.mif -datatype uint8 -force

mrcalc ../Segmentation/subcortical_nextbrain.nii.gz 1394 -eq ../Segmentation/subcortical_nextbrain.nii.gz 1458 -eq -or ROIs/ROI_VPL_rh.mif -force

mrcalc ../Segmentation/subcortical_nextbrain.nii.gz 1314 -eq ../Segmentation/subcortical_nextbrain.nii.gz 1350 -eq -or \
	    ../Segmentation/subcortical_nextbrain.nii.gz 1381 -eq -or ../Segmentation/subcortical_nextbrain.nii.gz 1382 -eq -or \
	    ROIs/ROI_VL_rh.mif \
	    -datatype uint8 -force
	    

time tckgen  \
				-act 5tt_coreg.mif \
				-seed_image ROIs/ROI_DN_rh.mif \
				-select 100 \
				-seeds 1M \
				-include ROIs/ROI_PSA_rh.mif \
				-include ROIs/ROI_VL_rh.mif \
				-exclude ROIs/ROI_WMf_lh.mif \
				-exclude ROIs/ROI_WMh_lh.mif \
				-exclude ROIs/ROI_WMc_lh.mif \
				-minlength 40 \
				-angle 20 \
				-cutoff 0.1 \
				-step 1 \
				-samples 2 \
				-trials 500 \
				-max_attempts_per_seed 500 \
				-seed_unidirectional \
				-stop \
				wmfod_norm.mif track_ndDRTT_rh_teste_DN.tck \
				-nthreads 4 \
				-info \
				-force

tckedit track_ndDRTT_rh_teste_DN.tck -ends_only -include ROIs/ROI_thalamus_rh.mif partials.tck -force
tckmap partials.tck -template ../Segmentation/T1_upsampled.nii.gz partials_teste.mif -force				
time tckgen  \
				-act 5tt_coreg.mif \
				-backtrack \
				-seed_gmwmi ROIs/ROI_VL_rh.mif \
				-select 1000 \
				-seeds 1M \
				-include ROIs/ROI_PL_rh.mif \
				-include ROIs/ROI_PreCG_rh.mif \
				-exclude ROIs/ROI_WMf_lh.mif \
				-exclude ROIs/ROI_WMh_lh.mif \
				-exclude ROIs/ROI_WMc_lh.mif \
				-minlength 40 \
				-angle 20 \
				-cutoff 0.1 \
				-step 1 \
				-samples 2 \
				-trials 500 \
				-max_attempts_per_seed 500 \
				-seed_unidirectional \
				wmfod_norm.mif track_ndDRTT_rh_teste_VL.tck \
				-nthreads 4 \
				-info \
				-force
				
time tckgen  \
					-act 5tt_coreg.mif \
					-backtrack \
					-seed_image ROIs/ROI_DN_lh.mif \
					-select 100 \
					-seeds 100M \
					-include ROIs/ROI_PSA_rh.mif \
					-include ROIs/ROI_VL_rh.mif \
					-exclude ROIs/ROI_WMf_lh.mif \
					-exclude ROIs/ROI_WMh_rh.mif \
					-exclude ROIs/ROI_WMc_rh.mif \
					-minlength 60 \
					-angle 20 \
					-cutoff 0.1 \
					-step 1 \
					-trials 500 \
					-max_attempts_per_seed 500 \
					-seed_unidirectional \
					-samples 2 \
					wmfod_norm.mif track_DRTT_rh_teste_DN.tck \
					-nthreads 4 \
					-info \
					-force
