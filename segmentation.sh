    SUBJECTS_DIR="$BASE_DIR/fs_subjects"
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
          flirt -in "$OUT_PRE/T2_raw.nii.gz" -ref "$OUT_PRE/T1_raw.nii.gz" -dof 6 -omat t22t1.mat
          transformconvert t22t1.mat T2_raw.nii.gz T1_raw.nii.gz flirt_import t22t1_mrtrix.txt -force
          mrtransform T2_raw.mif -linear t22t1_mrtrix.txt T2_raw_coreg.mif -force
          mrconvert T2_raw_coreg.mif T2_raw_coreg.nii.gz -force
          # Reconstruction
          recon-all -s "$PAT_NUM" -i "$OUT_PRE/T1_raw.nii.gz" -T2 "$OUT_PRE/T2_raw_coreg.nii.gz" -all
        else
          exit
        fi
      }
      
    handleAnnot2Patient() {
        if [ $EXIST -eq 1 ]; then
          mri_surf2surf --srcsubject fsaverage --trgsubject "$PAT_NUM" --hemi lh --sval-annot $SUBJECTS_DIR/fsaverage/label/lh.Julich.annot  --tval $SUBJECTS_DIR/"$PAT_NUM"/label/lh.JULICH.annot  
	  mri_surf2surf --srcsubject fsaverage --trgsubject "$PAT_NUM" --hemi rh --sval-annot $SUBJECTS_DIR/fsaverage/label/rh.Julich.annot  --tval $SUBJECTS_DIR/"$PAT_NUM"/label/rh.JULICH.annot  
        else
          exit
        fi
      }
      
    handleLabel2Image() {
        if [ $EXIST -eq 1 ]; then
          mri_aparc2aseg --new-ribbon --s "$PAT_NUM" --annot JULICH --o output_freesurfer.mgz
          mrconvert -datatype uint32 output_freesurfer.mgz Julich_parcels.mif -force
          #labelconvert Julich_parcels.mif "$BASE_DIR/Atlas/JulichLUT_freesurfer.txt" "$BASE_DIR/Atlas/JulichLUT_mrtrix.txt" Julich_parcels_ordered.mif -force
        else
          exit
        fi
      } 
      
    handleTck2Connectome() {
        if [ $EXIST -eq 1 ]; then
          echo "Pat_PRE"
          tck2connectome -symmetric -zero_diagonal -scale_invnodevol -tck_weights_in sift_weights.txt tracks_10mio.tck "$OUT_PRE/Julich_parcels_ordered.mif" Julich.csv -out_assignment assignments_Julich.csv -force
          if [ -a "$OUT_24/sift_weights.txt" ]; then
            cp Julich_parcels.mif "$OUT_24"
            echo "Pat_24"
            cd "$OUT_24"
            tck2connectome -symmetric -zero_diagonal -scale_invnodevol -tck_weights_in sift_weights.txt tracks_10mio.tck "$OUT_PRE/Julich_parcels_ordered.mif" Julich.csv -out_assignment assignments_Julich.csv -force
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
    
    cd "$OUT_PRE"
    
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
        handleAnnot2Patient
        handleLabel2Image
        handleTck2Connectome;;
        
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
        $'\n'"2.Create annotation file"\
        $'\n'"3.Labeling"\
        $'\n'"4.Connectivity matrix"
        read -p "Opção: " step
        
          case $step in
          1)
          FILE=$FILE_1
          fileExistence
          handleReconstruction;;
        
          2)
          FILE=$FILE_2
          fileExistence
          handleAnnot2Patient;;
        
          3)
          FILE=$FILE_3
          fileExistence
          handleLabel2Image;;
        
          4)
          FILE=$FILE_4
          fileExistence
          handleTck2Connectome;;
        
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
    

        
