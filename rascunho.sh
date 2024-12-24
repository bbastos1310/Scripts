TRANSFORMAÇÃO DO ATLAS (TEMPLATE T1 -> ESPAÇO T1 DO PACIENTE)

# Converter o arquivo T1 da pasta mri do peciente no freesurfer (resolução de 256x256x256)
mri_convert ~/Mestrado/Dados/fs_subjects/Pat548/mri/T1.mgz T1_resampled.nii.gz

# Converter o arquivo T1 do template do atlas para nii.gz
mrconvert ~/Mestrado/Dados/Atlas/mni_icbm152_t1_tal_nlin_asym_09c.nii mni15209c.nii.gz -force

# Corregistrar a imagem do template à imagem T1 do paciente usando flirt e mrtrix
flirt -in mni15209c.nii.gz -ref T1_resampled.nii.gz -dof 6 -omat atlas2T1.mat
transformconvert atlas2T1.mat mni15209c.nii.gz T1_resampled.nii.gz flirt_import atlas2T1_mrtrix.txt -force
mrconvert ~/Mestrado/Dados/Atlas/mni_icbm152_t1_tal_nlin_asym_09c.nii mni15209c.mif -force
mrtransform mni15209c.mif -linear atlas2T1_mrtrix.txt mni15209c_coreg.mif -force
mrconvert mni15209c_coreg.mif mni15209c_coreg.nii.gz -force

# Aplicar transformação não linear no template para se ajustar ao paciente
antsRegistration \
    --dimensionality 3 \
    --float 0 \
    --output [ T1Atlas_to_T1Raw_, T1Atlas_warped.nii.gz ] \
    --interpolation Linear \
    --use-histogram-matching 0 \
    --initial-moving-transform [ T1_resampled.nii.gz,mni15209c_coreg.nii.gz, 1 ] \
    --transform Rigid[ 0.1 ] \
    --metric MI[ T1_resampled.nii.gz,mni15209c_coreg.nii.gz, 1, 32, Regular, 0.25] \
    --convergence [ 1000x500x250x100, 1e-6, 10] \
    --shrink-factors 8x4x2x1 \
    --smoothing-sigmas 3x2x1x0vox \
    --transform Affine[ 0.1 ] \
    --metric MI[ T1_resampled.nii.gz,mni15209c_coreg.nii.gz, 1, 32, Regular, 0.25 ] \
    --convergence [ 1000x500x250x100, 1e-6 , 10 ] \
    --shrink-factors 8x4x2x1 \
    --smoothing-sigmas 3x2x1x0vox \
    --transform SyN[ 0.1, 3, 0] \
    --metric CC[ T1_resampled.nii.gz,mni15209c_coreg.nii.gz, 1, 4] \
    --convergence [ 100x70x50x20, 1e-6, 10] \
    --shrink-factors 8x4x2x1 \
    --smoothing-sigmas 3x2x1x0vox \
    --verbose 1

# Corregistrar o atlas ao paciente a partir da matriz de transformação obtida na etapa anterior
mrconvert /home/brunobastos/Mestrado/Dados/Atlas/Julich_aseg.nii.gz Julich_aseg.mif -force
mrtransform Julich_aseg.mif -linear atlas2T1_mrtrix.txt Julich_aseg_coreg.mif -force
mrconvert Julich_aseg_coreg.mif Julich_aseg_coreg.nii.gz -force

# Aplicar a transformação não linear ao atlas a partir das matrizes de transformação obtidas anteriormente
antsApplyTransforms \
    -d 3 \
    -i Julich_aseg_coreg.nii.gz \
    -r T1_raw.nii.gz \
    -o Julich_aseg_coreg_transformed.nii.gz \
    -n NearestNeighbor \
    -t T1Atlas_to_T1Raw_1Warp.nii.gz \
    -t [T1Atlas_to_T1Raw_0GenericAffine.mat,1] 

mri_convert Julich_aseg_coreg_transformed.nii.gz Julich_aseg_coreg_transformed.mgz

TRANSFORMAÇÃO DO ATLAS (TEMPLATE WM -> ESPAÇO T1 DO PACIENTE USANDO WM)

# Converter o arquivo T1 da pasta mri do peciente no freesurfer (resolução de 256x256x256)
mri_convert ~/Mestrado/Dados/fs_subjects/Pat548/mri/T1.mgz T1_resampled.nii.gz

# Converter o arquivo T1 do template do atlas para nii.gz
mrconvert ~/Mestrado/Dados/Atlas/mni_icbm152_t1_tal_nlin_asym_09c.nii mni15209c.nii.gz -force

# Corregistrar a imagem do template à imagem T1 do paciente usando flirt e mrtrix
flirt -in mni15209c.nii.gz -ref T1_resampled.nii.gz -dof 6 -omat atlas2T1.mat
transformconvert atlas2T1.mat mni15209c.nii.gz T1_resampled.nii.gz flirt_import atlas2T1_mrtrix.txt -force
mrconvert ~/Mestrado/Dados/Atlas/mni_icbm152_t1_tal_nlin_asym_09c.nii mni15209c.mif -force
mrtransform mni15209c.mif -linear atlas2T1_mrtrix.txt mni15209c_coreg.mif -force
mrconvert mni15209c_coreg.mif mni15209c_coreg.nii.gz -force

# Aplicar transformação não linear no template para se ajustar ao paciente usando T1
antsRegistration \
    --dimensionality 3 \
    --float 0 \
    --output [ T1Atlas_to_T1Raw_, T1Atlas_warped.nii.gz ] \
    --interpolation Linear \
    --use-histogram-matching 0 \
    --initial-moving-transform [ T1_resampled.nii.gz,mni15209c_coreg.nii.gz, 1 ] \
    --transform Rigid[ 0.1 ] \
    --metric MI[ T1_resampled.nii.gz,mni15209c_coreg.nii.gz, 1, 32, Regular, 0.25] \
    --convergence [ 1000x500x250x100, 1e-6, 10] \
    --shrink-factors 8x4x2x1 \
    --smoothing-sigmas 3x2x1x0vox \
    --transform Affine[ 0.1 ] \
    --metric MI[ T1_resampled.nii.gz,mni15209c_coreg.nii.gz, 1, 32, Regular, 0.25 ] \
    --convergence [ 1000x500x250x100, 1e-6 , 10 ] \
    --shrink-factors 8x4x2x1 \
    --smoothing-sigmas 3x2x1x0vox \
    --transform SyN[ 0.1, 3, 0] \
    --metric CC[ T1_resampled.nii.gz,mni15209c_coreg.nii.gz, 1, 4] \
    --convergence [ 100x70x50x20, 1e-6, 10] \
    --shrink-factors 8x4x2x1 \
    --smoothing-sigmas 3x2x1x0vox \
    --verbose 1

# Corregistrar o atlas ao paciente a partir da matriz de transformação obtida na etapa anterior
mrconvert /home/brunobastos/Mestrado/Dados/Atlas/Julich_aseg.nii.gz Julich_aseg.mif -force
mrtransform Julich_aseg.mif -linear atlas2T1_mrtrix.txt Julich_aseg_coreg.mif -force
mrconvert Julich_aseg_coreg.mif Julich_aseg_coreg.nii.gz -force

# Aplicar a transformação não linear ao atlas a partir das matrizes de transformação obtidas anteriormente
antsApplyTransforms \
    -d 3 \
    -i Julich_aseg_coreg.nii.gz \
    -r T1_raw.nii.gz \
    -o Julich_aseg_coreg_transformed.nii.gz \
    -n NearestNeighbor \
    -t T1Atlas_to_T1Raw_1Warp.nii.gz \
    -t [T1Atlas_to_T1Raw_0GenericAffine.mat,1] 

mri_convert Julich_aseg_coreg_transformed.nii.gz Julich_aseg_coreg_transformed.mgz



ATRIBUIÇÃO DE LABELS USANDO FREESURFER

# Atribuição dos labels corticais a partir dos arquivos .annot e dos labels subcorticais a partir do atlas 
mri_surf2surf --srcsubject fsaverage --trgsubject Pat548 --hemi lh --sval-annot $SUBJECTS_DIR/fsaverage/label/lh.Julich.annot  --tval $SUBJECTS_DIR/Pat548/label/lh.Julich_pat.annot
mri_surf2surf --srcsubject fsaverage --trgsubject Pat548 --hemi rh --sval-annot $SUBJECTS_DIR/fsaverage/label/rh.Julich.annot  --tval $SUBJECTS_DIR/Pat548/label/rh.Julich_pat.annot
mri_convert Julich_mni152_transformed.nii.gz Julich_mni152_transformed.mgz
mri_aparc2aseg --new-ribbon --s Pat548 --annot JULICH --o output_freesurfer.mgz
mrconvert -datatype uint32 output_freesurfer.mgz output_freesurfer.nii.gz -force

# ajustes da segmentação subcortical
labelsgmfix nodes.mif T1w_acpc_dc_restore_brain.nii.gz BN_Atlas_246_default.txt nodes_fixsgm.mif -premasked



mris_convert --annot rh.JulichBrainAtlas_3.1_colin27.label.gii \
             /home/users/llewis/freesurfer/subjects/fsaverage/surf/fsavg.R.sphere.native \
             rh.JulichBrainAtlas_3.1_colin27.annot

mris_info $SUBJECTS_DIR/Pat548/label/lh.Julich_pat.annot

# Conversão de label.gii para .annot (Esse comando gera o arquivo diretamente na pasta surf de fsaverage
mris_convert --annot lh.JulichBrainAtlas_3.1.label.gii "$SUBJECTS_DIR/fsaverage/surf/lh.sphere" lh.Julich.annot
mris_convert --annot rh.JulichBrainAtlas_3.1.label.gii "$SUBJECTS_DIR/fsaverage/surf/rh.sphere" rh.Julich.annot

mri_convert Julich_transformed_updated.nii.gz Julich_transformed_updated.mgz

mris_anatomical_stats -a Julich_pat.annot -f output_stats.txt Pat548 lh


run_first_all -i input_T1.nii -o output_first

# Corregistrar a região de interesse ao paciente a partir da matriz de transformação obtida na etapa anterior
mrconvert Midbrain-NRp_lh_MNI152.nii.gz Midbrain-NRp_lh_MNI152.mif -force
mrtransform Midbrain-NRp_lh_MNI152.mif -linear atlas2T1_mrtrix.txt NRp_coreg.mif -force
mrconvert NRp_coreg.mif NRp_coreg.nii.gz -force

# Aplicar a transformação não linear ao atlas a partir das matrizes de transformação obtidas anteriormente
antsApplyTransforms \
    -d 3 \
    -i NRp_coreg.nii.gz \
    -r T1_raw.nii.gz \
    -o NRp_coreg_transformed.nii.gz \
    -n Linear \
    -t T1Atlas_to_T1Raw_1Warp.nii.gz \
    -t [T2Atlas_to_T2Raw_0GenericAffine.mat,1] 

flirt -in 021_raw_24.nii.gz -ref T1_raw.nii.gz -dof 6 -omat wmn2t1.mat
transformconvert wmn2t1.mat 021_raw.nii.gz T1_raw.nii.gz flirt_import wmn2t1_mrtrix.txt -force
mrtransform 021_raw.mif -linear wmn2t1_mrtrix.txt 021_raw_coreg.mif -force
mrconvert 021_raw_coreg.mif 021_raw_coreg.nii.gz -force

mrconvert 021_raw_24.mif 021_raw_24.nii.gz -force    
flirt -in 021_raw_24.nii.gz -ref T1_raw.nii.gz -dof 6 -omat mprage2t1.mat
transformconvert mprage2t1.mat 021_raw_24.nii.gz T1_raw.nii.gz flirt_import mprage2t1_mrtrix.txt -force
mrtransform 021_raw_24.mif -linear mprage2t1_mrtrix.txt 021_raw_24_coreg_temp.mif -force
mrgrid 021_raw_24_coreg_temp.mif regrid -template 021_raw_coreg.mif 021_raw_24_coreg.mif -force
mrconvert 021_raw_24_coreg.mif 021_raw_24_coreg.nii.gz -force


# Converter o arquivo T2 do template do atlas para nii.gz
mrconvert ~/Mestrado/Dados/Atlas/mni_icbm152_t2_tal_nlin_asym_09c.nii mni152_T2.nii.gz -force

# Corregistrar a imagem do template à imagem T2 do paciente usando flirt e mrtrix
flirt -in mni152_T2.nii.gz -ref T2_raw_coreg.nii.gz -dof 6 -omat atlas2T2.mat
transformconvert atlas2T2.mat mni152_T2.nii.gz T2_raw_coreg.nii.gz flirt_import atlas2T2_mrtrix.txt -force
mrconvert ~/Mestrado/Dados/Atlas/mni_icbm152_t2_tal_nlin_asym_09c.nii mni152_T2.mif -force
mrtransform mni152_T2.mif -linear atlas2T2_mrtrix.txt mni152_T2_coreg.mif -force
mrconvert mni152_T2_coreg.mif mni152_T2_coreg.nii.gz -force

# Aplicar transformação não linear no template para se ajustar ao paciente usando T1
antsRegistration \
    --dimensionality 3 \
    --float 0 \
    --output [ T2Atlas_to_T2Raw_, T2Atlas_warped.nii.gz ] \
    --interpolation Linear \
    --use-histogram-matching 0 \
    --initial-moving-transform [ T2_raw_coreg.nii.gz,mni152_T2_coreg.nii.gz, 1 ] \
    --transform Rigid[ 0.1 ] \
    --metric MI[ T2_raw_coreg.nii.gz,mni152_T2_coreg.nii.gz, 1, 32, Regular, 0.25] \
    --convergence [ 1000x500x250x100, 1e-6, 10] \
    --shrink-factors 8x4x2x1 \
    --smoothing-sigmas 3x2x1x0vox \
    --transform Affine[ 0.1 ] \
    --metric MI[ T2_raw_coreg.nii.gz,mni152_T2_coreg.nii.gz, 1, 32, Regular, 0.25 ] \
    --convergence [ 1000x500x250x100, 1e-6 , 10 ] \
    --shrink-factors 8x4x2x1 \
    --smoothing-sigmas 3x2x1x0vox \
    --transform SyN[ 0.1, 3, 0] \
    --metric CC[ T2_raw_coreg.nii.gz,mni152_T2_coreg.nii.gz, 1, 4] \
    --convergence [ 100x70x50x20, 1e-6, 10] \
    --shrink-factors 8x4x2x1 \
    --smoothing-sigmas 3x2x1x0vox \
    --verbose 1


# Exemplo de máscara para transformação não linear de uma região de interesse
mrconvert ~/Mestrado/Dados/Atlas/mni_icbm152_t1_tal_nlin_asym_09c_mask.nii mni152_mask.mif -force
mrtransform mni152_mask.mif -linear atlas2T2_mrtrix.txt mni152_mask_coreg.mif -force
mrconvert mni152_mask_coreg.mif mni152_mask_coreg.nii.gz -force

mrgrid T2_raw_coreg.mif regrid -template T1_resampled.mif T2_raw_coreg_resampled.mif -force
mrconvert T2_raw_coreg_resampled.mif T2_raw_coreg_resampled.nii.gz -force
mrconvert mni152_T2_coreg.nii.gz mni152_T2_coreg.mif -force
mrgrid mni152_T2_coreg.mif regrid -template T1_resampled.mif mni152_T2_coreg_resampled.mif -force
mrconvert mni152_T2_coreg_resampled.mif mni152_T2_coreg_resampled.nii.gz -force
mrconvert NRp_coreg.nii.gz NRp_coreg.mif -force
mrgrid NRp_coreg.mif regrid -template T1_resampled.mif NRp_coreg_resampled.mif -force
mrconvert NRp_coreg_resampled.mif NRp_coreg_resampled.nii.gz -force



antsRegistration \
    --dimensionality 3 \
    --float 0 \
    --output [ ROI_to_T2Raw_, ROI_warped.nii.gz ] \
    --interpolation Linear \
    --use-histogram-matching 0 \
    --initial-moving-transform [ T2_raw_coreg_resampled.nii.gz, mni152_T2_coreg_resampled.nii.gz, 1 ] \
    --transform Rigid[ 0.1 ] \
    --metric MI[ T2_raw_coreg_resampled.nii.gz, mni152_T2_coreg_resampled.nii.gz, 1, 32, Regular, 0.25] \
    --convergence [ 1000x500x250x100, 1e-6, 10] \
    --shrink-factors 8x4x2x1 \
    --smoothing-sigmas 3x2x1x0vox \
    --transform Affine[ 0.1 ] \
    --metric MI[ T2_raw_coreg_resampled.nii.gz, mni152_T2_coreg_resampled.nii.gz, 1, 32, Regular, 0.25 ] \
    --convergence [ 1000x500x250x100, 1e-6 , 10 ] \
    --shrink-factors 8x4x2x1 \
    --smoothing-sigmas 3x2x1x0vox \
    --transform SyN[ 0.1, 3, 0] \
    --metric CC[ T2_raw_coreg_resampled.nii.gz, mni152_T2_coreg_resampled.nii.gz, 1, 4] \
    --convergence [ 100x70x50x20, 1e-6, 10] \
    --shrink-factors 8x4x2x1 \
    --smoothing-sigmas 3x2x1x0vox \
    --masks [mask_transform.nii.gz, mask_transform.nii.gz] \
    --verbose 1

antsApplyTransforms \
    -d 3 \
    -i NRp_coreg_resampled.nii.gz \
    -r T2_raw_coreg.nii.gz \
    -o NRp_coreg_resampled_transformed.nii.gz \
    -n Linear \
    -t ROI_to_T2Raw_1Warp.nii.gz \
    -t [ROI_to_T2Raw_0GenericAffine.mat,1] 
    
    
  recon-all -s Pat_mni -i /home/brunobastos/Downloads/mni_icbm152_nlin_asym_09c_nifti/mni_icbm152_nlin_asym_09c/mni_icbm152_t1_tal_nlin_asym_09c.nii -T2 /home/brunobastos/Downloads/mni_icbm152_nlin_asym_09c_nifti/mni_icbm152_nlin_asym_09c/mni_icbm152_t2_tal_nlin_asym_09c.nii -all
