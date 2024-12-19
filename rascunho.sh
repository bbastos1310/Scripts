# Criação do arquivo annot para cada hemisfério
mris_convert --annot rh.JulichBrainAtlas_3.1.label.gii /home/brunobastos/Mestrado/Dados/fs_subjects/fsaverage/surf/rh.white rh.Julich.annot
mris_convert --annot lh.JulichBrainAtlas_3.1.label.gii /home/brunobastos/Mestrado/Dados/fs_subjects/fsaverage/surf/lh.white lh.Julich.annot


# Teste de corregistro de T1 ao fsaverage antes do recon all
mri_convert "$SUBJECTS_DIR/fsaverage/mri/brain.mgz" brain_fsaverage.nii.gz
flirt -in T1_brain.nii.gz -ref brain_fsaverage.nii.gz -dof 6 -omat T1tofsaverage.mat
flirt -in T1_raw.nii.gz -ref brain_fsaverage.nii.gz -applyxfm -init T1tofsaverage.mat -out T1_raw_fsaverage.nii.gz

convert_xfm -omat t2tofsaverage.mat -concat T1tofsaverage.mat t22t1.mat
flirt -in T2_raw_coreg.nii.gz -ref brain_fsaverage.nii.gz -applyxfm -init t2tofsaverage.mat -out T2_raw_fsaverage.nii.gz -interp trilinear

recon-all -s Pat548_fsav -i T1_raw_fsaverage.nii.gz -T2 T2_raw_fsaverage.nii.gz -all

mri_surf2surf --srcsubject fsaverage --trgsubject Pat548_fsav --hemi lh --sval-annot $SUBJECTS_DIR/fsaverage/label/lh.Julich.annot  --tval $SUBJECTS_DIR/Pat548_fsav/label/lh.Julich_pat.annot
mri_surf2surf --srcsubject fsaverage --trgsubject Pat548_fsav --hemi rh --sval-annot $SUBJECTS_DIR/fsaverage/label/rh.Julich.annot  --tval $SUBJECTS_DIR/Pat548_fsav/label/rh.Julich_pat.annot

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
