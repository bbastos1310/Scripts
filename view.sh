    FLAG_CONTINUE=1
 
    # FUNCTIONS: PRE PROCESSING

    # 1.Denoising
    handleDenoising() {
      echo "Qual das imagens deseja visualizar?:"$'\n'\
      "1.Denoised image"$'\n'\
      "2.Noise and residual image"$'\n'
      read -p "Opção: " denoising
      
      case $denoising in
      1) mrview dwi_den.mif;;
      2) mrview noise.mif residual.mif;;
      esac
    }

    # 2.Unringing
    handleUnringing() { mrview dwi_den_unr.mif residualUnringed.mif; }

    # 3.Motion correction
    handleMotion() {
      echo "Qual das imagens deseja visualizar?:"$'\n'\
      "1.Preprocessed image"$'\n'\
      "2.AP and PA comparison image"$'\n'
      read -p "Opção: " motion
      
      case $motion in
      1) mrview dwi_den_unr_preproc.mif;;
      2) mrview mean_b0_AP.mif -overlay.load mean_b0_PA.mif;;
      esac
    }

    # 4.Bias correction

    handleBias() { mrview bias.mif -colourmap 2; }

    # 5.Brain mask
    handleMask() { mrview dwi_den_unr_preproc_unbiased.mif -overlay.load dwi_mask.mif; }
    
    # 6.Coregister
    handleCoregister() {
      echo "Qual das imagens deseja visualizar?:"\
      $'\n'"1.Tissues"\
      $'\n'"2.Alignment T1 and dwi"\
      $'\n'"3.Alignment dwi and tissues"\
      $'\n'"4.Alignment T1 and tissues"
      read -p "Opção: " coreg
      
      case $coreg in
      1) mrview 5tt_coreg.mif;;
      2) mrview dwi_den_unr_preproc_unb_reg.mif -overlay.load T1_raw.mif;;
      3) mrview dwi_den_unr_preproc_unb_reg.mif -overlay.load 5tt_coreg.mif -overlay.colourmap 2;;
      4) mrview T1_raw.mif -overlay.load 5tt_coreg.mif -overlay.colourmap 2;;
      esac
    }

    # 7.Response function
    handleRF() {
      echo "Qual das imagens deseja visualizar?:"$'\n'\
      "1.WM, GM and CSF response function"$'\n'\
      "2.Response function with the dwi"$'\n'
      read -p "Opção: " rf
      
      case $rf in
      1) shview wm.txt & shview gm.txt & shview csf.txt ;;
      2) mrview voxels.mif -overlay.load dwi_den_unr_preproc_unb_reg.mif;;
      esac
    }

    # 8.Fiber orientation distribution(FOD)
    handleFod() { mrview vf.mif -odf.load_sh wmfod.mif; }

    # 9.Raw files
    handleRaw() {
      echo "Qual das imagens deseja visualizar?:"$'\n'\
      "1.Dwi"$'\n'\
      "2.T1"$'\n'
      read -p "Opção: " raw
      
      case $raw in
      1) mrview dwi_raw.mif;;
      2) mrview T1_raw.mif;;
      esac
    }

    # FUNCTIONS TRACTOGRAPHY

    # 1.Mask between GM/WM
    handleFringe() { mrview dwi_den_unr_preproc_unb_reg.mif -overlay.load gmwmSeed_coreg.mif; }

    # 2.Streamline creation
    handleStreamlines() { mrview dwi_den_unr_preproc_unb_reg.mif -tractography.load smallerTracks_200k.tck; }

    # 3.Streamlines filtering
    handleSift() { mrview dwi_den_unr_preproc_unb_reg.mif -tractography.load smallerTracks_200k.tck & mrview dwi_den_unr_preproc_unb_reg.mif -tractography.load smallerTracks_200k.tck; }

    # MAIN FUNCTION
            
      echo "Deseja visualizar a imagem de qual etapa? "\
      $'\n'"1.Preprocessing"\
      $'\n'"2.Tractography"
      read -p "Etapa: " option
      case $option in
      1)
      while [ $FLAG_CONTINUE -eq 1 ]; do
          echo "Deseja visualizar a imagem de qual dos processos:"\
          $'\n'"1.Denoising"\
          $'\n'"2.Unringing"\
          $'\n'"3.Motion correction"\
          $'\n'"4.Bias correction"\
          $'\n'"5.Brain mask"\
          $'\n'"6.Coregister"\
          $'\n'"7.Response function"\
          $'\n'"8.Fiber orientation distribution"\
          $'\n'"9.Raw files"
          read -p "Opção: " process
          
            case $process in
            1) handleDenoising;;
            2) handleUnringing;;
            3) handleMotion;;
            4) handleBias;;
            5) handleMask;;
            6) handleCoregister;;
            7) handleRaw;;
            *) echo invalid response;;
            esac
            
          read -p "Deseja visualizar mais imagens do preprocessing (y/n)? " option
          
            case $option in 
            [Yy]) FLAG_CONTINUE=1;;
            [nN]) FLAG_CONTINUE=0;;
            *)  FLAG_CONTINUE=0;;
            esac
      done
      ;;
      
      2)
      while [ $FLAG_CONTINUE -eq 1 ]; do    
          echo "Deseja visualizar a imagem de qual dos processos:"\
          $'\n'"1.Response function"\
          $'\n'"2.Fiber orientation distribution"\
          $'\n'"3.Mask GM/WM"\
          $'\n'"4.Streamlines"\
          $'\n'"5.Streamlines filtering (SIFT)"
          read -p "Opção: " tract
          
            case $tract in
            1) handleRF;;
            2) handleFod;;
            3) handleFringe;;
            4) handleStreamlines;;
            5) handleSift;;
            esac
            
      read -p "Deseja visualizar mais imagens do preprocessing (y/n)? " option
          
            case $option in 
            [Yy]) FLAG_CONTINUE=1;;
            [nN]) FLAG_CONTINUE=0;;
            *)  FLAG_CONTINUE=0;;
            esac
      done
      ;;
            
      *)
      echo invalid response;;
      
      esac
