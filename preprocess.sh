  
      #Files
      FILE_1="dwi_den.mif"
      FILE_2="dwi_den_unr.mif"
      FILE_3="dwi_den_unr_preproc.mif"
      FILE_4="dwi_den_unr_preproc_unbiased.mif"
      FILE_5="dwi_mask.mif"
      FILE_6="dwi_den_unr_preproc_unb_reg.mif"
      FLAG=0
      FLAG_CONTINUE=1
      
      # FUNCTIONS

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
          EXIST=1
        else
          EXIST=1
        fi
      }
            
      # 1.Denoising
      handleDenoise() {
        if [ $EXIST -eq 1 ]; then
          mkdir teste
          time dwidenoise ../Raw/dwi_raw.mif dwi_den.mif -noise noise.mif -force
          mrcalc ../Raw/dwi_raw.mif dwi_den.mif -subtract residual.mif -force
        else
          exit
        fi
      }

      # 2.Unring
      handleUnring() {
        if [ $EXIST -eq 1 ]; then
          time mrdegibbs dwi_den.mif dwi_den_unr.mif -axes 0,1 -force
          mrcalc dwi_den.mif dwi_den_unr.mif -subtract residualUnringed.mif -force
        else
          exit
        fi
      }

      # 3.Motion correction
      handleMotion() {
        if [ $EXIST -eq 1 ]; then
          dwiextract dwi_den_unr.mif - -bzero | mrmath - mean mean_b0_AP.mif -axis 3 -force
          #mrconvert ../019/ raw_19.mif -force
          mrmath ../../Output_general/019_raw.mif mean mean_b0_PA.mif -axis 3 -force
          MEAN1=$(mrinfo mean_b0_AP.mif -size)
	      MEAN2=$(mrinfo mean_b0_PA.mif -size)
	  if [ "$MEAN1" != "$MEAN2" ]; then
	    echo "Os arquivos AP e PA possuem um número diferente de cortes, será feito um resample do arquivo AP para que fiquem com o mesmo número de cortes. Isso é necessário para o cálculo da média, confira o arquivo de saída."
		mrgrid mean_b0_AP.mif regrid -template mean_b0_PA.mif mean_b0_AP_resampled.mif -force
		mrcat mean_b0_AP_resampled.mif mean_b0_PA.mif -axis 3 b0_pair.mif -force
        time dwifslpreproc dwi_den_unr.mif dwi_den_unr_preproc.mif -pe_dir AP -rpe_pair -se_epi b0_pair.mif -eddy_options " --slm=linear --data_is_shelled" -force
	  else
	  	mrcat mean_b0_AP.mif mean_b0_PA.mif -axis 3 b0_pair.mif -force
        time dwifslpreproc dwi_den_unr.mif dwi_den_unr_preproc.mif -pe_dir AP -rpe_pair -se_epi b0_pair.mif -eddy_options " --slm=linear --data_is_shelled" -force
	  fi
          
        else
          exit
        fi
      }

      # 4.Bias correction
      handleBias() {
        if [ $EXIST -eq 1 ]; then
          dwibiascorrect ants dwi_den_unr_preproc.mif dwi_den_unr_preproc_unbiased.mif -bias bias.mif -force
        else
          exit
        fi
      }

      # 5.Mask estimation
      handleMask() {
        if [ $EXIST -eq 1 ]; then
          mrconvert dwi_den_unr_preproc_unbiased.mif dwi_unbiased.nii.gz -force
          bet2 dwi_unbiased.nii.gz masked -m -f 0.6
          mrconvert masked_mask.nii.gz dwi_mask.mif -force
        else
          exit
        fi
      }
      
      # 6.Coregister
    handleCoregister() {
      if [ $EXIST -eq 1 ]; then
          #mrgrid dwi_den_unr_preproc_unbiased.mif regrid dwi_den_unr_preproc_unb_up.mif -voxel 1.5 -force
          #mrgrid dwi_mask.mif regrid - -template dwi_den_unr_preproc_unb_up.mif -interp linear -datatype bit | maskfilter - median dwi_mask_up.mif -force
          #5ttgen fsl ../Raw/T1_raw.mif 5tt_coreg.mif -force
          #dwiextract dwi_den_unr_preproc_unb_up.mif - -bzero | mrmath - mean mean_b0_preprocessed.mif -axis 3 -force
          #mrconvert mean_b0_preprocessed.mif mean_b0_preprocessed.nii.gz -force
          bet2 "$OUT_PRE/Preprocess/T1_raw.nii.gz" T1_brain.nii.gz -f 0.4 -m
          epi_reg --epi=mean_b0_preprocessed.nii.gz --t1="$OUT_PRE/Preprocess/T1_raw.nii.gz" --t1brain="$OUT_PRE/Preprocess/T1_brain.nii.gz" --out=dwi2t1_reg
          transformconvert dwi2t1_reg.mat mean_b0_preprocessed.nii.gz "$OUT_PRE/Preprocess/T1_raw.nii.gz" flirt_import matrix_dwi2t1.txt -force
          if [ "$moment" -eq 1 ]; then
            mrtransform dwi_den_unr_preproc_unb_up.mif -linear matrix_dwi2t1.txt dwi_den_unr_preproc_unb_reg.mif -force
            mrtransform dwi_mask_up.mif -linear matrix_dwi2t1.txt dwi_mask_up_reg.mif -force
            mrconvert dwi_mask_up_reg.mif "$OUT_PRE/Segmentation/dwi_mask_up_reg.nii.gz"
          elif [ "$moment" -eq 2 ]; then
            MEAN1=$(mrinfo "$OUT_PRE/Preprocess/dwi_mask_up_reg.mif" -size)
            MEAN2=$(mrinfo "$OUT_24/Preprocess/dwi_den_unr_preproc_unb_up.mif" -size)
	    if [ "$MEAN1" != "$MEAN2" ]; then
	    	echo "Os arquivos dwi_PRE e dwi_24 possuem um número diferente de cortes, será feito um resample do arquivo dwi_24 para que fiquem com o mesmo número de cortes. Isso é necessário para que a comparação entre as duas imagens tenha a mesma referência, confira o arquivo de saída."
		mrtransform dwi_den_unr_preproc_unb_up.mif -linear matrix_dwi2t1.txt dwi_den_unr_preproc_unb_reg_temp.mif -force
		mrtransform dwi_mask_up.mif -linear matrix_dwi2t1.txt dwi_mask_up_reg_24.mif -force
		mrgrid dwi_den_unr_preproc_unb_reg_temp.mif regrid -template "$OUT_PRE/Preprocess/dwi_mask_up_reg.mif" dwi_den_unr_preproc_unb_reg.mif -force
            else     
            	mrtransform dwi_den_unr_preproc_unb_up.mif -linear matrix_dwi2t1.txt dwi_den_unr_preproc_unb_reg.mif -force
            	mrtransform dwi_mask_up.mif -linear matrix_dwi2t1.txt dwi_mask_up_reg_24.mif -force
            fi
          fi           
      else
        exit
      fi
    }

      # MAIN FUNCTION
      # Asks the user if they want to perform all the preprocessing or just one of the steps
      while true; do
	cd "Preprocess/"
        read -p "Would you like to do all the preprocessing? (y/n):  " yn

        case $yn in
          # Complete preprocessing
          [Yy])
          for file in $FILE_1 $FILE_2 $FILE_3 $FILE_4 $FILE_5 $FILE_6; do
            FILE=$file
            fileExistence
          done
          
          if [ $FLAG -eq 1 ]; then
            echo "Pelo menos um dos arquivos de saída já existe, o processo irá convertê-los."
            FLAG=0
          fi
          
          if [ $FLAG -eq 0 ]; then
            read -p "Confirma o pré processamento completo? (y/n): " confirm
            case $confirm in
            
            [Yy])
            handleDenoise
            handleUnring
            handleMotion
            handleBias
            handleMask
            handleCoregister;;
            
            [Nn])
            exit;;
            
            esac
          fi
          
          break;;
          
          # One step of the preprocessing
          [Nn])
          while [ $FLAG_CONTINUE -eq 1 ]; do
            echo "Deseja realizar qual das etapas?"\
            $'\n'"1.Denoising"\
            $'\n'"2.Unringing"\
            $'\n'"3.Motion correction"\
            $'\n'"4.Bias correction"\
            $'\n'"5.Brain mask"\
            $'\n'"6.Coregister"
            read -p "Opção: " step
              case $step in
              1)
              FILE=$FILE_1
              fileExistence
              handleDenoise;;
            
              2)
              FILE=$FILE_2
              fileExistence
              handleUnring;;
            
              3)
              FILE=$FILE_3
              fileExistence
              handleMotion;;
            
              4)
              FILE=$FILE_4
              fileExistence
              handleBias;;
            
              5)
              FILE=$FILE_5
              fileExistence
              handleMask;;
            
              6)
              FILE=$FILE_6
              fileExistence
              handleCoregister;;
                        
              *)
              echo invalid response;;
              esac
              
              read -p "Deseja realizar outra etapa do pré-processamento (y/n)? " option
          
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
      done



  
