    ANALYSIS_DIR="$PAT_DIR/Analysis"
    FLAG_CONTINUE=1
	
	# FUNCTIONS: RAW FILES
    handleRaw() {
      echo "Qual das imagens deseja visualizar?:"$'\n'\
      "1.Dwi"$'\n'\
      "2.T1"$'\n'\
      "3.T2"$'\n'\
      "4.WMnull"$'\n'      
      read -p "Opção: " raw
      
      case $raw in
      1) mrview Raw/dwi_raw.mif;;
      2) mrview Raw/T1_raw.mif;;
      3) mrview Raw/T2_raw.mif;;
      4) mrview Raw/Contrast_raw.mif;;
      esac
    } 
	
    # FUNCTIONS: PRE PROCESSING

    # 1.Denoising
    handleDenoising() {
      echo "Qual das imagens deseja visualizar?:"$'\n'\
      "1.Denoised image"$'\n'\
      "2.Noise and residual image"$'\n'
      read -p "Opção: " denoising
      
      case $denoising in
      1) mrview Preprocess/dwi_den.mif;;
      2) mrview Preprocess/noise.mif;;
      esac
    }

    # 2.Unringing
    handleUnringing() { mrview Preprocess/dwi_den_unr.mif -overlay.load Preprocess/residualUnringed.mif -overlay.opacity 0.7; }

    # 3.Motion correction
    handleMotion() {
      echo "Qual das imagens deseja visualizar?:"$'\n'\
      "1.Preprocessed image"$'\n'\
      "2.AP and PA comparison image"$'\n'
      read -p "Opção: " motion
      
      case $motion in
      1) mrview Preprocess/dwi_den_unr_preproc.mif -overlay.load Preprocess/dwi_den_unr.mif -overlay.opacity 0.5;;
      2) mrview Preprocess/mean_b0_AP.mif -overlay.load Preprocess/mean_b0_PA.mif -overlay.opacity 0.5;;
      esac
    }

    # 4.Bias correction

    handleBias() { mrview Preprocess/bias.mif -colourmap 2 -overlay.load Preprocess/dwi_den_unr_preproc_unbiased.mif -overlay.opacity 0.5 -overlay.colourmap 0 ; }

    # 5.Brain mask
    handleMask() { mrview Preprocess/dwi_den_unr_preproc_unbiased.mif -overlay.load Preprocess/dwi_mask.mif -overlay.opacity 0.5; }
    
    # 6.Coregister
    handleCoregister() {
      echo "Qual das imagens deseja visualizar?:"\
      $'\n'"1.Tissues"\
      $'\n'"2.Alignment T1 and dwi"\
      $'\n'"3.Alignment dwi and tissues"
      read -p "Opção: " coreg
      
      case $coreg in
      1) mrview Preprocess/5tt_coreg.mif -overlay.load Raw/T1_raw.mif -overlay.opacity 0.5;;
      2) mrview Preprocess/dwi_den_unr_preproc_unb_reg.mif -overlay.load Raw/T1_raw.mif -overlay.opacity 0.3;;
      3) mrview Preprocess/dwi_den_unr_preproc_unb_reg.mif -overlay.load Preprocess/5tt_coreg.mif -overlay.colourmap 2 -overlay.opacity 0.3;;
      esac
    }
         
    # FUNCTIONS SEGMENTATION
    
    # 1. Coregister of T1 and T2 to fsaverage
    handleT2freesurfer() { freeview -v "$SUBJECTS_DIR/$PAT_NUM/mri/T2.mgz" -f "$SUBJECTS_DIR/$PAT_NUM/surf/lh.pial" -f "$SUBJECTS_DIR/$PAT_NUM/surf/rh.pial" --viewport axial ; }    
    
    # 2. Create annotation files
    handleNextbrain() { freeview -v "$SUBJECTS_DIR/$PAT_NUM/mri/T2.mgz" -v "$SUBJECTS_DIR/$PAT_NUM/next_brain_segmentation/seg_left.nii.gz":colormap=LUT:lut="$SUBJECTS_DIR/$PAT_NUM/next_brain_segmentation/lookup_table.txt" \
	-v "$SUBJECTS_DIR/$PAT_NUM/next_brain_segmentation/seg_right.nii.gz":colormap=LUT:lut="$SUBJECTS_DIR/$PAT_NUM/next_brain_segmentation/lookup_table.txt"	 --viewport axial ; }   
    
    # 3. Create annotation files
    handleAnnot() { freeview -v "$SUBJECTS_DIR/$PAT_NUM/mri/T2.mgz" -f "$SUBJECTS_DIR/$PAT_NUM/surf/lh.pial":annot="$SUBJECTS_DIR/$PAT_NUM/label/lh.JULICH.annot" \
    -f "$SUBJECTS_DIR/$PAT_NUM/surf/rh.pial":annot="$SUBJECTS_DIR/$PAT_NUM/label/rh.JULICH.annot" --viewport 3d ; }   
    
    # 3. Segmentation on freesurfer
    handleFreesurferseg() { 
		echo "Qual das imagens deseja visualizar?:"$'\n'\
        "1.Atlas probabilístico das ROIs no espaço nativo do paciente"$'\n'\
        "2.Segmentação subcortical automática do freesurfer"$'\n'\
        "3.Segmentação cortical do freesurfer usando o JulichBrain atlas"$'\n'\
        "4.Segmentação no mrtrix (incluindo ROIs do Julich atlas)"$'\n'
        read -p "Opção: " fsseg
      
        case $fsseg in
        1) freeview -v T2_resampled.nii.gz \
        -v NRp_lh_coreg_weighted_transformed.nii.gz:colormap=heat \
        -v NRp_rh_coreg_weighted_transformed.nii.gz:colormap=heat \
        -v NRm_lh_coreg_weighted_transformed.nii.gz:colormap=pet \
        -v NRm_rh_coreg_weighted_transformed.nii.gz:colormap=pet \
        -v SNc_lh_coreg_weighted_transformed.nii.gz:colormap=heat \
        -v SNc_rh_coreg_weighted_transformed.nii.gz:colormap=heat \
        -v SNr_lh_coreg_weighted_transformed.nii.gz:colormap=pet \
        -v SNr_rh_coreg_weighted_transformed.nii.gz:colormap=pet \
        -v DNd_lh_coreg_weighted_transformed.nii.gz:colormap=heat \
        -v DNd_rh_coreg_weighted_transformed.nii.gz:colormap=heat \
        -v DNv_lh_coreg_weighted_transformed.nii.gz:colormap=pet \
        -v DNv_rh_coreg_weighted_transformed.nii.gz:colormap=pet 
        ;;
        2) freeview -v T2_resampled.nii.gz -v "$SUBJECTS_DIR/$PAT_NUM/mri/aseg.mgz";;
        3) freeview -v T2_resampled.nii.gz -v output_freesurfer.mgz:colormap=LUT:lut="$ATLAS_DIR/JulichLUT_complete.txt";;
        4) mrview Julich_parcels_mrtrix_colored.mif -overlay.load "$OUT_PRE/T2_resampled.nii.gz" -overlay.opacity 0.3 -overlay.colourmap 0;;
        esac
    }
		
	# FUNCTIONS TRACTOGRAPHY
    
    # 1.Response function
    handleRF() {
      echo "Qual das imagens deseja visualizar?:"$'\n'\
      "1.WM, GM and CSF response function"$'\n'\
      "2.Response function with the dwi"$'\n'
      read -p "Opção: " rf
      
      case $rf in
      1) shview wm.txt & shview gm.txt & shview csf.txt ;;
      2) mrview dwi_den_unr_preproc_unb_reg.mif -overlay.load voxels.mif -overlay.opacity 0.5;;
      esac
    }

    # 2.Fiber orientation distribution(FOD)
    handleFod() { mrview vf.mif -odf.load_sh wmfod.mif; }

    # 3.Mask between GM/WM
    handleFringe() { mrview dwi_den_unr_preproc_unb_reg.mif -overlay.load gmwmSeed_coreg.mif -overlay.opacity 0.3; }

    # 4.Streamline creation
    handleStreamlines() { mrview dwi_den_unr_preproc_unb_reg.mif -tractography.load smallerTracks_200k.tck; }
    
    # FUNCTIONS ANALYSIS
      
     # 1. Visualização dos mapas
    handleMaps() { 
    	cd "$ANALYSIS_DIR/Results/"  
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
              1) mrview ADCmap\(PRE\).nii.gz -colourmap 5 | mrview ADCmap\(24H\).nii.gz -colourmap 5 | mrview ADCmap\(Subtraction\).nii.gz -colourmap 4 -overlay.load "$ANALYSIS_DIR/Results/mask_lesion.nii.gz" -overlay.opacity 0.3;;
              2) mrview FAmap\(PRE\).nii.gz -colourmap 7 | mrview FAmap\(24H\).nii.gz -colourmap 7 | mrview FAmap\(Subtraction\).nii.gz -colourmap 4 -overlay.load "$ANALYSIS_DIR/Results/mask_lesion.nii.gz" -overlay.opacity 0.3;;
              3) mrview CLmap\(PRE\).nii.gz -colourmap 5 | mrview CLmap\(24H\).nii.gz -colourmap 5 | mrview CLmap\(Subtraction\).nii.gz -colourmap 4 -overlay.load "$ANALYSIS_DIR/Results/mask_lesion.nii.gz" -overlay.opacity 0.3;;
              4) mrview CSmap\(PRE\).nii.gz -colourmap 5 | mrview CSmap\(24H\).nii.gz -colourmap 5 | mrview CSmap\(Subtraction\).nii.gz -colourmap 4 -overlay.load "$ANALYSIS_DIR/Results/mask_lesion.nii.gz" -overlay.opacity 0.3;;
              5) mrview CPmap\(PRE\).nii.gz -colourmap 5 | mrview CPmap\(24H\).nii.gz -colourmap 5 | mrview CPmap\(Subtraction\).nii.gz -colourmap 4 -overlay.load "$ANALYSIS_DIR/Results/mask_lesion.nii.gz" -overlay.opacity 0.3;;
              6) mrview ADmap\(PRE\).nii.gz -colourmap 5 | mrview ADmap\(24H\).nii.gz -colourmap 5 | mrview ADmap\(Subtraction\).nii.gz -colourmap 4 -overlay.load "$ANALYSIS_DIR/Results/mask_lesion.nii.gz" -overlay.opacity 0.3;;
              7) mrview RDmap\(PRE\).nii.gz -colourmap 5 | mrview RDmap\(24H\).nii.gz -colourmap 5 | mrview RDmap\(Subtraction\).nii.gz -colourmap 4 -overlay.load "$ANALYSIS_DIR/Results/mask_lesion.nii.gz" -overlay.opacity 0.3;;   
              esac 
     } 
     
     # 2. Visualização dos tratos
    handleTracks() {
   	      cd "$OUT_PRE"
		echo "Deseja visualizar qual trato:"\
              $'\n'"1.Corticospinal tract (CST)"\
              $'\n'"2.Decussating Dentatorubrothalamic Tract (DRTT)"\
              $'\n'"3.Non-Decussating Dentatorubrothalamic Tract (ndDRTT)"\
              $'\n'"Medial lemniscus (ML)"\
              $'\n'"All"
              read -p "Opção: " tract
              
              case $tract in
              1) mrview T2_resampled.nii.gz -tractography.load cst_track_lh.tck -plane 1 ;;
              2) mrview T2_resampled.nii.gz -tractography.load DRTT_track_lh.tck -plane 1;;
              3) mrview T2_resampled.nii.gz -tractography.load nDRTT_track_lh.tck  -plane 1;;
              4) mrview T2_resampled.nii.gz -tractography.load ml_track_lh.tck -plane 1;;
              5) mrview T2_resampled.nii.gz -tractography.load ml_track_lh.tck -tractography.load nDRTT_track_lh.tck -tractography.load cst_track_lh.tck -plane 1;;
              esac 
     } 
    
    handleConnectivitymatrix() { xdg-open "$ANALYSIS_DIR/Results/connectivitymatrix.png" ; }
    
    handleMasklesion() {
    	cd "$ANALYSIS_DIR/Results/" 
    	mrview "$ANALYSIS_DIR/T1_raw_24_coreg.mif" -overlay.load mask_lesion.nii.gz -overlay.opacity 0.3 ; }
        
    # MAIN FUNCTION
            
      echo "Deseja visualizar a imagem de qual etapa? "\
      $'\n'"0.Raw images"\
      $'\n'"1.Preprocessing"\
      $'\n'"2.Segmentation"\
      $'\n'"3.Tractography"\
      $'\n'"4.Analysis"      
      read -p "Etapa: " option
      case $option in
      
      # RAW FILES
      0)
      while [ $FLAG_CONTINUE -eq 1 ]; do
          handleRaw       
          read -p "Deseja visualizar mais imagens do preprocessing (y/n)? " option
          
            case $option in 
            [Yy]) FLAG_CONTINUE=1;;
            [nN]) FLAG_CONTINUE=0;;
            *)  FLAG_CONTINUE=0;;
            esac
      done
      ;;
      
      # PREPROCESSING
      1)
      while [ $FLAG_CONTINUE -eq 1 ]; do
          echo "Deseja visualizar a imagem de qual dos processos:"\
          $'\n'"1.Denoising"\
          $'\n'"2.Unringing"\
          $'\n'"3.Motion correction"\
          $'\n'"4.Bias correction"\
          $'\n'"5.Brain mask"\
          $'\n'"6.Coregister"
          read -p "Opção: " process
          
            case $process in
            1) handleDenoising;;
            2) handleUnringing;;
            3) handleMotion;;
            4) handleBias;;
            5) handleMask;;
            6) handleCoregister;;
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
           
      # SEGMENTATION
      2)
      export FREESURFER_HOME="/usr/local/freesurfer/7.4.1"
      export SUBJECTS_DIR="$SUBJECTS_DIR"
      source "$FREESURFER_HOME/SetUpFreeSurfer.sh"
      
      cd "$OUT_PRE"
      
      while [ $FLAG_CONTINUE -eq 1 ]; do    
          echo "Deseja visualizar a imagem de qual dos processos:"\
          $'\n'"1.Imagem T2 processada pelo freesurfer"\
          $'\n'"2.Segmentação do atlas Nextbrain"\
          $'\n'"3.Visualização 3D da segmentação cortical"\
         			
          read -p "Opção: " segmentation
          
            case $segmentation in
            1) handleT2freesurfer;;
            2) handleNextbrain;;
            3) handleAnnot;;
            esac
            
      read -p "Deseja visualizar mais imagens da segmentação (y/n)? " option
          
            case $option in 
            [Yy]) FLAG_CONTINUE=1;;
            [nN]) FLAG_CONTINUE=0;;
            *)  FLAG_CONTINUE=0;;
            esac
      done
      ;;
      
      # TRACTOGRAPHY
      3)
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
            esac
            
      read -p "Deseja visualizar mais imagens da tractografia (y/n)? " option
          
            case $option in 
            [Yy]) FLAG_CONTINUE=1;;
            [nN]) FLAG_CONTINUE=0;;
            *)  FLAG_CONTINUE=0;;
            esac
      done
      ;;
      
      # ANALYSIS
      4)    
      while [ $FLAG_CONTINUE -eq 1 ]; do    
          echo "Deseja visualizar a imagem de qual dos resultados:"\
          $'\n'"1.Maps"\
          $'\n'"2.Tracts"\
          $'\n'"3.Connectivity matrix"\
          $'\n'"4.Máscara da lesão"
          read -p "Opção: " analysis
          
            case $analysis in
            1) handleMaps;;
            2) handleTracks;;
            3) handleConnectivitymatrix;;
            4) handleMasklesion;;
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
