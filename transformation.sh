# Corregistro da imagem T2 do atlas com T2 do paciente
echo "Corregistro da imagem T2 do atlas com a imagem T2 no espaço nativo do paciente..."
flirt -in $ATLAS_DIR/T2_mni_resampled.nii.gz -ref T2_resampled.nii.gz -dof 6 -omat atlas2T2.mat
transformconvert atlas2T2.mat $ATLAS_DIR/T2_mni_resampled.nii.gz T2_resampled.nii.gz flirt_import atlas2T2_mrtrix.txt -force
mrconvert $ATLAS_DIR/T2_mni_resampled.nii.gz T2_mni_resampled.mif -force
mrtransform T2_mni_resampled.mif -linear atlas2T2_mrtrix.txt T2_mni_resampled_coreg.mif -force
mrconvert T2_mni_resampled_coreg.mif T2_mni_resampled_coreg.nii.gz -force
echo "Corregistro da imagem T2 do atlas com T2 do paciente finalizado"

# Corregistro dos labels no espaço mni para o espaço do paciente
mrconvert $ATLAS_DIR/output_freesurfer.nii.gz output_mni_freesurfer.mif -force
mrtransform output_mni_freesurfer.mif -interp nearest -datatype uint32 -linear atlas2T2_mrtrix.txt output_mni_freesurfer_coreg.mif -force
mrconvert output_mni_freesurfer_coreg.mif -datatype uint32 output_mni_freesurfer_coreg.nii.gz -force

# Criação das máscaras com as regiões de interesse
python $SCRIPT_DIR/Python/mask_extraction.py

# Corregistro com peso no diencéfalo
echo "Corregistro linear ponderado do diencéfalo ..."
flirt -in T2_mni_resampled_coreg.nii.gz \
 -ref T2_resampled.nii.gz -out midbrain_flirt.nii.gz \
 -inweight mask_midbrain_coreg.nii.gz \
 -refweight mask_midbrain.nii.gz \
 -dof 6 \
 -omat atlas2T2_midbrain.mat
echo "Corregistro linear ponderado do diencéfalo finalizado"

#Corregistro não linear do diencéfalo
antsRegistration --dimensionality 3 \
  --float 1 \
  --output [midbrain_to_T2_,atlas_warped.nii.gz] \
  --transform Rigid[0.1] \
  --metric MI[T2_resampled.nii.gz,midbrain_flirt.nii.gz,1,32,Regular,0.25] \
  --convergence [1000x500x250,1e-6,10] \
  --shrink-factors 8x4x2 \
  --smoothing-sigmas 3x2x1vox \
  --transform Affine[0.1] \
  --metric MI[T2_resampled.nii.gz,midbrain_flirt.nii.gz,1,32,Regular,0.25] \
  --convergence [1000x500x250,1e-6,10] \
  --shrink-factors 8x4x2 \
  --smoothing-sigmas 3x2x1vox \
  --transform SyN[0.1,3,0] \
  --metric CC[T2_resampled.nii.gz,midbrain_flirt.nii.gz,1,4] \
  --convergence [100x70x50x20,1e-6,10] \
  --shrink-factors 8x4x2x1 \
  --smoothing-sigmas 3x2x1x0vox \
  --x [mask_midbrain.nii.gz,mask_midbrain_coreg.nii.gz] \
  --verbose 1
  
# Apply the transformations to the atlas red nucleus and substantia nigra
# Corregister
mrconvert $ATLAS_DIR/Midbrain-NRp_lh_MNI152.nii.gz NRp_lh.mif -force
mrtransform NRp_lh.mif -linear atlas2T2_mrtrix.txt NRp_lh_coreg.mif -force
mrconvert $ATLAS_DIR/Midbrain-NRp_rh_MNI152.nii.gz NRp_rh.mif -force
mrtransform NRp_rh.mif -linear atlas2T2_mrtrix.txt NRp_rh_coreg.mif -force
mrconvert $ATLAS_DIR/Midbrain-NRm_lh_MNI152.nii.gz NRm_lh.mif -force
mrtransform NRm_lh.mif -linear atlas2T2_mrtrix.txt NRm_lh_coreg.mif -force
mrconvert $ATLAS_DIR/Midbrain-NRm_rh_MNI152.nii.gz NRm_rh.mif -force
mrtransform NRm_rh.mif -linear atlas2T2_mrtrix.txt NRm_rh_coreg.mif -force
mrconvert $ATLAS_DIR/Midbrain-SNC_lh_MNI152.nii.gz SNc_lh.mif -force
mrtransform SNc_lh.mif -linear atlas2T2_mrtrix.txt SNc_lh_coreg.mif -force
mrconvert $ATLAS_DIR/Midbrain-SNC_rh_MNI152.nii.gz SNc_rh.mif -force
mrtransform SNc_rh.mif -linear atlas2T2_mrtrix.txt SNc_rh_coreg.mif -force
mrconvert $ATLAS_DIR/Midbrain-SNR_lh_MNI152.nii.gz SNr_lh.mif -force
mrtransform SNr_lh.mif -linear atlas2T2_mrtrix.txt SNr_lh_coreg.mif -force
mrconvert $ATLAS_DIR/Midbrain-SNR_rh_MNI152.nii.gz SNr_rh.mif -force
mrtransform SNr_rh.mif -linear atlas2T2_mrtrix.txt SNr_rh_coreg.mif -force


# Corregister (weighted)
transformconvert atlas2T2_midbrain.mat T2_mni_resampled_coreg.nii.gz T2_resampled.nii.gz flirt_import atlas2T2_midbrain_mrtrix.txt -force
mrtransform NRp_lh_coreg.mif -linear atlas2T2_midbrain_mrtrix.txt NRp_lh_coreg_weighted.mif -force
mrconvert NRp_lh_coreg_weighted.mif NRp_lh_coreg_weighted.nii.gz -force
mrtransform NRp_rh_coreg.mif -linear atlas2T2_midbrain_mrtrix.txt NRp_rh_coreg_weighted.mif -force
mrconvert NRp_rh_coreg_weighted.mif NRp_rh_coreg_weighted.nii.gz -force
mrtransform NRm_lh_coreg.mif -linear atlas2T2_midbrain_mrtrix.txt NRm_lh_coreg_weighted.mif -force
mrconvert NRm_lh_coreg_weighted.mif NRm_lh_coreg_weighted.nii.gz -force
mrtransform NRm_rh_coreg.mif -linear atlas2T2_midbrain_mrtrix.txt NRm_rh_coreg_weighted.mif -force
mrconvert NRm_rh_coreg_weighted.mif NRm_rh_coreg_weighted.nii.gz -force
mrtransform SNc_lh_coreg.mif -linear atlas2T2_midbrain_mrtrix.txt SNc_lh_coreg_weighted.mif -force
mrconvert SNc_lh_coreg_weighted.mif SNc_lh_coreg_weighted.nii.gz -force
mrtransform SNc_rh_coreg.mif -linear atlas2T2_midbrain_mrtrix.txt SNc_rh_coreg_weighted.mif -force
mrconvert SNc_rh_coreg_weighted.mif SNc_rh_coreg_weighted.nii.gz -force
mrtransform SNr_lh_coreg.mif -linear atlas2T2_midbrain_mrtrix.txt SNr_lh_coreg_weighted.mif -force
mrconvert SNr_lh_coreg_weighted.mif SNr_lh_coreg_weighted.nii.gz -force
mrtransform SNr_rh_coreg.mif -linear atlas2T2_midbrain_mrtrix.txt SNr_rh_coreg_weighted.mif -force
mrconvert SNr_rh_coreg_weighted.mif SNr_rh_coreg_weighted.nii.gz -force

# Transform
antsApplyTransforms \
    -d 3 \
    -i NRp_lh_coreg_weighted.nii.gz \
    -r T2_resampled.nii.gz \
    -o NRp_lh_coreg_weighted_transformed.nii.gz \
    -n Linear \
    -t midbrain_to_T2_1Warp.nii.gz \
    -t [midbrain_to_T2_0GenericAffine.mat,1] 

antsApplyTransforms \
    -d 3 \
    -i NRp_rh_coreg_weighted.nii.gz \
    -r T2_resampled.nii.gz \
    -o NRp_rh_coreg_weighted_transformed.nii.gz \
    -n Linear \
    -t midbrain_to_T2_1Warp.nii.gz \
    -t [midbrain_to_T2_0GenericAffine.mat,1] 

antsApplyTransforms \
    -d 3 \
    -i NRm_lh_coreg_weighted.nii.gz \
    -r T2_resampled.nii.gz \
    -o NRm_lh_coreg_weighted_transformed.nii.gz \
    -n Linear \
    -t midbrain_to_T2_1Warp.nii.gz \
    -t [midbrain_to_T2_0GenericAffine.mat,1] 

antsApplyTransforms \
    -d 3 \
    -i NRm_rh_coreg_weighted.nii.gz \
    -r T2_resampled.nii.gz \
    -o NRm_rh_coreg_weighted_transformed.nii.gz \
    -n Linear \
    -t midbrain_to_T2_1Warp.nii.gz \
    -t [midbrain_to_T2_0GenericAffine.mat,1] 

antsApplyTransforms \
    -d 3 \
    -i SNc_lh_coreg_weighted.nii.gz \
    -r T2_resampled.nii.gz \
    -o SNc_lh_coreg_weighted_transformed.nii.gz \
    -n Linear \
    -t midbrain_to_T2_1Warp.nii.gz \
    -t [midbrain_to_T2_0GenericAffine.mat,1] 

antsApplyTransforms \
    -d 3 \
    -i SNc_rh_coreg_weighted.nii.gz \
    -r T2_resampled.nii.gz \
    -o SNc_rh_coreg_weighted_transformed.nii.gz \
    -n Linear \
    -t midbrain_to_T2_1Warp.nii.gz \
    -t [midbrain_to_T2_0GenericAffine.mat,1] 

antsApplyTransforms \
    -d 3 \
    -i SNr_lh_coreg_weighted.nii.gz \
    -r T2_resampled.nii.gz \
    -o SNr_lh_coreg_weighted_transformed.nii.gz \
    -n Linear \
    -t midbrain_to_T2_1Warp.nii.gz \
    -t [midbrain_to_T2_0GenericAffine.mat,1] 

antsApplyTransforms \
    -d 3 \
    -i SNr_rh_coreg_weighted.nii.gz \
    -r T2_resampled.nii.gz \
    -o SNr_rh_coreg_weighted_transformed.nii.gz \
    -n Linear \
    -t midbrain_to_T2_1Warp.nii.gz \
    -t [midbrain_to_T2_0GenericAffine.mat,1] 
    
# Corregistro com peso no quarto ventrículo 
echo "Corregistro linear ponderado do quarto ventrículo ..."
flirt -in T2_mni_resampled_coreg.nii.gz \
 -ref T2_resampled.nii.gz -out ventricle_flirt.nii.gz \
 -inweight mask_ventricle_coreg.nii.gz \
 -refweight mask_ventricle.nii.gz \
 -dof 6 \
 -omat atlas2T2_ventricle.mat
echo "Corregistro linear ponderado do quarto ventrículo finalizado"
 
antsRegistration --dimensionality 3 \
  --float 1 \
  --output [ventricle_to_T2_,ventricle_warped.nii.gz] \
  --transform Rigid[0.1] \
  --metric MI[T2_resampled.nii.gz,ventricle_flirt.nii.gz,1,32,Regular,0.25] \
  --convergence [1000x500x250,1e-6,10] \
  --shrink-factors 8x4x2 \
  --smoothing-sigmas 3x2x1vox \
  --transform Affine[0.1] \
  --metric MI[T2_resampled.nii.gz,ventricle_flirt.nii.gz,1,32,Regular,0.25] \
  --convergence [1000x500x250,1e-6,10] \
  --shrink-factors 8x4x2 \
  --smoothing-sigmas 3x2x1vox \
  --transform SyN[0.1,3,0] \
  --metric CC[T2_resampled.nii.gz,ventricle_flirt.nii.gz,1,4] \
  --convergence [100x70x50x20,1e-6,10] \
  --shrink-factors 8x4x2x1 \
  --smoothing-sigmas 3x2x1x0vox \
  --x [mask_ventricle.nii.gz, mask_ventricle_coreg.nii.gz] \
  --verbose 1

# Apply the transformations to the atlas dentate nucleus
# Corregister
mrconvert $ATLAS_DIR/Cerebellum-Ndentd_lh_MNI152.nii.gz DNd_lh.mif -force
mrtransform DNd_lh.mif -linear atlas2T2_mrtrix.txt DNd_lh_coreg.mif -force
mrconvert $ATLAS_DIR/Cerebellum-Ndentd_rh_MNI152.nii.gz DNd_rh.mif -force
mrtransform DNd_rh.mif -linear atlas2T2_mrtrix.txt DNd_rh_coreg.mif -force

# Corregister (weighted)
transformconvert atlas2T2_ventricle.mat T2_mni_resampled_coreg.nii.gz T2_resampled.nii.gz flirt_import atlas2T2_ventricle_mrtrix.txt -force
mrtransform DNd_lh_coreg.mif -linear atlas2T2_ventricle_mrtrix.txt DNd_lh_coreg_weighted.mif -force
mrconvert DNd_lh_coreg_weighted.mif DNd_lh_coreg_weighted.nii.gz -force
mrtransform DNd_rh_coreg.mif -linear atlas2T2_ventricle_mrtrix.txt DNd_rh_coreg_weighted.mif -force
mrconvert DNd_rh_coreg_weighted.mif DNd_rh_coreg_weighted.nii.gz -force

#Transform
antsApplyTransforms \
    -d 3 \
    -i DNd_lh_coreg_weighted.nii.gz \
    -r T2_resampled.nii.gz \
    -o DNd_lh_coreg_weighted_transformed.nii.gz \
    -n Linear \
    -t ventricle_to_T2_1Warp.nii.gz \
    -t [ventricle_to_T2_0GenericAffine.mat,1] 

antsApplyTransforms \
    -d 3 \
    -i DNd_rh_coreg_weighted.nii.gz \
    -r T2_resampled.nii.gz \
    -o DNd_rh_coreg_weighted_transformed.nii.gz \
    -n Linear \
    -t ventricle_to_T2_1Warp.nii.gz \
    -t [ventricle_to_T2_0GenericAffine.mat,1] 
    
# Apply the transformations to the atlas dentate nucleus
# Corregister
mrconvert $ATLAS_DIR/Cerebellum-Ndentv_lh_MNI152.nii.gz DNv_lh.mif -force
mrtransform DNv_lh.mif -linear atlas2T2_mrtrix.txt DNv_lh_coreg.mif -force
mrconvert $ATLAS_DIR/Cerebellum-Ndentv_rh_MNI152.nii.gz DNv_rh.mif -force
mrtransform DNv_rh.mif -linear atlas2T2_mrtrix.txt DNv_rh_coreg.mif -force

# Corregister (weighted)
mrtransform DNv_lh_coreg.mif -linear atlas2T2_ventricle_mrtrix.txt DNv_lh_coreg_weighted.mif -force
mrconvert DNv_lh_coreg_weighted.mif DNv_lh_coreg_weighted.nii.gz -force
mrtransform DNv_rh_coreg.mif -linear atlas2T2_ventricle_mrtrix.txt DNv_rh_coreg_weighted.mif -force
mrconvert DNv_rh_coreg_weighted.mif DNv_rh_coreg_weighted.nii.gz -force

#Transform
antsApplyTransforms \
    -d 3 \
    -i DNv_lh_coreg_weighted.nii.gz \
    -r T2_resampled.nii.gz \
    -o DNv_lh_coreg_weighted_transformed.nii.gz \
    -n Linear \
    -t ventricle_to_T2_1Warp.nii.gz \
    -t [ventricle_to_T2_0GenericAffine.mat,1] 

antsApplyTransforms \
    -d 3 \
    -i DNv_rh_coreg_weighted.nii.gz \
    -r T2_resampled.nii.gz \
    -o DNv_rh_coreg_weighted_transformed.nii.gz \
    -n Linear \
    -t ventricle_to_T2_1Warp.nii.gz \
    -t [ventricle_to_T2_0GenericAffine.mat,1] 
    

				 


