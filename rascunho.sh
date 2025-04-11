BASE_DIR="/home/brunobastos/Mestrado/Dados"
SCRIPT_DIR="/home/brunobastos/Mestrado/Scripts"
SUBJECTS_DIR="$BASE_DIR/fs_subjects"
ATLAS_DIR="$BASE_DIR/Atlas" 


#mrgrid "$HISTO_DIR/SynthSeg.mgz" regrid -interp nearest -template "$OUT_PRE/T1_resampled.nii.gz" "$OUT_PRE/SynthSeg_resampled.nii.gz" -force

#mrcalc histo_parcels.nii.gz 1210 -eq ROI_ML_lh.mif -datatype bit -force
#mrgrid ROI_ML_lh.mif regrid -template dwi_den_unr_preproc_unb_reg.mif ROI_ML_lh_resampled.mif -interp nearest -datatype bit -force

#mrcalc histo_parcels.nii.gz 1211 -eq ROI_CP_lh.mif -datatype bit -force
#mrgrid ROI_CP_lh.mif regrid -template dwi_den_unr_preproc_unb_reg.mif ROI_CP_lh_resampled.mif -interp nearest -datatype bit -force
#mrcalc ROI_CP_lh_resampled.mif 0 -gt - | maskfilter - connect - | maskfilter - dilate -npass 1 ROI_CP_lh_filtered.mif -force

#mrconvert histo_parcels.nii.gz histo_parcels.mif -force
#mrconvert mask_DN_teste.nii.gz mask_DN_teste.mif -force
#mrcalc histo_parcels.nii.gz 1210 -eq ROI_ML_lh.mif -datatype bit -force
#mrcalc histo_parcels.nii.gz 1211 -eq ROI_CP_lh.mif -datatype bit -force
#mrcalc histo_parcels.nii.gz 1212 -eq ROI_RN_lh.mif -datatype bit -force
#mrcalc histo_parcels.nii.gz 1214 -eq ROI_DN_lh.mif -datatype bit -force
#mrcalc histo_parcels.nii.gz 1215 -eq ROI_PSA_lh.mif -datatype bit -force
#mrcalc histo_parcels.nii.gz 1216 -eq ROI_WMf_lh.mif -datatype bit -force
#mrcalc histo_parcels.nii.gz 1217 -eq ROI_WMh_lh.mif -datatype bit -force
#mrcalc histo_parcels.nii.gz 1218 -eq ROI_WMc_lh.mif -datatype bit -force

#mrcalc histo_parcels.nii.gz 2215 -eq ROI_PSA_rh.mif -datatype bit -force
#mrcalc histo_parcels.nii.gz 2216 -eq ROI_WMf_rh.mif -datatype bit -force
#mrcalc histo_parcels.nii.gz 2217 -eq ROI_WMh_rh.mif -datatype bit -force
#mrcalc histo_parcels.nii.gz 2218 -eq ROI_WMc_rh.mif -datatype bit -force

#mrcalc SynthSeg.mgz 16 -eq ROI_brainstem.mif -force
#mrcalc SynthSeg.mgz 10 -eq ROI_thalamus_lh.mif -force
#mrcalc SynthSeg.mgz 49 -eq ROI_thalamus_rh.mif -force
#mrcalc SynthSeg.mgz 41 -eq ROI_cerebralwm_rh.mif -force
#mrcalc SynthSeg.mgz 46 -eq ROI_cerebellumwm_rh.mif -force
#mrcalc SynthSeg.mgz 52 -eq ROI_pallidum_rh.mif -force
#mrcalc SynthSeg.mgz 13 -eq ROI_pallidum_lh.mif -force
#mrcalc SynthSeg.mgz 251 -eq SynthSeg.mgz 252 -eq -or SynthSeg.mgz 253 -eq -or SynthSeg.mgz 254 -eq -or SynthSeg.mgz 255 -eq -or ROI_CC.mif -force

#mrcalc Julich_parcels_mrtrix.mif 47 -eq Julich_parcels_mrtrix.mif 48 -eq -or \
	   #Julich_parcels_mrtrix.mif 86 -eq -or Julich_parcels_mrtrix.mif 87 -eq -or \
	   #Julich_parcels_mrtrix.mif 116 -eq -or Julich_parcels_mrtrix.mif 117 -eq -or Julich_parcels_mrtrix.mif 118 -eq -or \
	   #Julich_parcels_mrtrix.mif 146 -eq -or \
	   #ROI_PCG_lh.mif \
	   #-datatype bit -force
	   
#mrgrid ROI_PCG_lh.mif regrid -template dwi_den_unr_preproc_unb_reg.mif ROI_PCG_lh_resampled.mif -datatype bit -force
	   
#mrcalc Julich_parcels_mrtrix.mif 199 -eq Julich_parcels_mrtrix.mif 200 -eq -or \
	   #Julich_parcels_mrtrix.mif 238 -eq -or Julich_parcels_mrtrix.mif 239 -eq -or \
	   #Julich_parcels_mrtrix.mif 268 -eq -or Julich_parcels_mrtrix.mif 269 -eq -or Julich_parcels_mrtrix.mif 270 -eq -or \
	   #Julich_parcels_mrtrix.mif 298 -eq -or \
	   #ROI_PCG_rh.mif \
	   #-datatype bit -force

#mrgrid ROI_PCG_lh.mif regrid -template dwi_den_unr_preproc_unb_reg.mif ROI_PCG_lh_resampled.mif -datatype bit -force
	   
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
	#-seed_gmwmi intersect_seed.mif \
	#-select 50000 \
	#-seeds 50M \
    #-include ROI_PSA_lh.mif \
    #-exclude ROI_WM_rh.mif \
    #-minlength 40 \
    #-angle 45 \
    #-cutoff 0.15 \
    #wmfod_norm.mif ndDRTT_track_lh.tck \
    #-force
    
#mrgrid gmwmSeed_coreg.mif regrid -template mask_DN_teste.mif gmwmSeed_coreg_resampled.mif -interp linear -force
#mrcalc gmwmSeed_coreg_resampled.mif mask_DN_teste.mif -mult intersect_seed.mif -force

#time tckgen  \
	#-act 5tt_coreg.mif \
	#-backtrack \
	#-seed_gmwmi intersect_seed.mif \
	#-select 1000 \
	#-seeds 100M \
    #-include ROI_PSA_rh.mif \
    #-include ROI_PCG_rh.mif \
    #-exclude ROI_WMf_lh.mif \
    #-exclude ROI_WMc_rh.mif \
    #-exclude ROI_WMh_rh.mif \
    #-minlength 50 \
    #-angle 20 \
    #-cutoff 0.1 \
    #-step 1 \
    #-seed_unidirectional \
    #-samples 2 \
    #wmfod_norm.mif track_DRTT_lrh_teste.tck \
    #-force

#mrcalc Julich_parcels_mrtrix.mif 49 -eq Julich_parcels_mrtrix.mif 50 -eq -or Julich_parcels_mrtrix.mif 51 -eq -or \
	   #Julich_parcels_mrtrix.mif 81 -eq -or\
	   #ROI_S1_lh.mif -force
	   
#mrcalc Julich_parcels_mrtrix.mif 201 -eq Julich_parcels_mrtrix.mif 202 -eq -or Julich_parcels_mrtrix.mif 203 -eq -or \
	   #Julich_parcels_mrtrix.mif 233 -eq -or\
	   #ROI_S1_lh.mif -force

#mrcalc histo_parcels.nii.gz 1216 -eq ROI_brainstem_lh.mif -force
#mrgrid gmwmSeed_coreg.mif regrid -template ROI_brainstem_lh.mif gmwmSeed_coreg_resampled.mif -interp linear -force	   
#mrcalc gmwmSeed_coreg_resampled.mif ROI_brainstem_lh.mif -mult intersect_seed_brainstem.mif -force

 
#time tckgen  \
	#-act 5tt_coreg.mif \
	#-backtrack \
	#-seed_gmwmi intersect_seed_brainstem.mif \
	#-select 1000 \
	#-seeds 10M \
    #-include ROI_ML_lh.mif \
    #-include ROI_PL_lh.nii.gz \
    #-include ROI_S1_lh.mif \
    #-exclude ROI_WMf_rh.mif \
    #-exclude ROI_WMc_rh.mif \
    #-exclude ROI_WMc_lh.mif \
    #-exclude ROI_WMh_rh.mif \
    #-minlength 40 \
    #-angle 20 \
    #-cutoff 0.1 \
    #-seed_unidirectional \
    #-samples 2 \
    #wmfod_norm.mif ml_track_lh.tck \
    #-force 

mrcalc Julich_parcels_freesurfer.nii.gz 1047 -eq Julich_parcels_freesurfer.nii.gz 1048 -eq -or ROI_PMC_lh.mif -force
mrgrid gmwmSeed_coreg.mif regrid -template ROI_PMC_lh.mif gmwmSeed_coreg_resampled_cst.mif -interp linear -force	   
mrcalc gmwmSeed_coreg_resampled_cst.mif ROI_PMC_lh.mif -mult intersect_seed_cst.mif -force

#mrcalc Julich_parcels_mrtrix.mif 0 -gt Julich_parcels_mask_lh.mif -force
#mrcalc Julich_parcels_mask_lh.mif ROI_PMC_lh.mif -subtract ROI_notPMC_lh.mif -force

time tckgen  \
	-act 5tt_coreg.mif \
	-seed_gmwmi intersect_seed_cst.mif \
	-select 1000 \
	-seeds 100M \
    -include ROI_CP_lh.mif \
    -include ROI_PL_lh.nii.gz \
    -include ROI_PMC_lh.mif \
    -exclude ROI_WMf_rh.mif \
    -exclude ROI_WMc_rh.mif \
    -exclude ROI_WMc_lh.mif \
    -exclude ROI_WMh_rh.mif \
    -exclude ROI_thalamus_lh.mif \
    -minlength 40 \
    -angle 20 \
    -cutoff 0.3 \
    -seed_unidirectional \
    -samples 2 \
    wmfod_norm.mif cst_track_lh_teste.tck \
    -force



