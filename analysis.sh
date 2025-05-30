    ANALYSIS_DIR="$PAT_DIR/Analysis"
    FILE_1="$ANALYSIS_DIR/fa_map_abs.mif"
    FILE_2="$ANALYSIS_DIR/Nifti/fa_map_abs.mif"
    FILE_3="$ANALYSIS_DIR/Nifti/teste.nii.gz"
    FLAG=0
    FLAG_CONTINUE=1
    
    
    # Existing file (Check if the output file already exists and, if it does, if the user wants to convert it)
      fileExistence() {
        if [[ -a $FILE && $yn == [Nn] ]]; then
          read -p "o arquivo $FILE já existe, deseja convertê-lo? (y/n):  " file
          case $file in
            [Yy]) EXIST=1;;
            [Nn]) EXIST=0;;
            * )   echo invalid response; exit;;
          esac
        elif [[ -a $FILE && $yn == [Yy] ]]; then
          FLAG=1
        else
          EXIST=1
        fi
      }
    
    #Functions
    handleMapscreation() {
        if [ $EXIST -eq 1 ]; then
          # Create maps (PRE)
          cd "$OUT_PRE"
          mrconvert "$SUBJECTS_DIR/$PAT_NUM/mri/T1.mgz" "$OUT_PRE/T1_resampled.mif" -force
          mrgrid dwi_den_unr_preproc_unb_reg.mif regrid -template "$OUT_PRE/T1_resampled.mif" -strides -1,3,-2,4 dwi_den_unr_preproc_unb_reg_resampled.mif -force
          mrgrid dwi_mask_up_reg.mif regrid -template "$OUT_PRE/T1_resampled.mif" -strides -1,3,-2 dwi_mask_resampled.mif -force
          dwi2tensor dwi_den_unr_preproc_unb_reg_resampled.mif -mask "$OUT_PRE/dwi_mask_resampled.mif" tensor.mif -force
          tensor2metric tensor.mif -vec fa_map.mif -adc adc_map.mif -cl cl_map.mif -cs cs_map.mif -cp cp_map.mif -ad ad_map.mif -rd rd_map.mif -force
          mrcalc fa_map.mif -abs fa_map_abs.mif -force
          cp -f fa_map_abs.mif adc_map.mif cl_map.mif cs_map.mif cp_map.mif ad_map.mif rd_map.mif "$ANALYSIS_DIR"
          cp Julich_parcels_mrtrix.mif "$ANALYSIS_DIR/Julich_parcels_mrtrix.mif"
          cp dwi_mask_up_reg.mif "$ANALYSIS_DIR/dwi_mask_up_reg.mif"
          
          # Create maps (24H)
          cd "$OUT_24"
          mrgrid dwi_den_unr_preproc_unb_reg.mif regrid -template "$OUT_PRE/T1_resampled.mif" -strides -1,3,-2,4 dwi_den_unr_preproc_unb_reg_resampled.mif -force
          dwi2tensor dwi_den_unr_preproc_unb_reg_resampled.mif -mask "$OUT_PRE/dwi_mask_resampled.mif" tensor_24.mif -force      
          tensor2metric tensor_24.mif -vec fa_map_24.mif -adc adc_map_24.mif -cl cl_map_24.mif -cs cs_map_24.mif -cp cp_map_24.mif -ad ad_map_24.mif -rd rd_map_24.mif -force
          mrcalc fa_map_24.mif -abs fa_map_24_abs.mif -force
          cp -f fa_map_24_abs.mif adc_map_24.mif cl_map_24.mif cs_map_24.mif cp_map_24.mif ad_map_24.mif rd_map_24.mif "$ANALYSIS_DIR"
        else
          exit
        fi
      }
      
    handleNifti() {
        if [ $EXIST -eq 1 ]; then
          cd "$ANALYSIS_DIR"
          if [ ! -d "$ANALYSIS_DIR/Nifti" ] ; then
              mkdir Nifti
          fi
          # Convert the T1 image from freesurfer to mif
          mrconvert "$OUT_PRE/T1_resampled.mif" -stride -1,3,-2 "$ANALYSIS_DIR/Nifti/T1_resampled.nii.gz" -force
                    
          # Conversion (PRE)
          cd "$OUT_PRE"
          cp Julich.csv "$ANALYSIS_DIR/Nifti/Julich.csv"
          mrconvert fa_map_abs.mif -stride -1,3,-2,4 "$ANALYSIS_DIR/Nifti/fa_map_abs.nii.gz" -force
          mrconvert adc_map.mif -stride -1,3,-2 "$ANALYSIS_DIR/Nifti/adc_map.nii.gz" -force
          mrconvert cl_map.mif -stride -1,3,-2 "$ANALYSIS_DIR/Nifti/cl_map.nii.gz" -force
          mrconvert cs_map.mif -stride -1,3,-2 "$ANALYSIS_DIR/Nifti/cs_map.nii.gz" -force
          mrconvert cp_map.mif -stride -1,3,-2 "$ANALYSIS_DIR/Nifti/cp_map.nii.gz" -force
          mrconvert ad_map.mif -stride -1,3,-2 "$ANALYSIS_DIR/Nifti/ad_map.nii.gz" -force
          mrconvert rd_map.mif -stride -1,3,-2 "$ANALYSIS_DIR/Nifti/rd_map.nii.gz" -force
          #mrconvert T1_raw.mif -stride -1,3,-2 "$ANALYSIS_DIR/Nifti/T1.nii.gz" -force
          mrconvert Julich_parcels_mrtrix.mif -stride -1,3,-2 "$ANALYSIS_DIR/Nifti/Julich_parcels_mrtrix.nii.gz" -force
          mrconvert "$OUT_PRE/dwi_mask_resampled.mif" -stride -1,3,-2 "$ANALYSIS_DIR/Nifti/dwi_mask_resampled.nii.gz" -force   
          
          # Coregister and resample Contrast with T1's freesurfer
          mrconvert Contrast.mif Contrast.nii.gz -force
          flirt -in Contrast.nii.gz -ref "$ANALYSIS_DIR/Nifti/T1_resampled.nii.gz" -dof 6 -omat contrast2t1.mat
          transformconvert contrast2t1.mat Contrast.nii.gz "$ANALYSIS_DIR/Nifti/T1_resampled.nii.gz" flirt_import contrast2t1_mrtrix.txt -force
          mrtransform Contrast.mif -linear contrast2t1_mrtrix.txt Contrast_coreg.mif -force
          mrgrid Contrast_coreg.mif regrid -template "$OUT_PRE/T1_resampled.mif" Contrast_coreg_resampled.mif -force
          mrconvert Contrast_coreg_resampled.mif -stride -1,3,-2 "$ANALYSIS_DIR/Nifti/Contrast_coreg_resampled.nii.gz" -force          
          
          cd "$OUT_24"
                    
          # Coregister T1_raw_24 with T1_raw
          #mrconvert T1_raw_24.mif T1_raw_24.nii.gz -force
          #flirt -in T1_raw_24.nii.gz -ref T1_raw.nii.gz -dof 6 -omat t12t1.mat
          #transformconvert t12t1.mat T1_raw_24.nii.gz T1_raw.nii.gz flirt_import t12t1_mrtrix.txt -force
      
          #MEAN1=$(mrinfo "$OUT_24/T1_raw_24" -size)
          #MEAN2=$(mrinfo "$OUT_PRE/T1_raw.mif" -size)
          #if [ "$MEAN1" != "$MEAN2" ]; then
            #echo "Os arquivos T1_raw_24 e T1_raw possuem um número diferente de cortes, será feito um resample do arquivo T1_raw_24 para que fiquem com o mesmo número de cortes. Isso é necessário para que a comparação entre as duas imagens tenha a mesma referência, confira o arquivo de saída."
            #mrtransform T1_raw_24.mif -linear t12t1_mrtrix.txt T1_raw_24_coreg_temp.mif -force
            #mrgrid T1_raw_24_coreg_temp.mif regrid -template "$OUT_PRE/T1_raw.mif" T1_raw_24_coreg.mif -force
          #else     
            #mrtransform T1_raw_24.mif -linear t12t1_mrtrix.txt T1_raw_24_coreg.mif -force
          #fi
          
          # Conversion (24H)    
          #cp T1_raw_24_coreg.mif "$ANALYSIS_DIR/T1_raw_24_coreg.mif"
          cp Julich.csv "$ANALYSIS_DIR/Nifti/Julich_24.csv" 
          mrconvert fa_map_24_abs.mif -stride -1,3,-2,4 "$ANALYSIS_DIR/Nifti/fa_map_24_abs.nii.gz" -force
          mrconvert adc_map_24.mif -stride -1,3,-2 "$ANALYSIS_DIR/Nifti/adc_map_24.nii.gz" -force
          mrconvert cl_map_24.mif -stride -1,3,-2 "$ANALYSIS_DIR/Nifti/cl_map_24.nii.gz" -force
          mrconvert cs_map_24.mif -stride -1,3,-2 "$ANALYSIS_DIR/Nifti/cs_map_24.nii.gz" -force
          mrconvert cp_map_24.mif -stride -1,3,-2 "$ANALYSIS_DIR/Nifti/cp_map_24.nii.gz" -force
          mrconvert ad_map_24.mif -stride -1,3,-2 "$ANALYSIS_DIR/Nifti/ad_map_24.nii.gz" -force
          mrconvert rd_map_24.mif -stride -1,3,-2 "$ANALYSIS_DIR/Nifti/rd_map_24.nii.gz" -force
          #mrconvert T1_raw_24_coreg.mif -stride -1,3,-2 "$ANALYSIS_DIR/Nifti/T1_24_coreg.nii.gz" -force
          
          # Coregister and resample Contrast_24 with T1's freesurfer
          mrconvert Contrast.mif Contrast.nii.gz -force
          flirt -in Contrast.nii.gz -ref "$ANALYSIS_DIR/Nifti/T1_resampled.nii.gz" -dof 6 -omat contrast2t1.mat
          transformconvert contrast2t1.mat Contrast.nii.gz "$ANALYSIS_DIR/Nifti/T1_resampled.nii.gz" flirt_import contrast2t1_mrtrix.txt -force
          mrtransform Contrast.mif -linear contrast2t1_mrtrix.txt Contrast_coreg.mif -force
          mrgrid Contrast_coreg.mif regrid -template "$OUT_PRE/T1_resampled.mif" Contrast_coreg_resampled.mif -force
          mrconvert Contrast_coreg_resampled.mif -stride -1,3,-2 "$ANALYSIS_DIR/Nifti/Contrast_24_coreg_resampled.nii.gz" -force
        else
          exit
        fi
      }
      
    handleScript() {
        if [ $EXIST -eq 1 ]; then
          cd "$ANALYSIS_DIR"
          if [ ! -d "$ANALYSIS_DIR/Results" ] ; then
              mkdir Results
          fi
          cd "$ANALYSIS_DIR/Nifti"
          python "$SCRIPT_DIR/Python/main_analysis.py"
          cd "$ANALYSIS_DIR/Results"
          mrcat FAmap_Red\(PRE\).nii.gz FAmap_Green\(PRE\).nii.gz FAmap_Blue\(PRE\).nii.gz FAmap\(PRE\).nii.gz -force
          mrcat FAmap_Red\(Subtraction\).nii.gz FAmap_Green\(Subtraction\).nii.gz FAmap_Blue\(Subtraction\).nii.gz FAmap\(Subtraction\).nii.gz -force
          mrcat FAmap_Red\(24H\).nii.gz FAmap_Green\(24H\).nii.gz FAmap_Blue\(24H\).nii.gz FAmap\(24H\).nii.gz -force  
          rm FAmap_Red\(PRE\).nii.gz FAmap_Green\(PRE\).nii.gz FAmap_Blue\(PRE\).nii.gz
          rm FAmap_Red\(24H\).nii.gz FAmap_Green\(24H\).nii.gz FAmap_Blue\(24H\).nii.gz
          rm FAmap_Red\(Subtraction\).nii.gz FAmap_Green\(Subtraction\).nii.gz FAmap_Blue\(Subtraction\).nii.gz
        else
          exit
        fi
      } 
      
    # MAIN FUNCTION
      # Create analysis folder
      cd "$PAT_DIR"
      
      if [ ! -d "$ANALISIS_DIR" ]; then
	mkdir -p Analysis
      fi
      
      cd "$ANALYSIS_DIR"     
      
      echo "$PAT_NUM"
      read -p "Would you like to do all the analysis? (y/n):  " yn

      case $yn in
        # Complete analysis
        [Yy])
        for file in $FILE_1 $FILE_2 $FILE_3 $FILE_4; do
          FILE=$file
          fileExistence
        done
      
      if [ $FLAG -eq 1 ]; then
        echo "Pelo menos um dos arquivos de saída já existe, o processo irá convertê-los."
        FLAG=0
      fi
      
      if [ $FLAG -eq 0 ]; then
        read -p "Confirma a análise completa? (y/n): " confirm
        case $confirm in
        
        [Yy])
        handleMapscreation
        handleNifti
        handleScript;;
        
        [Nn])
        exit;;
        
        esac
      fi
      
      ;;
      
        # One step of the preprocessing
      [Nn])
      while [ $FLAG_CONTINUE -eq 1 ]; do   
        echo "Deseja realizar qual das etapas?"\
        $'\n'"1.Create maps"\
        $'\n'"2.Create nifti files"\
        $'\n'"3.Run python script"
        read -p "Opção: " step
        
          case $step in
          1)
          FILE=$FILE_1
          fileExistence
          handleMapscreation;;
        
          2)
          FILE=$FILE_2
          fileExistence
          handleNifti;;
        
          3)
          FILE=$FILE_3
          fileExistence
          handleScript;;
        
          *)
          echo invalid response;;
          esac
          
          read -p "Deseja realizar outra etapa da análise (y/n)? " option
          
          case $option in 
          [Yy]) FLAG_CONTINUE=1;;
          [nN]) FLAG_CONTINUE=0;;
          *)  FLAG_CONTINUE=0;;
          esac
      done
      exit;;
      
      * )
      echo invalid response
      ;;
    esac    
    

        
