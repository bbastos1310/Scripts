    BASE_DIR="/home/brunobastos/Mestrado/Dados"
    SCRIPT_DIR="/home/brunobastos/Mestrado/Scripts"
    SUBJECTS_DIR="$BASE_DIR/fs_subjects"
    ATLAS_DIR="$BASE_DIR/Atlas"    

    # Files 
    FILE_1="rename_data.sh"
    FILE_2="preprocess.sh"
    FILE_3="tract.sh"
    FILE_4="view.sh"
    FILE_5="analysis.sh"
    FILE_6="start.sh"
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
        echo "Verifique a pasta dos scripts, na pasta definida atualmente estão faltanto $FLAG_SCRIPT arquivos .sh"
        exit
    fi
    
    # Definition of the databases folder
    if [ -d "$BASE_DIR" ]; then
        echo "Pasta de dados atual: $BASE_DIR"
        read -p "Confirma o uso dessa pasta?(y/n) " BASE
        
        case $BASE in
            # Complete preprocessing
            [Yy])
            echo "Endereço da pasta de dados: $BASE_DIR";;

            [Nn])
            read -p "Digite o endereço completo da pasta de dados: " NEW_BASE
                     
            if [ -d "$NEW_BASE" ]; then
                BASE_DIR=$NEW_BASE
                echo "Endereço da Pasta de dados: $BASE_DIR"
            else
                echo "Pasta inválida, abra o programa novamente ou mude a pasta base no script"
                exit
            fi;;
        esac
    else
        echo "A pasta de dados registrada no script é inválida"
        read -p "Digit o endereço completo da pasta de dados: " NEW_BASE
        if [ -d "$NEW_BASE" ]; then
                BASE_DIR=$NEW_BASE
                echo "Endereço da Pasta de dados: $BASE_DIR"
            else
                echo "Pasta inválida, abra o programa novamente ou mude a pasta base no script"
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
      
      if [[ ! -d "$PAT_DIR_PRE" && ! -d "$PAT_DIR_24" ]]; then
        echo "Error: Directory of patient not found"
        exit
      fi
      

      echo "Deseja realizar a análise para os dados pré procedimento ou 24 horas após o procedimento?: "\
      $'\n'"1. PRE"\
      $'\n'"2. 24H"
      read -p "Opção " moment
      
      case $moment in
      1)
          if [[ -d "$PAT_DIR_PRE" && -d "$OUT_PRE" ]]; then
                cd "$OUT_PRE"
                echo "passou"
          elif [[ -d "$PAT_DIR_PRE" && ! -d "$OUT_PRE" ]]; then
                echo "É necessário fazer o tratamento de dados"
                read -p "Deseja continuar?(y/n): " yn
                
                case $yn in
                [yY])
                   . "$SCRIPT_DIR/rename_data.sh"
                   cd "$OUT_PRE";;
                   
                [nN]) 
                   echo "Programa finalizado"
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
      $'\n'"2.Tractography"\
        $'\n'"    Response function"\
        $'\n'"    Fiber orientation distribution"\
        $'\n'"    Mask GM/WM"\
        $'\n'"    Streamlines creation"\
        $'\n'"    Streamlines weighting"\
      $'\n'"3.Freesurfer"\
        $'\n'"    Reconstruction"\
        $'\n'"    Segmentation"\
        $'\n'"    Labeling"\
        $'\n'"    Connectivity matrix"\
      $'\n'"4.Analysis"\
      $'\n'"5.View"\
        $'\n'"    Results of preprocessing"\
        $'\n'"    Results of tractography"\
        $'\n'"    Results of segmentation"\
        $'\n'"    Results of analysis"
       read -p "Opção: " script
       
        case $script in               
        1)
        . "$SCRIPT_DIR/preprocess.sh";;
        
        2)
        . "$SCRIPT_DIR/tract.sh";;
        
        3)
        . "$SCRIPT_DIR/segmentation.sh";;
        
        4)
        . "$SCRIPT_DIR/analysis.sh";;
        
        5)
        . "$SCRIPT_DIR/view.sh";;
                 
        *)
        echo "invalid response"
        exit;;
        
        esac
            
      echo "teste"
      
        
