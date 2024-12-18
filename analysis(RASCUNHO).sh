        
      # Create analisys directory
      cd "$PAT_DIR"
      mkdir -p Analysis
      ANALYSIS="${PAT_DIR}/Analysis"
      cd "$ANALYSIS"     
      
      if [ ! -a "T1_raw.mif" ]; then
      # Copy T1 from pat_PRE
      cp "$OUT_PRE/T1_raw.mif" "$ANALYSIS"
      fi
      
      if [ ! -a "T1_raw_24.mif" ]; then
      # Copy T1 from pat_24
      cp "$OUT_24/T1_raw_24.mif" "$ANALYSIS"
      fi
      
      # Create maps (PRE)
      cd "$OUT_PRE"
      dwi2tensor dwi_den_unr_preproc_unb_reg.mif -mask "$OUT_PRE/dwi_mask_up_reg.mif" tensor.mif -force
      tensor2metric tensor.mif -vec fa_map.mif -adc adc_map.mif -cl cl_map.mif -cs cs_map.mif -cp cp_map.mif -ad ad_map.mif -rd rd_map.mif -force
      mrcalc fa_map.mif -abs fa_map_abs.mif -force
      cp -f fa_map_abs.mif adc_map.mif cl_map.mif cs_map.mif cp_map.mif ad_map.mif rd_map.mif "$ANALYSIS"
      cp hcpmmp1.csv "$ANALYSIS/hcpmmp1.csv"
      cp hcpmmp1_parcels.mif "$ANALYSIS/hcpmmp1_parcels.mif"
      cp dwi_mask_up_reg.mif "$ANALYSIS/dwi_mask_up_reg.mif"
      cd "$ANALYSIS"
      if [ ! -d Nifti ] ; then
          mkdir Nifti
      fi
      mrconvert fa_map_abs.mif -stride 1,2,3,4 "$ANALYSIS/Nifti/fa_map_abs.nii.gz" -force
      mrconvert adc_map.mif -stride 1,2,3 "$ANALYSIS/Nifti/adc_map.nii.gz" -force
      mrconvert cl_map.mif -stride 1,2,3 "$ANALYSIS/Nifti/cl_map.nii.gz" -force
      mrconvert cs_map.mif -stride 1,2,3 "$ANALYSIS/Nifti/cs_map.nii.gz" -force
      mrconvert cp_map.mif -stride 1,2,3 "$ANALYSIS/Nifti/cp_map.nii.gz" -force
      mrconvert ad_map.mif -stride 1,2,3 "$ANALYSIS/Nifti/ad_map.nii.gz" -force
      mrconvert rd_map.mif -stride 1,2,3 "$ANALYSIS/Nifti/rd_map.nii.gz" -force
      mrconvert T1_raw.mif -stride 1,2,3 "$ANALYSIS/Nifti/T1.nii.gz" -force
      mrconvert hcpmmp1_parcels.mif -stride 1,2,3 "$ANALYSIS/Nifti/hcpmmp1_parcels.nii.gz" -force
      mrconvert dwi_mask_up_reg.mif -stride 1,2,3 "$ANALYSIS/Nifti/dwi_mask_up_reg.nii.gz" -force      
      
      cd "$OUT_24"
      # Coregister T1_raw_24 with T1_raw
      mrconvert T1_raw_24.mif T1_raw_24.nii.gz -force
      flirt -in T1_raw_24.nii.gz -ref T1_raw.nii.gz -dof 6 -omat t12t1.mat
      transformconvert t12t1.mat T1_raw_24.nii.gz T1_raw.nii.gz flirt_import t12t1_mrtrix.txt -force
      
      MEAN1=$(mrinfo "$OUT_24/T1_raw_24" -size)
      MEAN2=$(mrinfo "$OUT_PRE/T1_raw.mif" -size)
      if [ "$MEAN1" != "$MEAN2" ]; then
        echo "Os arquivos T1_raw_24 e T1_raw possuem um número diferente de cortes, será feito um resample do arquivo T1_raw_24 para que fiquem com o mesmo número de cortes. Isso é necessário para que a comparação entre as duas imagens tenha a mesma referência, confira o arquivo de saída."
        mrtransform T1_raw_24.mif -linear t12t1_mrtrix.txt T1_raw_24_coreg_temp.mif -force
        mrgrid T1_raw_24_coreg_temp.mif regrid -template "$OUT_PRE/T1_raw.mif" T1_raw_24_coreg.mif -force
      else     
        mrtransform T1_raw_24.mif -linear t12t1_mrtrix.txt T1_raw_24_coreg.mif -force
      fi      
      
      cp T1_raw_24_coreg.mif "$ANALYSIS/T1_raw_24_coreg.mif"      
      
      # Create maps (24H)
      dwi2tensor dwi_den_unr_preproc_unb_reg.mif -mask "$OUT_PRE/dwi_mask_up_reg.mif" tensor_24.mif -force      
      tensor2metric tensor_24.mif -vec fa_map_24.mif -adc adc_map_24.mif -cl cl_map_24.mif -cs cs_map_24.mif -cp cp_map_24.mif -ad ad_map_24.mif -rd rd_map_24.mif -force
      mrcalc fa_map_24.mif -abs fa_map_24_abs.mif -force
      cp -f fa_map_24_abs.mif adc_map_24.mif cl_map_24.mif cs_map_24.mif cp_map_24.mif ad_map_24.mif rd_map_24.mif "$ANALYSIS"
      cp hcpmmp1.csv "$ANALYSIS/hcpmmp1_24.csv"
      cd "$ANALYSIS"
      if [ ! -d Nifti ] ; then
          mkdir Nifti
      fi
      mrconvert fa_map_24_abs.mif -stride 1,2,3,4 "$ANALYSIS/Nifti/fa_map_24_abs.nii.gz" -force
      mrconvert adc_map_24.mif -stride 1,2,3 "$ANALYSIS/Nifti/adc_map_24.nii.gz" -force
      mrconvert cl_map_24.mif -stride 1,2,3 "$ANALYSIS/Nifti/cl_map_24.nii.gz" -force
      mrconvert cs_map_24.mif -stride 1,2,3 "$ANALYSIS/Nifti/cs_map_24.nii.gz" -force
      mrconvert cp_map_24.mif -stride 1,2,3 "$ANALYSIS/Nifti/cp_map_24.nii.gz" -force
      mrconvert ad_map_24.mif -stride 1,2,3 "$ANALYSIS/Nifti/ad_map_24.nii.gz" -force
      mrconvert rd_map_24.mif -stride 1,2,3 "$ANALYSIS/Nifti/rd_map_24.nii.gz" -force
      mrconvert T1_raw_24_coreg.mif -stride 1,2,3 "$ANALYSIS/Nifti/T1_24_coreg.nii.gz" -force

     
      

