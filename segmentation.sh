    SUBJECTS_DIR="$BASE_DIR/fs_subjects"
    HISTO_DIR="$SUBJECTS_DIR/$PAT_NUM/next_brain_segmentation"
    ATLAS_DIR="$BASE_DIR/Atlas" 
    FILE_1="$SUBJECTS_DIR/$PAT_NUM/scripts/recon-all.done"
    FILE_2="$SUBJECTS_DIR/$PAT_NUM/label/rh.hcpmmp1.annot"
    FILE_3="hcpmmp1_parcels.mif"
    FILE_4="hcpmmp1.csv"
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
    handleReconstruction() {
        if [ $EXIST -eq 1 ]; then
                             
          # Coregister T2_raw with T1_raw
          #flirt -in "$OUT_PRE/Preprocess/T2_raw.nii.gz" -ref "$OUT_PRE/Segmentation/T1_raw.nii.gz" -dof 6 -omat t22t1.mat
          #transformconvert t22t1.mat "$OUT_PRE/Preprocess/T2_raw.nii.gz" "$OUT_PRE/Segmentation/T1_raw.nii.gz" flirt_import t22t1_mrtrix.txt -force
          #mrtransform "$OUT_PRE/Raw/T2_raw.mif" -linear t22t1_mrtrix.txt T2_raw_coreg.mif -force
          #mrconvert T2_raw_coreg.mif T2_raw_coreg.nii.gz -force
          
          # Coregister T2_raw_24 with T1_raw
          #mrgrid "$OUT_24/Segmentation/T2_raw.nii.gz" regrid -template T1_raw.nii.gz T2_raw_24_T1.nii.gz -force
          #flirt -in T2_raw_24_T1.nii.gz -ref "$OUT_PRE/Segmentation/T1_raw.nii.gz" -dof 6 -omat t22t1_24.mat
          #transformconvert t22t1_24.mat T2_raw_24_T1.nii.gz "$OUT_PRE/Segmentation/T1_raw.nii.gz" flirt_import t22t1_24_mrtrix.txt -force
          #mrtransform "$OUT_24/Raw/T2_raw.mif" -linear t22t1_24_mrtrix.txt T2_raw_24_coreg.mif -force
          #mrconvert T2_raw_24_coreg.mif T2_raw_24_coreg.nii.gz -force
          #rm T2_raw_24_T1.nii.gz
          
          # Coregister Contrast_raw with T1_raw
          mrgrid Contrast_raw.nii.gz regrid -template T1_raw.nii.gz Contrast_raw_T1.nii.gz -force
          flirt -in Contrast_raw_T1.nii.gz -ref "$OUT_PRE/Segmentation/T1_raw.nii.gz" -dof 6 -omat Contrast2t1.mat
          transformconvert Contrast2t1.mat Contrast_raw_T1.nii.gz "$OUT_PRE/Segmentation/T1_raw.nii.gz" flirt_import Contrast2t1_mrtrix.txt -force
          mrtransform "$OUT_PRE/Raw/Contrast_raw.mif" -linear Contrast2t1_mrtrix.txt Contrast_raw_coreg.mif -force
          mrconvert Contrast_raw_coreg.mif -stride -1,-2,3 Contrast_raw_coreg.nii.gz -force
          rm Contrast_raw_T1.nii.gz
          
          # Coregister Contrast_raw_24 with T1_raw
          mrgrid "$OUT_24/Segmentation/Contrast_raw.nii.gz" regrid -template T1_raw.nii.gz Contrast_raw_24_T1.nii.gz -force
          flirt -in Contrast_raw_24_T1.nii.gz -ref "$OUT_PRE/Segmentation/T1_raw.nii.gz" -dof 6 -omat Contrast2t1_24.mat
          transformconvert Contrast2t1_24.mat Contrast_raw_24_T1.nii.gz "$OUT_PRE/Segmentation/T1_raw.nii.gz" flirt_import Contrast2t1_24_mrtrix.txt -force
          mrtransform "$OUT_24/Raw/Contrast_raw.mif" -linear Contrast2t1_24_mrtrix.txt Contrast_raw_coreg_24.mif -force
          mrconvert Contrast_raw_coreg_24.mif -stride -1,-2,3 Contrast_raw_coreg_24.nii.gz -force      
          rm Contrast_raw_24_T1.nii.gz
          
          mrgrid Contrast_raw_coreg.nii.gz regrid -template Contrast_raw_coreg_24.nii.gz Contrast_raw_coreg_resampled.nii.gz -force
                   
          # Reconstruction
          #recon-all -s "$PAT_NUM" -i "$OUT_PRE/Preprocess/T1_raw.nii.gz" -T2 T2_raw_coreg.nii.gz -all
          #mrconvert "$SUBJECTS_DIR/$PAT_NUM/mri/T1.mgz" "$OUT_PRE/Segmentation/T1_resampled.mif" -force
          #mrconvert T1_resampled.mif -stride -1,-2,3 T1_resampled.nii.gz -force
        else
          exit
        fi
      }
      
    handleHistoSegmentation() {
        if [ $EXIST -eq 1 ]; then
          #mrconvert "$OUT_PRE/Raw/Contrast_raw.mif" Contrast.nii.gz -force
          #flirt -in Contrast.nii.gz -ref T1_resampled.nii.gz -dof 6 -omat contrast2t1.mat
          #transformconvert contrast2t1.mat Contrast.nii.gz T1_resampled.nii.gz flirt_import contrast2t1_mrtrix.txt -force
          #mrtransform "$OUT_PRE/Raw/Contrast_raw.mif" -linear contrast2t1_mrtrix.txt Contrast_coreg.mif -force
          #mrgrid Contrast_coreg.mif regrid -template T1_resampled.mif Contrast_coreg_resampled.mif -force
          #mrconvert Contrast_coreg_resampled.mif Contrast_coreg_resampled.nii.gz -force          
          
          export FREESURFER_HOME=/usr/local/freesurfer_dev/7-dev # Versão dev do freesurfer
          source $FREESURFER_HOME/SetUpFreeSurfer.sh
          
          #mri_histo_atlas_segment_fast "$OUT_PRE/Contrast_coreg_resampled.nii.gz" "$HISTO_DIR" 0 -1
          #mri_histo_atlas_segment_fast T2_raw_coreg.nii.gz "$HISTO_DIR" 0 -1
          
          export FREESURFER_HOME=/usr/local/freesurfer/7.4.1  #versão padrão do freesurfer
    	  source $FREESURFER_HOME/SetUpFreeSurfer.sh
                       
          # Upsample da imagem T1 para usar como template (a imagem resultante da segmentação tem voxels de aproxidamente 0.4 mm, mas os dois hemisférios tem resoluções diferentes) 
	  #mrgrid T1_resampled.nii.gz regrid -voxel 0.4 T1_upsampled.nii.gz -force
	  mrgrid "$HISTO_DIR/seg_left.nii.gz" regrid -template T1_upsampled.nii.gz -interp nearest -oversample 1,1,1 seg_left_resampled.nii.gz -force
	  mrgrid "$HISTO_DIR/seg_right.nii.gz" regrid -interp nearest -template T1_upsampled.nii.gz -oversample 1,1,1 seg_right_resampled.nii.gz -force
	  mrgrid "$HISTO_DIR/SynthSeg.mgz" regrid -interp nearest -template T1_upsampled.nii.gz -oversample 1,1,1 SynthSeg_resampled.nii.gz -force
	  
	  #flirt -in "$HISTO_DIR/seg_left.nii.gz" -ref T2_raw_coreg_upsampled.nii.gz -applyxfm -init identity.mat -out seg_left_resampled.nii.gz -interp nearestneighbour
	  #flirt -in "$HISTO_DIR/seg_right.nii.gz" -ref T2_raw_coreg_upsampled.nii.gz -applyxfm -init t22t1.mat -out seg_right_resampled.nii.gz -interp nearestneighbour

    	  	  
        else
          exit
        fi
      }
      
    handleLabel2Image() {
        if [ $EXIST -eq 1 ]; then
          #mri_surf2surf --srcsubject fsaverage --trgsubject "$PAT_NUM" --hemi lh --sval-annot "$SUBJECTS_DIR/fsaverage/label/lh.Julich.annot"  --tval "$SUBJECTS_DIR/"$PAT_NUM"/label/lh.JULICH.annot"  
	  #mri_surf2surf --srcsubject fsaverage --trgsubject "$PAT_NUM" --hemi rh --sval-annot "$SUBJECTS_DIR/fsaverage/label/rh.Julich.annot"  --tval "$SUBJECTS_DIR/"$PAT_NUM"/label/rh.JULICH.annot" 
	  #mri_aparc2aseg --new-ribbon --s "$PAT_NUM" --annot JULICH --o output_freesurfer.mgz
	  
          #mrconvert output_freesurfer.mgz output_freesurfer.nii.gz -force
          mrcalc "$HISTO_DIR/seg_left.nii.gz" 314 -eq ROI_rostral_lh.mif -datatype bit -force
          mrgrid ROI_rostral_lh.mif regrid -template Contrast_raw_coreg_24.nii.gz -datatype uint8 -oversample 1,1,1 ROI_rostral_lh_Contrast.nii.gz -force
          python "$SCRIPT_DIR/Python/main_segmentation.py"
          #mrconvert -datatype uint32 Julich_parcels_freesurfer.nii.gz Julich_parcels_freesurfer.mif -force
          #labelconvert Julich_parcels_freesurfer.mif "$ATLAS_DIR/JulichLUT_complete.txt" "$ATLAS_DIR/JulichLUT_mrtrix.txt" Julich_parcels_mrtrix.mif -force
          #label2colour Julich_parcels_mrtrix.mif -lut "$ATLAS_DIR/JulichLUT_mrtrix.txt" Julich_parcels_mrtrix_colored.mif -force
        else
          exit
        fi
      } 
      
    handleTck2Connectome() {
        if [ $EXIST -eq 1 ]; then
          echo "Pat_PRE"
          tck2connectome -symmetric -zero_diagonal -scale_invnodevol -tck_weights_in sift_weights.txt tracks_10mio.tck "$OUT_PRE/Julich_parcels_mrtrix.mif" Julich.csv -out_assignment assignments_Julich.csv -force
          if [ -a "$OUT_24/sift_weights.txt" ]; then
            echo "Pat_24"
            cd "$OUT_24"
            tck2connectome -symmetric -zero_diagonal -scale_invnodevol -tck_weights_in sift_weights.txt tracks_10mio.tck "$OUT_PRE/Julich_parcels_mrtrix.mif" Julich.csv -out_assignment assignments_Julich.csv -force
          fi
        else
          exit
        fi
      }       
   
    
    # MAIN FUNCTION
    # Definition of the fs_subjects folder
    export FREESURFER_HOME="/usr/local/freesurfer/7.4.1"
    export SUBJECTS_DIR="$SUBJECTS_DIR"
    source "$FREESURFER_HOME/SetUpFreeSurfer.sh"
    
    cd "$OUT_PRE/Segmentation"
    
    if [ -d "$SUBJECTS_DIR" ]; then
        echo "Pasta fs_subjects atual: $SUBJECTS_DIR"
        read -p "Confirma o uso dessa pasta?(y/n) " FOLDER
        
        case $FOLDER in
            [Yy])
            echo "Endereço da pasta fs_subjects: $SUBJECTS_DIR";;

            [Nn])
            read -p "Digite o endereço completo da pasta fs_subjects: " NEW_FOLDER
                     
            if [ -d "$NEW_FOLDER" ]; then
                SUBJECTS_DIR=$NEW_FOLDER
                echo "Endereço da Pasta fs_subjects: $SUBJECTS_DIR"
            else
                echo "Pasta inválida, abra o programa novamente ou mude a pasta fs_subjects no script"
                exit
            fi;;
        esac
    else
        echo "A pasta fs_subjects registrada no script é inválida"
        read -p "Digit o endereço completo da pasta fs_subjects: " NEW_FOLDER
        if [ -d "$NEW_FOLDER" ]; then
                SUBJECTS_DIR=$NEW_FOLDER
                echo "Endereço da Pasta fs_subjects: $SUBJECTS_DIR"
            else
                echo "Pasta inválida, abra o programa novamente ou mude a pasta fs_subjects no script"
                exit
        fi
    fi
    
    echo "$PAT_NUM"
    read -p "Would you like to do all the segmentation process? (y/n):  " yn

    case $yn in
      # Complete preprocessing
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
        read -p "Confirma o pré processamento completo? (y/n): " confirm
        case $confirm in
        
        [Yy])
        handleReconstruction
        handleHistoSegmentation
        handleLabel2Image;;
        # handleTck2Connectome;;
        
        [Nn])
        exit;;
        
        esac
      fi
      
      break;;
      
        # One step of the preprocessing
      [Nn])
      while [ $FLAG_CONTINUE -eq 1 ]; do   
        echo "Deseja realizar qual das etapas?"\
        $'\n'"1.Reconstruction"\
        $'\n'"2.Subcortical segmentation"\
        $'\n'"3.Cortical segmentation"
        #$'\n'"4.Connectivity matrix (tck2connectome)"
        read -p "Opção: " step
        
          case $step in
          1)
          FILE=$FILE_1
          fileExistence
          handleReconstruction;;
        
          2)
          FILE=$FILE_2
          fileExistence
          handleHistoSegmentation;;
        
          3)
          FILE=$FILE_3
          fileExistence
          handleLabel2Image;;
        
          #4)
          #FILE=$FILE_4
          #fileExistence
          #handleTck2Connectome;;
        
          *)
          echo invalid response;;
          esac
          
          read -p "Deseja realizar outra etapa da segmentação (y/n)? " option
          
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
    

        
