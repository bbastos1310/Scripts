    # Files 
    FILE_1="wm.txt"
    FILE_2="wmfod.mif"    
    FILE_3="gmwmSeed_coreg.mif"
    FILE_4="tracks_10mio.tck"
    FILE_5="sift_weights.txt"
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
    
    # 1.Resample and response function
      handleFunction() {
        if [ $EXIST -eq 1 ]; then
          dwi2response dhollander dwi_den_unr_preproc_unb_reg.mif wm.txt gm.txt csf.txt -voxels voxels.mif -mask "$OUT_PRE/dwi_mask_up_reg.mif" -force
        else
          exit
        fi
      }

      # 2.Fiber orientation distribution (FOD)
      handleFod() {
        if [ $EXIST -eq 1 ]; then
          time ss3t_csd_beta1 dwi_den_unr_preproc_unb_reg.mif wm.txt wmfod.mif gm.txt gmfod.mif csf.txt csffod.mif -mask "$OUT_PRE/dwi_mask_up_reg.mif" -force
          mrconvert -coord 3 0 wmfod.mif - | mrcat csffod.mif gmfod.mif - vf.mif -force
          mtnormalise wmfod.mif wmfod_norm.mif gmfod.mif gmfod_norm.mif csffod.mif csffod_norm.mif -mask "$OUT_PRE/dwi_mask_up_reg.mif" -force
        else
          exit
        fi
      }
    
    # 3.Mask between GM and WM
    handleFringe() {
      if [ $EXIST -eq 1 ]; then
        5tt2gmwmi 5tt_coreg.mif gmwmSeed_coreg.mif -force
      else
        exit
      fi
    }

    # 4.Streamlines creation
    handleStreamlines() {
      if [ $EXIST -eq 1 ]; then
        time tckgen -act 5tt_coreg.mif -backtrack -seed_gmwmi gmwmSeed_coreg.mif -select 10000000 wmfod_norm.mif tracks_10mio.tck -force
        tckedit tracks_10mio.tck -number 200k smallerTracks_200k.tck -force
      else
        exit
      fi
    }

    # 5.SIFT (Streamlines filtering)
    handleSift() {
      if [ $EXIST -eq 1 ]; then
        time tcksift2 -act 5tt_coreg.mif -out_mu sift_mu.txt -out_coeffs sift_coeffs.txt -nthreads 4 tracks_10mio.tck wmfod_norm.mif sift_weights.txt -force
      else
        exit
      fi
    }

    # MAIN FUNCTION
    
      read -p "Would you like to do all the tractography? (y/n):  " yn
      case $yn in
      
        [Yy])
        for file in $FILE_1 $FILE_2 $FILE_3 $FILE_4 $FILE_5; do
          FILE=$file
          fileExistence
        done  
      
        if [ $FLAG -eq 1 ]; then
            echo "Pelo menos um dos arquivos de saída já existe, o processo irá convertê-los."
            FLAG=0
        fi
      
        if [ $FLAG -eq 0 ]; then
            read -p "Confirma a tratografia completa? (y/n): " confirm
            case $confirm in
            
            [Yy])
            handleFunction
            handleFod            
            handleFringe
            handleStreamlines
            handleSift;;
            
            [Nn])
            exit;;
            
            esac
        fi
        ;;
        
        [Nn])
        while [ $FLAG_CONTINUE -eq 1 ]; do
          echo "Deseja realizar qual das etapas?"\
          $'\n'"1.Response function"\
          $'\n'"2.Fiber orientation distribution"\
          $'\n'"3.Mask GM/WM"\
          $'\n'"4.Streamlines creation"\
          $'\n'"5.Streamlines filtering"
          read -p "Opção: " step
          
            case $step in
            1)
            FILE=$FILE_1
            fileExistence
            handleFunction;;
          
            2)
            FILE=$FILE_2
            fileExistence
            handleFod;;          
          
            3)
            FILE=$FILE_3
            fileExistence
            handleFringe;;
          
            4)
            FILE=$FILE_4
            fileExistence
            handleStreamlines;;
          
            5)
            FILE=$FILE_5
            fileExistence
            handleSift;;
          
            *) echo invalid response;;
          	
            esac
            
            read -p "Deseja realizar outra etapa da tractografia (y/n)? " option
          
            case $option in 
            [Yy]) FLAG_CONTINUE=1;;
            [nN]) FLAG_CONTINUE=0;;
            *)  FLAG_CONTINUE=0;;
            esac
          done
          exit;;
        
        *) echo invalid response;;
      esac
    
