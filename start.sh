#!/bin/bash
    
    BASE_DIR="/home/brunobastos/Mestrado/Dados/"
    SCRIPT_DIR="/home/brunobastos/Mestrado/Scripts/"
    FREESURFER_HOME_DEV="/home/brunobastos/Software/freesurfer-dev/"
    FREESURFER_HOME_STAND="/home/brunobastos/Software/freesurfer-7.4.1/"
    N_THREADS=20
    SUBJECTS_DIR="$BASE_DIR/fs_subjects"
    ATLAS_DIR="$BASE_DIR/Atlas" 
    ACPC_DIR="$BASE_DIR/acpc"

    # Files 
    FILE_1="rename_data.sh"
    FILE_2="start.sh"
    FILE_3="preprocess.sh"
    FILE_4="segmentation.sh"
    FILE_5="tract.sh"
    FILE_6="view.sh"
    FLAG_SCRIPT=6

          
    # Verification of the scripts folder
    cd "$SCRIPT_DIR"
    for file in $FILE_1 $FILE_2 $FILE_3 $FILE_4 $FILE_5 $FILE_6; do
	  FILE=$file
	  if [[ -a $FILE ]]; then
	    FLAG_SCRIPT=$(($FLAG_SCRIPT-1))
	  fi       
    done  
    
    if [ $FLAG_SCRIPT -ne 0 ]; then
        echo "Please check the scripts directory. The folder currently configured is missing $FLAG_SCRIPT .sh files."
        exit
    fi
    
    # Definition of the databases folder
    if [ -d "$BASE_DIR" ]; then
        echo "Current data directory: $BASE_DIR"
        read -p "Can you confirm that this directory is the one that should be used?(y/n) " BASE
        
        case $BASE in
            # Complete preprocessing
            [Yy])
            echo "Data's directory location: $BASE_DIR";;

            [Nn])
            read -p "Enter the full path to the data directory: " NEW_BASE
                     
            if [ -d "$NEW_BASE" ]; then
                BASE_DIR=$NEW_BASE
                echo "Data's directory location: $BASE_DIR"
            else
                echo "Invalid directory. Please restart the program or change the base directory in the script."
                exit
            fi;;
            
            *) echo "Invalid option. Please restart the script."
               exit;;
        esac
    else
        echo "The data directory specified in the script is invalid."
        read -p "Enter the full path to the data directory:" NEW_BASE
        if [ -d "$NEW_BASE" ]; then
                BASE_DIR=$NEW_BASE
                echo "Data's directory location: $BASE_DIR"
            else
                echo "Invalid directory. Please restart the script and change the base directory."
                exit
        fi
    fi
    
      # Change to base directory
      cd $BASE_DIR
      
      # Create a folder for each patient and move Pat_24H and PAT_PRE to this folder
      for dir in "$BASE_DIR"/*/; do 
        FOLDER_NAME=$(basename "$dir")    
        if [[ "$FOLDER_NAME" =~ ^Pat[0-9]+_PRE$ ]]; then
            PAT_NUM=$(echo "$FOLDER_NAME" | sed -E 's/^(Pat[0-9]+)_.*$/\1/')
            mkdir -p "$PAT_NUM"
            mv "$BASE_DIR/$PAT_NUM""_PRE" "$BASE_DIR/$PAT_NUM/"
            mv "$BASE_DIR/$PAT_NUM""_24H" "$BASE_DIR/$PAT_NUM/"
        fi
      done

      # Define the patient
      read -p "Do you want to do the analysis of which patient? " pat
      PAT_DIR="${BASE_DIR}/Pat${pat}"
      PAT_DIR_PRE="${PAT_DIR}/Pat${pat}_PRE"
      PAT_DIR_24="${PAT_DIR}/Pat${pat}_24H"
      OUT_PRE="${PAT_DIR_PRE}/Output_tract"
      OUT_24="${PAT_DIR_24}/Output_tract"
      PAT_NUM="Pat$pat"
      
      # raw_files
      FILE_RAW_1="$OUT_PRE/Raw/T1_raw.mif"
      FILE_RAW_2="$OUT_PRE/Raw/T2_raw.mif"
      FILE_RAW_3="$OUT_PRE/Raw/Contrast_raw.mif"
      FILE_RAW_4="$OUT_PRE/Raw/dwi_raw.mif"
      FILE_RAW_5="$OUT_PRE/Raw/dwi_PA_raw.mif"
      FILE_RAW_6="$OUT_24/Raw/T1_raw.mif"
      FILE_RAW_7="$OUT_24/Raw/T2_raw.mif"
      FILE_RAW_8="$OUT_24/Raw/Contrast_raw.mif"
      FILE_RAW_9="$OUT_24/Raw/dwi_raw.mif"
      FILE_RAW_10="$OUT_24/Raw/dwi_PA_raw.mif"
      FLAG_RAW=10
      
      if [[ ! -d "$PAT_DIR_PRE" && ! -d "$PAT_DIR_24" ]]; then
        echo "Error: Directory of patient not found"
        exit
      fi
      

      echo "Would you like to perform the analysis on the pre-procedure data or on the data collected 24 hours after the procedure? "\
      $'\n'"1. PRE"\
      $'\n'"2. 24H"
      read -p "Opção " moment
      
      case $moment in
      1)
          if [[ -d "$PAT_DIR_PRE" && -d "$OUT_PRE" ]]; then
                cd "$OUT_PRE"
          elif [[ -d "$PAT_DIR_PRE" && ! -d "$OUT_PRE" ]]; then
                echo "Data processing is required"
                read -p "Do you like to continue?(y/n): " yn
                
                case $yn in
                [yY])
                   . "$SCRIPT_DIR/rename_data.sh"
                   cd "$OUT_PRE";;
                   
                [nN]) 
                   echo "Program terminated."
                   exit;;
                
                *)
                  echo "Entrada inválida, programa encerrado"
                  exit;;
                esac  
          else
              echo "Error: Directory $PAT_DIR_PRE not found"
              exit 
          fi;;
      
      2)
          if [[ -d "$PAT_DIR_24" && -d "$OUT_24" ]]; then
                cd "$OUT_24"
          elif [[ -d "$PAT_DIR_24" && ! -d "$OUT_24" ]];then
                echo "É necessário fazer o tratamento de dados"
                read -p "Deseja continuar?(y/n): " yn
                
                case $yn in
                [yY])
                   . "$SCRIPT_DIR/rename_data.sh"
                   cd "$OUT_24";;
                   
                [nN]) 
                   echo "Programa finalizado"
                   exit;;
                
                *)
                  echo "Entrada inválida, programa encerrado"
                  exit;;
                esac  
          else
              echo "Error: Directory $PAT_DIR_24 not found"
              exit 
          fi;;
          
      *)
        echo "Entrada inválida, programa encerrado"
        exit
        
      esac
           
      echo "Deseja realizar qual das etapas?"\
      $'\n'"1.Preprocessing"\
        $'\n'"    Denoise"\
        $'\n'"    Unring"\
        $'\n'"    Mation Correction"\
        $'\n'"    Bias Correction"\
        $'\n'"    Brain mask"\
        $'\n'"    Coregister"\
      $'\n'"2.Freesurfer"\
        $'\n'"    Reconstruction"\
        $'\n'"    Segmentation"\
        $'\n'"    Labeling"\
      $'\n'"3.Tractography"\
        $'\n'"    Response function"\
        $'\n'"    Fiber orientation distribution"\
        $'\n'"    Mask GM/WM"\
        $'\n'"    Streamlines creation"\
        $'\n'"    Streamlines filtering"\
      $'\n'"4.Analysis"\
      $'\n'"5.View"\
		$'\n'"    Raw images"\
        $'\n'"    Results of preprocessing"\
        $'\n'"    Results of segmentation"\
        $'\n'"    Results of tractography"\
        $'\n'"    Results of analysis"\
      $'\n'"6.Rascunho"
       read -p "Opção: " script
       
        case $script in               
        1)
        . "$SCRIPT_DIR/preprocess.sh";;
                
        2)
        . "$SCRIPT_DIR/segmentation.sh";;
        
        3)
        . "$SCRIPT_DIR/tract.sh";;
        
        4)
        . "$SCRIPT_DIR/analysis.sh";;
        
        5)
        . "$SCRIPT_DIR/view.sh";;
        
        6)
        . "$SCRIPT_DIR/rascunho.sh";;
                 
        *)
        echo "invalid response"
        exit;;
        
        esac
                  
        
