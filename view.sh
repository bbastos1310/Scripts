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
      2) mrview dwi_den_unr_preproc_unb_reg.mif -overlay.load voxels.mif;;
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

    # FUNCTIONS SEGMENTATION
    
    # 1. Coregister of T1 and T2 to fsaverage
    handleFsavcoregister() { freeview -v "$OUT_PRE/T1_raw_fsaverage.nii.gz" -v "$OUT_PRE/T2_raw_fsaverage.nii.gz" -v "$OUT_PRE/brain_fsaverage.nii.gz"; }   
    
    # 2. Create annotation files
    handleAnnot() { freeview -f "$SUBJECTS_DIR/$PAT_NUM/surf/lh.pial":annot="$SUBJECTS_DIR/$PAT_NUM/label/lh.Julich_pat.annot" \
    -f "$SUBJECTS_DIR/$PAT_NUM/surf/rh.pial":annot="$SUBJECTS_DIR/$PAT_NUM/label/rh.Julich_pat.annot"; }   
    
    # 3. Segmentation on freesurfer
    handleFreesurferseg() { freeview -v output_freesurfer.mgz:colormap=LUT:lut="$BASE_DIR/Atlas/JulichLUT_freesurfer.txt"; }   
    
    # 4. Segmentation on mrview
    handleMrviewseg() { mrview Julich_parcels_ordered.mif; }   
    
    # 5. Coregister of T1 and Julich_parcels_ordered.mif
    handleT1coregister() { mrview T1_raw.mif -overlay.load Julich_parcels_ordered.mif; }   
        
    # MAIN FUNCTION
            
      echo "Deseja visualizar a imagem de qual etapa? "\
      $'\n'"1.Preprocessing"\
      $'\n'"2.Tractography"\
      $'\n'"3.Segmentation"
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
          $'\n'"7.Raw files"
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
            
      read -p "Deseja visualizar mais imagens da tractografia (y/n)? " option
          
            case $option in 
            [Yy]) FLAG_CONTINUE=1;;
            [nN]) FLAG_CONTINUE=0;;
            *)  FLAG_CONTINUE=0;;
            esac
      done
      ;;
      
      3)
      export FREESURFER_HOME="/usr/local/freesurfer/7.4.1"
      export SUBJECTS_DIR="$SUBJECTS_DIR"
      source "$FREESURFER_HOME/SetUpFreeSurfer.sh"
      
      cd "$OUT_PRE"
      
      while [ $FLAG_CONTINUE -eq 1 ]; do    
          echo "Deseja visualizar a imagem de qual dos processos:"\
          $'\n'"1.Coregistro das imagens T1 e T2 ao espaço fsaverage"\
          $'\n'"2.Annotation files"\
          $'\n'"3.Imagem segmentada no freesurfer"\
          $'\n'"4.Imagem segmentada no mrview"\
          $'\n'"5.Corregistro da imagem segmentada e a imagem T1 no mrview"
          read -p "Opção: " segmentation
          
            case $segmentation in
            1) handleFsavcoregister;;
            2) handleAnnot;;
            3) handleFreesurferseg;;
            4) handleMrviewseg;;
            5) handleT1coregister;;
            esac
            
      read -p "Deseja visualizar mais imagens da segmentação (y/n)? " option
          
            case $option in 
            [Yy]) FLAG_CONTINUE=1;;
            [nN]) FLAG_CONTINUE=0;;
            *)  FLAG_CONTINUE=0;;
            esac
      done
      ;;
      
      4)      
      while [ $FLAG_CONTINUE -eq 1 ]; do    
          echo "Deseja visualizar a imagem de qual dos resultados:"\
          $'\n'"1.Tracts"\
          $'\n'"2.Maps"\
          $'\n'"3.Connectivity matrix"
          read -p "Opção: " analysis
          
            case $analysis in
            1) 
            echo "Deseja visualizar qual trato:"\
              $'\n'"1.Corticospinal tract (CST)"\
              $'\n'"2.Decussating Dentatorubrothalamic Tract (DRTT)"\
              $'\n'"3.Non-Decussating Dentatorubrothalamic Tract (ndDRTT)"\
              $'\n'"Medial lemniscus (ML)"\
              $'\n'"All"
              read -p "Opção: " tract
              
              case $tract in
              1) handleCst;;
              2) handleDrtt;;
              3) handleNddrtt;;
              4) handleMl;;
              5) handleAlltracts;;
              esac
            ;;
            
            2) 
            echo "Deseja visualizar qual mapa:"\
              $'\n'"1.ADC"\
              $'\n'"2.FA"\
              $'\n'"3.CL"\
              $'\n'"4.CS"\
              $'\n'"5.CP"\
              $'\n'"6.AD"\
              $'\n'"7.RD"
              read -p "Opção: " maps
              
              case $maps in
              1) handleADCmap;;
              2) handleFAmap;;
              3) handleCLmap;;
              4) handleCSmap;;
              5) handleCPmap;;
              6) handleADmap;;
              7) handleRDmap;;   
              esac           
            ;;
            
            3) handleConnectivitymatrix;;
            esac
            
      read -p "Deseja visualizar mais imagens dos resultados (y/n)? " option
          
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
