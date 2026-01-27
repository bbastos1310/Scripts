    # Files 
    FILE_1="$BASE_DIR/stats.csv"
    FILE_2="$BASE_DIR/results.csv"
    FLAG=0
    FLAG_CONTINUE=1

    # FUNCTIONS

    # Existing file
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
    
    # 1.Response function and Fiber Orientation distribution (FOD)
      handleStats() {
        if [ $EXIST -eq 1 ]; then
        
          export PAT_NUM BASE_DIR 
          python "$SCRIPT_DIR/Python/analysis.py"
          
        else
          exit
        fi
      }

          
    
    # MAIN FUNCTION
      
      cd "$OUT_PRE/Tractography"
           
      read -p "Would you like to do all the analysis? (y/n):  " yn
      case $yn in
      
        [Yy])
        for file in $FILE_1 $FILE_2 ; do
          FILE=$file
          fileExistence
        done  
      
        if [ $FLAG -eq 1 ]; then
            echo "Pelo menos um dos arquivos de saída já existe, o processo irá convertê-los."
            FLAG=0
        fi
      
        if [ $FLAG -eq 0 ]; then
            read -p "Confirma a análise de dados completa? (y/n): " confirm
            case $confirm in
            
            [Yy])
            handleStats
            handleResults;;
            
            [Nn])
            exit;;
            
            esac
        fi
        ;;
        
        [Nn])
        while [ $FLAG_CONTINUE -eq 1 ]; do
          echo "Deseja realizar qual das etapas?"\
          $'\n'"1.Estatísticas individuais do paciente"\
          $'\n'"2.Estatística conjunta dos pacientes "
          read -p "Opção: " step
          
            case $step in
            1)
            FILE=$FILE_1
            fileExistence
            handleStats;;
          
            2)
            FILE=$FILE_2
            fileExistence
            handleResults;;
          
            *) echo invalid response;;
          	
            esac
            
            read -p "Deseja realizar outra etapa da análise de dados (y/n)? " option
          
            case $option in 
            [Yy]) FLAG_CONTINUE=1;;
            [nN]) FLAG_CONTINUE=0;;
            *)  FLAG_CONTINUE=0;;
            esac
          done
          exit;;
        
        *) echo invalid response;;
      esac
    
