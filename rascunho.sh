# Criação do arquivo annot para cada hemisfério
mris_convert --annot rh.JulichBrainAtlas_3.1.label.gii /home/brunobastos/Mestrado/Dados/fs_subjects/fsaverage/surf/rh.white rh.Julich.annot
mris_convert --annot lh.JulichBrainAtlas_3.1.label.gii /home/brunobastos/Mestrado/Dados/fs_subjects/fsaverage/surf/lh.white lh.Julich.annot

convert_xfm -omat t2tofsaverage.mat -concat T1tofsaverage.mat t22t1.mat
flirt -in T2_raw_coreg.nii.gz -ref brain_fsaverage.nii.gz -applyxfm -init t2tofsaverage.mat -out T2_raw_fsaverage.nii.gz -interp trilinear


#mri_vol2vol --mov $SUBJECTS_DIR/fsaverage/mri/Julich_fsaverage.nii.gz --targ T1_raw_fsaverage.nii.gz --regheader --o Julich_fsaverage_pat.nii.gz
flirt -in $SUBJECTS_DIR/fsaverage/mri/Julich_fsaverage.nii.gz -ref T1_raw_fsaverage.nii.gz -omat template_to_T1.mat -dof 12
fnirt --in=$SUBJECTS_DIR/fsaverage/mri/Julich_fsaverage.nii.gz --ref=T1_raw_fsaverage.nii.gz --aff=template_to_T1.mat --cout=template_to_T1_nonlinear_coeff
applywarp --in=in=$SUBJECTS_DIR/fsaverage/mri/Julich_fsaverage.nii.gz --ref=T1_raw_fsaverage.nii.gz --warp=template_to_T1_nonlinear_coeff --interp=nn --out=Julich_fsaverage_pat.nii.gz

flirt -in brain_fsaverage.nii.gz -ref T1_raw_fsaverage.nii.gz -omat template_to_T1.mat -dof 12
fnirt --in=brain_fsaverage.nii.gz --ref=T1_raw_fsaverage.nii.gz --aff=template_to_T1.mat --cout=template_to_T1_nonlinear_coeff
applywarp --in=in=$SUBJECTS_DIR/fsaverage/mri/Julich_fsaverage.nii.gz --ref=T1_raw_fsaverage.nii.gz --warp=template_to_T1_nonlinear_coeff --interp=nn --out=Julich_fsaverage_pat.nii.gz
 
mri_aparc2aseg --s Pat548_fsav --old-ribbon --aseg Julich_fsaverage.mgz --annot Julich --annot-table /home/brunobastos/Mestrado/Dados/Atlas/JulichLUT_freesurfer.txt --o output_freesurfer_teste.mgz
mrconvert -datatype uint32 output_freesurfer.mgz Julich_parcels.mif -force 

mrconvert "$SUBJECTS_DIR/fsaverage/mri/Julich_fsaverage.nii.gz" Julich_fsaverage.mif
mrgrid T1_raw.mif regrid -template Julich_fsaverage.mif T1_raw_resampled.mif -force
mrconvert T1_raw_resampled.mif T1_raw_resampled.nii.gz
flirt -in brain_fsaverage.nii.gz -ref T1_raw_resampled.nii.gz -dof 6 -omat fsaveragetoT1.mat
fnirt --in=brain_fsaverage.nii.gz --ref=T1_raw_resampled.nii.gz --aff=fsaveragetoT1.mat --cout=fsaveragetoT1_nonlin_coeff
applywarp --in=in=$SUBJECTS_DIR/fsaverage/mri/Julich_fsaverage.nii.gz --ref=T1_raw_resampled.nii.gz --warp=template_to_T1_nonlinear_coeff --interp=nn --out=Julich_fsaverage_pat.nii.gz

193x229x193





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

antsApplyTransforms \
    -d 3 \
    -i Julich_mni152_coreg.nii.gz \
    -r T1_raw.nii.gz \
    -o Julich_mni152_transformed.nii.gz \
    -n NearestNeighbor \
    -t T1Atlas_to_T1Raw_1Warp.nii.gz \
    -t [T1Atlas_to_T1Raw_0GenericAffine.mat,1] 

antsApplyTransforms -d 3 \
                    -i moving_image.nii.gz \
                    -r fixed_image.nii.gz \
                    -o output_image.nii.gz \
                    -t transform1.nii.gz \
                    -t transform2.mat \
                    --interpolation Linear

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

# Atribuição dos labels corticais a partir dos arquivos .annot e dos labels subcorticais a partir do atlas 
mri_surf2surf --srcsubject fsaverage --trgsubject Pat548 --hemi lh --sval-annot $SUBJECTS_DIR/fsaverage/label/lh.Julich.annot  --tval $SUBJECTS_DIR/Pat548/label/lh.Julich_pat.annot
mri_surf2surf --srcsubject fsaverage --trgsubject Pat548 --hemi rh --sval-annot $SUBJECTS_DIR/fsaverage/label/rh.Julich.annot  --tval $SUBJECTS_DIR/Pat548/label/rh.Julich_pat.annot
mri_convert Julich_mni152_transformed.nii.gz Julich_mni152_transformed.mgz
mri_aparc2aseg --s Pat548 --old-ribbon --aseg Julich_transformed_updated.mgz --annot Julich_pat --annot-table /home/brunobastos/Mestrado/Dados/Atlas/JulichLUT_complete.txt --debug --o output_freesurfer.mgz
mri_aparc2aseg --s Pat548 --old-ribbon --annot Julich_pat --annot-table /home/brunobastos/Mestrado/Dados/Atlas/JulichLUT_complete.txt --aseg Julich_transformed_updated.mgz --debug --o output_freesurfer.mgz


mrconvert -datatype uint32 output_freesurfer.mgz Julich_parcels.mif -force

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


