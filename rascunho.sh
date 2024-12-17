# Criação do arquivo annot para cada hemisfério
mris_convert --annot rh.JulichBrainAtlas_3.1.label.gii /home/brunobastos/Mestrado/Dados/fs_subjects/fsaverage/surf/rh.white rh.Julich.annot
mris_convert --annot lh.JulichBrainAtlas_3.1.label.gii /home/brunobastos/Mestrado/Dados/fs_subjects/fsaverage/surf/lh.white lh.Julich.annot


# Teste de corregistro de T1 ao fsaverage antes do recon all
mri_convert "$SUBJECTS_DIR/fsaverage/mri/brain.mgz" brain_fsaverage.nii.gz
flirt -in T1_brain.nii.gz -ref brain_fsaverage.nii.gz -dof 6 -omat T1tofsaverage.mat
flirt -in T1_raw.nii.gz -ref brain_fsaverage.nii.gz -applyxfm -init T1tofsaverage.mat -out T1_raw_fsaverage.nii.gz

convert_xfm -omat t2tofsaverage.mat -concat T1tofsaverage.mat t22t1.mat
flirt -in T2_raw_coreg.nii.gz -ref brain_fsaverage.nii.gz -applyxfm -init t2tofsaverage.mat -out T2_raw_fsaverage.nii.gz -interp trilinear

flirt -in T2_raw_coreg.nii.gz -ref T1_raw_fsaverage.nii.gz -dof 6 -omat T2coregtofsaverage.mat -out T2_raw_fsaverage.nii.gz

recon-all -s Pat548_fsav -i T1_raw_fsaverage.nii.gz -T2 T2_raw_fsaverage.nii.gz -all
mri_aparc2aseg --s Pat548_fsav --new-ribbon --aseg Julich_fsaverage.mgz --annot Julich --annot-table /home/brunobastos/Mestrado/Dados/Atlas/JulichLUT_freesurfer.txt --o output_freesurfer_teste.mgz
mrconvert -datatype uint32 output_freesurfer.mgz Julich_parcels.mif -force 
