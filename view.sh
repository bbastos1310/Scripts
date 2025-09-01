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
      1) mrview dwi_raw.mif;;
      2) mrview T1_raw.mif;;
      3) mrview T2_raw.mif;;
      4) mrview Contrast_raw.mif;;
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
      1) mrview dwi_den.mif;;
      2) mrview noise.mif;;
      esac
    }

    # 2.Unringing
    handleUnringing() { mrview dwi_den_unr.mif -overlay.load residualUnringed.mif -overlay.opacity 0.7; }

    # 3.Motion correction
    handleMotion() {
      echo "Qual das imagens deseja visualizar?:"$'\n'\
      "1.Preprocessed image"$'\n'\
      "2.AP and PA comparison image"$'\n'
      read -p "Opção: " motion
      
      case $motion in
      1) mrview dwi_den_unr_preproc.mif -overlay.load dwi_den_unr.mif -overlay.opacity 0.5;;
      2) mrview mean_b0_AP.mif -overlay.load mean_b0_PA.mif -overlay.opacity 0.5;;
      esac
    }

    # 4.Bias correction

    handleBias() { mrview bias.mif -colourmap 2 -overlay.load dwi_den_unr_preproc_unbiased.mif -overlay.opacity 0.5 -overlay.colourmap 0 ; }

    # 5.Brain mask
    handleMask() { mrview dwi_den_unr_preproc_unbiased.mif -overlay.load dwi_mask.mif -overlay.opacity 0.5; }
    
    # 6.Coregister
    handleCoregister() {
      echo "Qual das imagens deseja visualizar?:"\
      $'\n'"1.Tissues"\
      $'\n'"2.Alignment T1 and dwi"\
      $'\n'"3.Alignment dwi and tissues"
      read -p "Opção: " coreg
      
      case $coreg in
      1) mrview $OUT_PRE/Preprocess/5tt_coreg.mif -overlay.load $OUT_PRE/Raw/T1_raw.mif -overlay.opacity 0.5 -plane 1;;
      2) mrview dwi_den_unr_preproc_unb_reg.mif -overlay.load $OUT_PRE/Raw/T1_raw.mif -overlay.opacity 0.3 -plane 1;;
      3) mrview dwi_den_unr_preproc_unb_reg.mif -overlay.load $OUT_PRE/Preprocess/5tt_coreg.mif -overlay.colourmap 2 -overlay.opacity 0.3 -plane 1;;
      esac
    }
         
    # FUNCTIONS SEGMENTATION
    
    # 1. T2 on freesurfer
    handleT2freesurfer() { freeview -v "$SUBJECTS_DIR/$PAT_NUM/mri/T2.mgz" -f "$SUBJECTS_DIR/$PAT_NUM/surf/lh.pial" -f "$SUBJECTS_DIR/$PAT_NUM/surf/rh.pial" --viewport axial ; }    
    
    # 2. Next brain segmentation
    handleNextbrain() { freeview -v "$SUBJECTS_DIR/$PAT_NUM/mri/T2.mgz" -v "$SUBJECTS_DIR/$PAT_NUM/next_brain_segmentation/seg_left.nii.gz":colormap=LUT:lut="$SUBJECTS_DIR/$PAT_NUM/next_brain_segmentation/lookup_table.txt" \
	-v "$SUBJECTS_DIR/$PAT_NUM/next_brain_segmentation/seg_right.nii.gz":colormap=LUT:lut="$SUBJECTS_DIR/$PAT_NUM/next_brain_segmentation/lookup_table.txt"	 --viewport axial ; }   
       
    # 3. Maps
    handleMaps() { 
		echo "Qual das imagens deseja visualizar?:"$'\n'\
		"1.Fractional Anisotropy (FA) map"$'\n'\
        "2.Apparent Diffusion Coefficient (ADC) map"$'\n'\
        "3.Axial Diffusivity (AD) map"$'\n'\
        "4.Linear Anisotropy Coefficient (CL) map"$'\n'\
        "5.Planar Anisotropy Coefficient (CP) map"$'\n'\
        "6.Spherical Anisotropy Coefficient (CS) map"$'\n'\
        "7.Radial Diffusivity (RD) map"$'\n'
        read -p "Opção: " map
        
        case $map in
        1) mrview Contrast_raw_coreg_24.mif -colourmap 1 -overlay.load "Maps/FAmap(PRE).nii.gz" -overlay.colourmap 6 -overlay.opacity 0.8 ;;
        2) mrview "Maps/ADCmap(PRE).nii.gz" -colourmap 4 -overlay.load Contrast_raw_coreg_24.mif -overlay.opacity 0.5 ;;
        3) mrview "Maps/ADmap(PRE).nii.gz" -colourmap 4 -overlay.load Contrast_raw_coreg_24.mif -overlay.opacity 0.5 ;;
        4) mrview "Maps/CLmap(PRE).nii.gz" -colourmap 4 -overlay.load Contrast_raw_coreg_24.mif -overlay.opacity 0.5 ;;
        5) mrview "Maps/CPmap(PRE).nii.gz" -colourmap 4 -overlay.load Contrast_raw_coreg_24.mif -overlay.opacity 0.5 ;;
        6) mrview "Maps/CSmap(PRE).nii.gz" -colourmap 4 -overlay.load Contrast_raw_coreg_24.mif -overlay.opacity 0.5 ;;
        7) mrview "Maps/RDmap(PRE).nii.gz" -colourmap 4 -overlay.load Contrast_raw_coreg_24.mif -overlay.opacity 0.5 ;;
        
        esac
	}
	
	# 4. Create annotation files
    handleAnnot() { 
		echo "Qual das imagens deseja visualizar?:"$'\n'\
		"1.Segmentação cortical (Julich atlas)"$'\n'\
		"2.Segmentação cortical 3D (Julich atlas)"$'\n'\
        "3.Segmentação completa cortical (Julich atlas) e subcortical (next brain atlas)"$'\n'\
        "4.Regiões de interesse (ROIs)"$'\n'\
        "5.Estimativa inicial do local da lesão"$'\n'
        read -p "Opção: " annot
        
        case $annot in
        1) freeview -v Contrast_raw_coreg_24.nii.gz -v output_freesurfer.mgz:colormap=LUT:lut="$ATLAS_DIR/JulichLUT_complete.txt" ;;
        2) freeview -v Contrast_raw_coreg_24.nii.gz -f "$SUBJECTS_DIR/$PAT_NUM/surf/lh.pial":annot="$SUBJECTS_DIR/$PAT_NUM/label/lh.JULICH.annot" \
		-f "$SUBJECTS_DIR/$PAT_NUM/surf/rh.pial":annot="$SUBJECTS_DIR/$PAT_NUM/label/rh.JULICH.annot" --viewport 3d ;;
        3) mrview full_segmentation_colored.mif -overlay.load Contrast_raw_coreg_24.mif -overlay.opacity 0.3 -overlay.colourmap 0 ;;
        4) freeview -v Contrast_raw_coreg_24.nii.gz -v ROIs_tracks.nii.gz:colormap=LUT:lut="$ATLAS_DIR/lookup_ROIs.txt" ;;
        5) mrview Contrast_raw_coreg_24.mif -overlay.load mask_lesion_binary.nii.gz -overlay.opacity 0.4 ;;
        
        esac 
        
        }
     
    		
	# FUNCTIONS TRACTOGRAPHY
    
    # 1.Response function
    handleRF() {
      echo "Qual das imagens deseja visualizar?:"$'\n'\
      "1.WM, GM and CSF response function"$'\n'\
      "2.Response function with the dwi"$'\n'\
      "3.Fiber orientation distribution (FOD)"$'\n'
      read -p "Opção: " rf
      
      case $rf in
      1) shview wm.txt & shview gm.txt & shview csf.txt ;;
      2) mrview ../Segmentation/Contrast_raw_coreg_24.mif -overlay.load voxels.mif -overlay.opacity 0.5;;
      3) mrview vf.mif -odf.load_sh wmfod.mif;;
      esac
    }

    # 2.Mask between GM/WM
    handleROI() { mrview ../Segmentation/Contrast_raw_coreg_24.mif -overlay.load gmwmSeed_coreg.mif -overlay.opacity 0.3; }
     
    # 3. Visualização dos tratos
    handleTracks() {
		echo "Deseja visualizar qual trato:"\
			  $'\n'"1.Non-Decussating Dentatorubrothalamic Tract (ndDRTT)"\
			  $'\n'"2.Decussating Dentatorubrothalamic Tract (dDRTT)"\
			  $'\n'"3.Corticospinal tract (CST)"\
			  $'\n'"4.Medial lemniscus (ML)"\
			  $'\n'"5.All"
			  read -p "Opção: " tract
			  
			  if [[ "$hemisphere" == "left" ]]; then
				  case $tract in
				  1) mrview ../Segmentation/Contrast_raw_coreg_24.mif -tractography.load track_ndDRTT_lh.tck -plane 1 ;;
				  2) mrview ../Segmentation/Contrast_raw_coreg_24.mif -tractography.load track_dDRTT_lh.tck -plane 1	;;
				  3) mrview ../Segmentation/Contrast_raw_coreg_24.mif -tractography.load track_CST_lh.tck  -plane 1 ;;
				  4) mrview ../Segmentation/Contrast_raw_coreg_24.mif -tractography.load track_ML_lh.tck -plane 1 ;;
				  5) mrview ../Segmentation/Contrast_raw_coreg_24.mif -tractography.load track_CST_lh.tck -tractography.load track_dDRTT_lh.tck -tractography.load track_ML_lh.tck -plane 1 ;;
				  esac 
				  
			  elif [[ "$hemisphere" == "right" ]]; then
				  case $tract in
				  1) mrview ../Segmentation/Contrast_raw_coreg_24.mif -tractography.load track_ndDRTT_rh.tck -plane 2 ;;
				  2) mrview ../Segmentation/Contrast_raw_coreg_24.mif -tractography.load track_dDRTT_rh.tck -plane 1	;;
				  3) mrview ../Segmentation/Contrast_raw_coreg_24.mif -tractography.load track_CST_rh.tck  -plane 1;;
				  4) mrview ../Segmentation/Contrast_raw_coreg_24.mif -tractography.load track_ML_rh.tck -plane 1;;
				  5) mrview ../Segmentation/Contrast_raw_coreg_24.mif -tractography.load track_CST_rh.tck -tractography.load track_dDRTT_rh.tck -tractography.load track_ndDRTT_rh.tck -tractography.load track_ML_rh.tck -plane 1;;
				  esac 
			  fi
	 } 
	 
	 # 4. Visualização dos volumes  
	 handleVolumes() {
		echo "Deseja visualizar qual trato:"\
			  $'\n'"1.Non-Decussating Dentatorubrothalamic Tract (ndDRTT)"\
			  $'\n'"2.Decussating Dentatorubrothalamic Tract (dDRTT)"\
			  $'\n'"3.Corticospinal tract (CST)"\
			  $'\n'"4.Medial lemniscus (ML)"
			  read -p "Opção: " tract_volume
			  
			  if [[ "$hemisphere" == "left" ]]; then
				  case $tract_volume in
				  1) mrview track_ndDRTT_lh.nii.gz -overlay.load ../Segmentation/Contrast_raw_coreg_24.mif -overlay.opacity 0.5 -plane 2 ;;
				  2) mrview track_dDRTT_lh.nii.gz -overlay.load ../Segmentation/Contrast_raw_coreg_24.mif -overlay.opacity 0.5 -plane 2 ;;
				  3) mrview track_CST_lh.nii.gz -overlay.load ../Segmentation/Contrast_raw_coreg_24.mif -overlay.opacity 0.5 -plane 2 ;;
				  4) mrview track_ML_lh.nii.gz -overlay.load ../Segmentation/Contrast_raw_coreg_24.mif -overlay.opacity 0.5 -plane 2 ;;
				  esac 
				  
			  elif [[ "$hemisphere" == "right" ]]; then
				  case $tract_volume in
				  1) mrview track_ndDRTT_rh.nii.gz -overlay.load ../Segmentation/Contrast_raw_coreg_24.mif -overlay.opacity 0.5 -plane 2 ;;
				  2) mrview track_dDRTT_rh.nii.gz -overlay.load ../Segmentation/Contrast_raw_coreg_24.mif -overlay.opacity 0.5 -plane 2 ;;
				  3) mrview track_CST_rh.nii.gz -overlay.load ../Segmentation/Contrast_raw_coreg_24.mif -overlay.opacity 0.5 -plane 2 ;;
				  4) mrview track_ML_rh.nii.gz -overlay.load ../Segmentation/Contrast_raw_coreg_24.mif -overlay.opacity 0.5 -plane 2 ;;
				  esac 
			  fi
	 } 
	 
	 # 5. Visualização do plano AC/PC
	 handleCoregister() {
      echo "Qual das imagens deseja visualizar?:"\
      $'\n'"1.Imagem T1"\
      $'\n'"2.Imagem WMnull"
      read -p "Opção: " acpc_view
      
      case $acpc_view in
      1) mrview ACPC/T1_raw_LPS_3D.nii ;;
      2) mrview ACPC/Contrast_raw_coreg_24_up_ACPC_aligned.nii.gz ;;
      esac
    }
	 
	 # 6. Visualização dos contornos
	 handleContours() {
		 (
		 export FREESURFER_HOME="$FREESURFER_HOME_STAND"
         export SUBJECTS_DIR="$SUBJECTS_DIR"
         source "$FREESURFER_HOME/SetUpFreeSurfer.sh"
                  
		 echo "Deseja visualizar qual contorno?:"\
			  $'\n'"1.Axial"\
			  $'\n'"2.Coronal"
			  read -p "Opção: " contour_view
			  
			  if [[ "$hemisphere" == "left" ]]; then
				  case $contour_view in
				  1) freeview -v ACPC/Contrast_raw_coreg_24_up_ACPC_aligned.nii.gz \
					 -v Contour/acpc_contour_CST.nii.gz:colormap=LUT:lut="$ATLAS_DIR/LUT_tracks.txt" \
					 -v Contour/acpc_contour_ML.nii.gz:colormap=LUT:lut="$ATLAS_DIR/LUT_tracks.txt" \
					 -v Contour/acpc_contour_ndDRTT.nii.gz:colormap=LUT:lut="$ATLAS_DIR/LUT_tracks.txt" \
					 -v Contour/acpc_contour_dDRTT.nii.gz:colormap=LUT:lut="$ATLAS_DIR/LUT_tracks.txt" \
					 --viewport axial ;;
				  2) freeview -v ACPC/Contrast_raw_coreg_24_up_ACPC_aligned.nii.gz \
					 -v Contour/coronal_contour_CST.nii.gz:colormap=LUT:lut="$ATLAS_DIR/LUT_tracks.txt" \
					 -v Contour/coronal_contour_ML.nii.gz:colormap=LUT:lut="$ATLAS_DIR/LUT_tracks.txt" \
					 -v Contour/coronal_contour_ndDRTT.nii.gz:colormap=LUT:lut="$ATLAS_DIR/LUT_tracks.txt" \
					 -v Contour/coronal_contour_dDRTT.nii.gz:colormap=LUT:lut="$ATLAS_DIR/LUT_tracks.txt" \
					 --viewport coronal ;;
				  esac 
				  
			  elif [[ "$hemisphere" == "right" ]]; then
				  case $contour_view in
				  1) freeview -v ACPC/Contrast_raw_coreg_24_up_ACPC_aligned.nii.gz \
					 -v Contour/acpc_contour_CST.nii.gz:colormap=LUT:lut="$ATLAS_DIR/LUT_tracks.txt" \
					 -v Contour/acpc_contour_ML.nii.gz:colormap=LUT:lut="$ATLAS_DIR/LUT_tracks.txt" \
					 -v Contour/acpc_contour_ndDRTT.nii.gz:colormap=LUT:lut="$ATLAS_DIR/LUT_tracks.txt" \
					 -v Contour/acpc_contour_dDRTT.nii.gz:colormap=LUT:lut="$ATLAS_DIR/LUT_tracks.txt" \
					 --viewport axial ;;
				  2) freeview -v ACPC/Contrast_raw_coreg_24_up_ACPC_aligned.nii.gz \
					 -v Contour/coronal_contour_CST.nii.gz:colormap=LUT:lut="$ATLAS_DIR/LUT_tracks.txt" \
					 -v Contour/coronal_contour_ML.nii.gz:colormap=LUT:lut="$ATLAS_DIR/LUT_tracks.txt" \
					 -v Contour/coronal_contour_ndDRTT.nii.gz:colormap=LUT:lut="$ATLAS_DIR/LUT_tracks.txt" \
					 -v Contour/coronal_contour_dDRTT.nii.gz:colormap=LUT:lut="$ATLAS_DIR/LUT_tracks.txt" \
					 --viewport coronal ;;
				  esac 
			  fi
		 )
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
      cd "Raw/"
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
      cd "Preprocess/"
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
      export FREESURFER_HOME="$FREESURFER_HOME_STAND"
      export SUBJECTS_DIR="$SUBJECTS_DIR"
      source "$FREESURFER_HOME/SetUpFreeSurfer.sh"
      
      cd "Segmentation/"
      
      while [ $FLAG_CONTINUE -eq 1 ]; do    
          echo "Deseja visualizar a imagem de qual dos processos:"\
          $'\n'"1.Imagem T2 processada pelo freesurfer"\
          $'\n'"2.Segmentação do atlas Nextbrain"\
          $'\n'"3.Visualização dos mapas de difusão"\
          $'\n'"4.Visualização 3D da segmentação cortical (Julich atlas)"
                   			
          read -p "Opção: " segmentation
          
            case $segmentation in
            1) handleT2freesurfer;;
            2) handleNextbrain;;
            3) handleMaps;;
            4) handleAnnot;;
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
      cd "Tractography/"
      hemisphere=$(< ../Segmentation/hemisphere.txt)
      while [ $FLAG_CONTINUE -eq 1 ]; do    
          echo "Deseja visualizar a imagem de qual dos processos:"\
          $'\n'"1.Response function and Fiber orientation distribution (FOD)"\
          $'\n'"2.Mask GM/WM"\
          $'\n'"3.Streamlines"\
          $'\n'"4.Streamlines' volume"\
          $'\n'"5.AC/PC plane"\
          $'\n'"6.Streamlines' contour"
          read -p "Opção: " tract
          
            case $tract in
            1) handleRF;;
            2) handleROI;;
            3) handleTracks;;
            4) handleVolumes;;
            5) handleAcpcView;;
            6) handleContours;;
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
