BASE_DIR="/home/brunobastos/Mestrado/Dados"
SCRIPT_DIR="/home/brunobastos/Mestrado/Scripts"
SUBJECTS_DIR="$BASE_DIR/fs_subjects"
ATLAS_DIR="$BASE_DIR/Atlas" 

# Upsample da imagem T1 para usar como template  
#mrgrid ~/Mestrado/Dados/Pat548/Pat548_PRE/Output_tract/T1_resampled.mif regrid -voxel 0.4 T1_teste.nii.gz -force
#mrgrid seg_left.nii.gz regrid -interp nearest -template T1_teste.nii.gz seg_left_resampled.nii.gz -force
#mrgrid seg_right.nii.gz regrid -interp nearest -template T1_teste.nii.gz seg_right_resampled.nii.gz -force
#mrgrid SynthSeg.mgz regrid -interp nearest -template T1_teste.nii.gz SynthSeg_resampled.nii.gz -force


#mrcalc Julich_parcels_mrtrix.mif 47 -eq Julich_parcels_mrtrix.mif 48 -eq -or \
	   #Julich_parcels_mrtrix.mif 86 -eq -or Julich_parcels_mrtrix.mif 87 -eq -or \
	   #Julich_parcels_mrtrix.mif 116 -eq -or Julich_parcels_mrtrix.mif 117 -eq -or Julich_parcels_mrtrix.mif 118 -eq -or \
	   #Julich_parcels_mrtrix.mif 146 -eq -or \
	   #ROI_PCG_lh.mif -force
	   
#mrcalc Julich_parcels_mrtrix.mif 199 -eq Julich_parcels_mrtrix.mif 200 -eq -or \
	   #Julich_parcels_mrtrix.mif 238 -eq -or Julich_parcels_mrtrix.mif 239 -eq -or \
	   #Julich_parcels_mrtrix.mif 268 -eq -or Julich_parcels_mrtrix.mif 269 -eq -or Julich_parcels_mrtrix.mif 270 -eq -or \
	   #Julich_parcels_mrtrix.mif 298 -eq -or \
	   #ROI_PCG_rh.mif -force
	   
#mrconvert "$SUBJECTS_DIR/Pat548/mri/aseg.mgz" aseg.mif -force
#mrcalc aseg.mif 10 -eq ROI_thalamus_lh.mif -force
#mrcalc aseg.mif 41 -eq ROI_cerebralwm_rh.mif -force
#mrcalc aseg.mif 46 -eq ROI_cerebellumwm_rh.mif -force
#mrcalc aseg.mif 251 -eq aseg.mif 252 -eq -or aseg.mif 253 -eq -or aseg.mif 254 -eq -or aseg.mif 255 -eq -or ROI_CC.mif -force

#mrcalc Julich_parcels_mrtrix.mif 0 -gt Julich_parcels_mrtrix.mif 149 -lt -and Julich_parcels_mrtrix_mask_lh.mif -force
#mrcalc Julich_parcels_mrtrix.mif 152 -gt Julich_parcels_mrtrix.mif 300 -lt -and Julich_parcels_mrtrix_mask_rh.mif -force

#mrcalc Julich_parcels_mrtrix_mask_lh.mif  ROI_PMC_lh.mif -subtract ROI_notPMC_lh.mif -force
#mrcalc Julich_parcels_mrtrix_mask_rh.mif  ROI_PMC_rh.mif -subtract ROI_notPMC_rh.mif -force

#mrcalc Julich_parcels_mrtrix_mask_lh.mif  ROI_PCG_lh.mif -subtract ROI_notPCG_lh.mif -force
#mrcalc Julich_parcels_mrtrix_mask_rh.mif  ROI_PCG_rh.mif -subtract ROI_notPCG_rh.mif -force

##mrview T2_resampled.nii.gz -overlay.load ROI_notPMC.mif -overlay.opacity 0.5

#tckgen  \
	#-act 5tt_coreg.mif \
	#-backtrack \
	#-seed_gmwmi gmwmSeed_coreg.mif \
	#-select 30 \
	#-seeds 15000000 \
    #-include ROI_DN_lh.mif \
    #-include ROI_NR_lh.mif \
    #-include ROI_thalamus_lh.mif \
    #-include ROI_PCG_lh.mif \
    #-exclude ROI_cerebralwm_rh.mif \
    #-exclude ROI_cerebellumwm_rh.mif \
    #-exclude ROI_CC.mif \
    #-minlength 40 \
    #-angle 45 \
    #-cutoff 0.15 \
    #wmfod_norm.mif nDRTT_track_lh.tck \
    #-force

#tckgen  \
	#-act 5tt_coreg.mif \
	#-backtrack \
	#-seed_gmwmi gmwmSeed_coreg.mif \
	#-select 30 \
	#-seeds 15000000 \
    #-include ROI_DN_rh.mif \
    #-include ROI_NR_lh.mif \
    #-include ROI_thalamus_lh.mif \
    #-include ROI_PCG_lh.mif \
    #-exclude ROI_cerebralwm_rh.mif \
    #-exclude ROI_cerebellumwm_lh.mif \
    #-exclude ROI_CC.mif \
    #-minlength 40 \
    #-angle 45 \
    #-cutoff 0.15 \
    #wmfod_norm.mif DRTT_track_lh.tck \
    #-force

#mrcalc Julich_parcels_mrtrix.mif 49 -eq Julich_parcels_mrtrix.mif 50 -eq -or Julich_parcels_mrtrix.mif 51 -eq -or \
	   #Julich_parcels_mrtrix.mif 81 -eq -or\
	   #ROI_S1_lh.mif -force
	   
#mrcalc Julich_parcels_mrtrix.mif 201 -eq Julich_parcels_mrtrix.mif 202 -eq -or Julich_parcels_mrtrix.mif 203 -eq -or \
	   #Julich_parcels_mrtrix.mif 233 -eq -or\
	   #ROI_S1_lh.mif -force
	   
#tckgen  \
	#-act 5tt_coreg.mif \
	#-backtrack \
	#-seed_gmwmi gmwmSeed_coreg.mif \
	#-select 30 \
	#-seeds 1000000 \
    #-include ROI_ML_lh.mif \
    #-include ROI_PL_lh.nii.gz \
    #-include ROI_PCG_lh.mif \
    #-exclude ROI_cerebralwm_rh.mif \
    #-exclude ROI_cerebellumwm_rh.mif \
    #-exclude ROI_cerebellumwm_lh.mif \
    #-exclude ROI_CC.mif \
    #-minlength 40 \
    #-angle 45 \
    #-cutoff 0.15 \
    #wmfod_norm.mif ml_track_lh.tck \
    #-force

tckgen  \
	-act 5tt_coreg.mif \
	-backtrack \
	-seed_gmwmi gmwmSeed_coreg.mif \
	-select 20 \
	-seeds 20000000 \
    -include ROI_CP_lh.mif \
    -include ROI_PL_lh.nii.gz \
    -include ROI_PMC_lh.mif \
    -exclude ROI_cerebralwm_rh.mif \
    -exclude ROI_cerebellumwm_rh.mif \
    -exclude ROI_cerebellumwm_lh.mif \
    -exclude ROI_CC.mif \
    -minlength 40 \
    -angle 45 \
    -cutoff 0.15 \
    wmfod_norm.mif cst_track_lh.tck \
    -force


