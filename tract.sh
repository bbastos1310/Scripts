    # Files 
    FILE_1="wmfod.mif"
    FILE_2="gmwmSeed_coreg.mif"    
    FILE_3="ROIs/intersect_seed_rh.mif"
    FILE_4A="track_ndDRTT_lh.tck"
    FILE_4B="track_DRTT_lh.tck"
    FILE_4C="track_CST_lh.tck"
    FILE_4D="track_ML_lh.tck"
    FILE_5="track_ML_lh.nii.gz"
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
      handleFunction() {
        if [ $EXIST -eq 1 ]; then
          dwi2response dhollander ../Preprocess/dwi_den_unr_preproc_unb_reg.mif wm.txt gm.txt csf.txt -voxels voxels.mif -mask ../Preprocess/dwi_mask_up_reg.mif -force
          time ss3t_csd_beta1 ../Preprocess/dwi_den_unr_preproc_unb_reg.mif wm.txt wmfod.mif gm.txt gmfod.mif csf.txt csffod.mif -mask ../Preprocess/dwi_mask_up_reg.mif -force
          mrconvert -coord 3 0 wmfod.mif - | mrcat csffod.mif gmfod.mif - vf.mif -force
          mtnormalise wmfod.mif wmfod_norm.mif gmfod.mif gmfod_norm.mif csffod.mif csffod_norm.mif -mask ../Preprocess/dwi_mask_up_reg.mif -force
        else
          exit
        fi
      }

          
    # 2.Mask between GM and WM
    handleFringe() {
      if [ $EXIST -eq 1 ]; then
      	5ttgen freesurfer "$SUBJECTS_DIR/$PAT_NUM/mri/aparc+aseg.mgz" 5tt_coreg.mif -force
        5tt2gmwmi 5tt_coreg.mif gmwmSeed_coreg.mif -force
      else
        exit
      fi
    }
	
	# 3.ROI extraction
	handleRoiextraction() {
      if [ $EXIST -eq 1 ]; then
		mkdir -p ROIs
		mrgrid gmwmSeed_coreg.mif regrid -template ../Segmentation/T1_upsampled.nii.gz gmwmSeed_coreg_subcortical.mif -interp linear -force
		mrgrid gmwmSeed_coreg.mif regrid -template ../Segmentation/cortical_Julich.nii.gz gmwmSeed_coreg_cortical.mif -interp linear -force
		mrgrid gmwmSeed_coreg.mif regrid -template ../Segmentation/T1_upsampled.nii.gz gmwmSeed_coreg_resampled.mif -interp linear -force
		
		# Left hemisphere
		mrcalc ../Segmentation/ROIs_tracks.nii.gz 1001 -eq ROIs/ROI_ML_lh.mif -datatype uint8 -force
		mrcalc ../Segmentation/ROIs_tracks.nii.gz 1002 -eq ROIs/ROI_CP_lh.mif -datatype uint8 -force
		mrcalc ../Segmentation/ROIs_tracks.nii.gz 1005 -eq ROIs/ROI_DN_lh.mif -datatype uint8 -force
		mrcalc ../Segmentation/ROIs_tracks.nii.gz 1006 -eq ROIs/ROI_PSA_lh.mif -datatype uint8 -force
		mrcalc ../Segmentation/ROIs_tracks.nii.gz 1007 -eq ROIs/ROI_STN_lh.mif -datatype uint8 -force
		mrcalc ../Segmentation/ROIs_tracks.nii.gz 1008 -eq ROIs/ROI_PL_lh.mif -datatype uint8 -force
		mrcalc ../Segmentation/ROIs_tracks.nii.gz 1009 -eq ROIs/ROI_BS_lh.mif -datatype uint8 -force
				
		mrcalc ../Segmentation/cortical_Julich.nii.gz 2047 -eq ../Segmentation/cortical_Julich.nii.gz 2048 -eq -or \
	    ../Segmentation/cortical_Julich.nii.gz 2086 -eq -or ../Segmentation/cortical_Julich.nii.gz 2087 -eq -or \
	    ../Segmentation/cortical_Julich.nii.gz 2116 -eq -or ../Segmentation/cortical_Julich.nii.gz 2117 -eq -or ../Segmentation/cortical_Julich.nii.gz 2118 -eq -or \
	    ../Segmentation/cortical_Julich.nii.gz 2146 -eq -or \
	    ROIs/ROI_PreCG_lh.mif \
	    -datatype uint8 -force  #Pre central gyrus regions 
	    
	    mrcalc ../Segmentation/cortical_Julich.nii.gz 2047 -eq ../Segmentation/cortical_Julich.nii.gz 2048 -eq -or ROIs/ROI_PMC_lh.mif -force  #Primary motor cortex (4a e 4p)
	    
	    mrcalc ../Segmentation/cortical_Julich.nii.gz 2049 -eq ../Segmentation/cortical_Julich.nii.gz 2050 -eq -or \
	    ../Segmentation/cortical_Julich.nii.gz 2051 -eq -or ../Segmentation/cortical_Julich.nii.gz 2081 -eq -or \
	    ROIs/ROI_PostCG_PostCS_lh.mif \
	    -datatype uint8 -force   # Somatosensorial region (Post central gyrus + Post CS )
		
		mrcalc ../Segmentation/wm_nextbrain.nii.gz 1010 -eq ROIs/ROI_WMf_lh.mif -datatype uint8 -force
		mrcalc ../Segmentation/wm_nextbrain.nii.gz 1011 -eq ROIs/ROI_WMh_lh.mif -datatype uint8 -force
		mrcalc ../Segmentation/wm_nextbrain.nii.gz 1012 -eq ROIs/ROI_WMc_lh.mif -datatype uint8 -force
		
		mrcalc ../Segmentation/subcortical_nextbrain.nii.gz 119 -eq ../Segmentation/subcortical_nextbrain.nii.gz 206 -eq -or ROIs/ROI_GP_lh.mif -force
		
		mrconvert ../Segmentation/thalamus_mask_lh.nii.gz ROIs/ROI_thalamus_lh.mif -datatype uint8 -force
		mrcalc gmwmSeed_coreg_resampled.mif ROIs/ROI_DN_lh.mif -mult ROIs/intersect_seed_DN_lh.mif -force
		#mrcalc gmwmSeed_coreg_cortical.mif ROIs/ROI_PreCG_lh.mif -mult ROIs/intersect_seed_DRTT_lh.mif -force
		mrcalc gmwmSeed_coreg_cortical.mif ROIs/ROI_PMC_lh.mif -mult ROIs/intersect_seed_CST_lh.mif -force
		mrcalc gmwmSeed_coreg_cortical.mif ROIs/ROI_PostCG_PostCS_lh.mif -mult ROIs/intersect_seed_ML_lh.mif -force
		#mrcalc gmwmSeed_coreg_resampled.mif ROIs/ROI_WMc_rh.mif -mult ROIs/intersect_seed_DRTT_lh_teste.mif -force
		
		# Right hemisphere
		mrcalc ../Segmentation/ROIs_tracks.nii.gz 2001 -eq ROIs/ROI_ML_rh.mif -datatype uint8 -force
		mrcalc ../Segmentation/ROIs_tracks.nii.gz 2002 -eq ROIs/ROI_CP_rh.mif -datatype uint8 -force
		mrcalc ../Segmentation/ROIs_tracks.nii.gz 2005 -eq ROIs/ROI_DN_rh.mif -datatype uint8 -force
		mrcalc ../Segmentation/ROIs_tracks.nii.gz 2006 -eq ROIs/ROI_PSA_rh.mif -datatype uint8 -force
		mrcalc ../Segmentation/ROIs_tracks.nii.gz 2007 -eq ROIs/ROI_STN_rh.mif -datatype uint8 -force
		mrcalc ../Segmentation/ROIs_tracks.nii.gz 2008 -eq ROIs/ROI_PL_rh.mif -datatype uint8 -force
		mrcalc ../Segmentation/ROIs_tracks.nii.gz 2009 -eq ROIs/ROI_BS_rh.mif -datatype uint8 -force
				
		mrcalc ../Segmentation/cortical_Julich.nii.gz 3047 -eq ../Segmentation/cortical_Julich.nii.gz 3048 -eq -or \
	    ../Segmentation/cortical_Julich.nii.gz 3086 -eq -or ../Segmentation/cortical_Julich.nii.gz 3087 -eq -or \
	    ../Segmentation/cortical_Julich.nii.gz 3116 -eq -or ../Segmentation/cortical_Julich.nii.gz 3117 -eq -or ../Segmentation/cortical_Julich.nii.gz 3118 -eq -or \
	    ../Segmentation/cortical_Julich.nii.gz 3146 -eq -or \
	    ROIs/ROI_PreCG_rh.mif \
	    -datatype uint8 -force  #Pre central gyrus regions 
	    
	    mrcalc ../Segmentation/cortical_Julich.nii.gz 3047 -eq ../Segmentation/cortical_Julich.nii.gz 3048 -eq -or ROIs/ROI_PMC_rh.mif -force  #Primary motor cortex (4a e 4p)
	    
	    mrcalc ../Segmentation/cortical_Julich.nii.gz 3049 -eq ../Segmentation/cortical_Julich.nii.gz 3050 -eq -or \
	    ../Segmentation/cortical_Julich.nii.gz 3051 -eq -or ../Segmentation/cortical_Julich.nii.gz 3081 -eq -or \
	    ROIs/ROI_PostCG_PostCS_rh.mif \
	    -datatype uint8 -force   # Somatosensorial region (Post central gyrus + Post CS )
		
		mrcalc ../Segmentation/wm_nextbrain.nii.gz 2010 -eq ROIs/ROI_WMf_rh.mif -datatype uint8 -force
		mrcalc ../Segmentation/wm_nextbrain.nii.gz 2011 -eq ROIs/ROI_WMh_rh.mif -datatype uint8 -force
		mrcalc ../Segmentation/wm_nextbrain.nii.gz 2012 -eq ROIs/ROI_WMc_rh.mif -datatype uint8 -force
		
		mrcalc ../Segmentation/subcortical_nextbrain.nii.gz 1119 -eq ../Segmentation/subcortical_nextbrain.nii.gz 1206 -eq -or ROIs/ROI_GP_rh.mif -force
		#mrcalc ../Segmentation/subcortical_nextbrain.nii.gz 1048 -eq ROIs/ROI_caudate_rh.mif -force
		
		mrconvert ../Segmentation/thalamus_mask_rh.nii.gz ROIs/ROI_thalamus_rh.mif -datatype uint8 -force
		mrcalc gmwmSeed_coreg_resampled.mif ROIs/ROI_DN_rh.mif -mult ROIs/intersect_seed_DN_rh.mif -force
		#mrcalc gmwmSeed_coreg_cortical.mif ROIs/ROI_PreCG_rh.mif -mult ROIs/intersect_seed_PreCG_rh.mif -force
		mrcalc gmwmSeed_coreg_cortical.mif ROIs/ROI_PMC_rh.mif -mult ROIs/intersect_seed_CST_rh.mif -force
		mrcalc gmwmSeed_coreg_cortical.mif ROIs/ROI_PostCG_PostCS_rh.mif -mult ROIs/intersect_seed_ML_rh.mif -force
		#mrcalc gmwmSeed_coreg_resampled.mif ROIs/ROI_WMc_rh.mif -mult ROIs/intersect_seed_cerebellum_rh.mif -force
					
      else
        exit
      fi
    }
    
	# 4A.Tract ndDRTT
	handleTractndDRTT() {
      if [ $EXIST -eq 1 ]; then
		if [[ "$hemisphere" == "left" ]]; then		
			tckgen  \
				-act 5tt_coreg.mif \
				-backtrack \
				-seed_gmwmi ROIs/intersect_seed_DN_lh.mif \
				-select 1100 \
				-seeds 50M \
				-include ROIs/ROI_PSA_lh.mif \
				-include ROIs/ROI_PreCG_lh.mif \
				-exclude ROIs/ROI_WMf_rh.mif \
				-exclude ROIs/ROI_WMh_rh.mif \
				-exclude ROIs/ROI_WMc_rh.mif \
				-minlength 40 \
				-angle 30 \
				-cutoff 0.1 \
				-seed_unidirectional \
				-samples 2 \
				wmfod_norm.mif track_ndDRTT_lh_teste.tck \
				-force
				
		elif [[ "$hemisphere" == "right" ]]; then
			tckgen  \
				-act 5tt_coreg.mif \
				-backtrack \
				-seed_gmwmi ROIs/intersect_seed_DN_rh.mif \
				-select 50 \
				-seeds 50M \
				-include ROIs/ROI_PSA_rh.mif \
				-include ROIs/ROI_PreCG_rh.mif \
				-exclude ROIs/ROI_WMf_lh.mif \
				-exclude ROIs/ROI_WMh_lh.mif \
				-exclude ROIs/ROI_WMc_lh.mif \
				-minlength 70 \
				-angle 30 \
				-cutoff 0.1 \
				-step 1 \
				-trials 5000 \
				-max_attempts_per_seed 5000 \
				-seed_unidirectional \
				-samples 2 \
				wmfod_norm.mif track_ndDRTT_rh.tck \
				-force
		else
			echo hemisfério não definido
			exit	
		fi			
      else
        exit
      fi
    }
    
    # 4B.Tract DRTT
	handleTractDRTT() {
      if [ $EXIST -eq 1 ]; then
		echo a
		#if [[ "$hemisphere" == "left" ]]; then				
			#time tckgen  \
				#-act 5tt_coreg.mif \
				#-backtrack \
				#-seed_gmwmi ROIs/ROI_WMc_rh.mif \
				#-select 10 \
				#-seeds 100M \
				#-include ROIs/ROI_PSA_lh.mif \
				#-include ROIs/ROI_PreCG_lh.mif \
				#-exclude ROIs/ROI_WMf_rh.mif \
				#-exclude ROIs/ROI_WMh_lh.mif \
				#-exclude ROIs/ROI_WMc_lh.mif \
				#-exclude ROIs/ROI_GP_lh.mif \
				#-minlength 100 \
				#-angle 20 \
				#-cutoff 0.1 \
				#-step 1 \
				#-trials 5000 \
				#-max_attempts_per_seed 5000 \
				#-seed_unidirectional \
				#-samples 4 \
				#wmfod_norm.mif track_DRTT_lh_teste2.tck \
				#-force
		#elif [[ "$hemisphere" == "right" ]]; then
			#time tckgen  \
				#-act 5tt_coreg.mif \
				#-backtrack \
				#-seed_gmwmi ROIs/ROI_WMc_lh.mif \
				#-select 10 \
				#-seeds 100M \
				#-include ROIs/ROI_PSA_rh.mif \
				#-include ROIs/ROI_PreCG_rh.mif \
				#-exclude ROIs/ROI_WMf_lh.mif \
				#-exclude ROIs/ROI_WMh_rh.mif \
				#-exclude ROIs/ROI_WMc_rh.mif \
				#-exclude ROIs/ROI_GP_rh.mif \
				#-minlength 100 \
				#-angle 20 \
				#-cutoff 0.1 \
				#-step 1 \
				#-trials 5000 \
				#-max_attempts_per_seed 5000 \
				#-seed_unidirectional \
				#-samples 4 \
				#wmfod_norm.mif track_DRTT_rh.tck \
				#-force
      else
        exit
      fi
    }
    
    # 4C.Tract CST
	handleTractCST() {
      if [ $EXIST -eq 1 ]; then
				
		tckgen  \
			-act 5tt_coreg.mif \
			-backtrack \
			-seed_gmwmi ROIs/intersect_seed_CST_lh.mif \
			-select 10500 \
			-seeds 50M \
			-include ROIs/ROI_CP_lh.mif \
			-include ROIs/ROI_PL_lh.mif \
			-exclude ROIs/ROI_WMf_rh.mif \
			-exclude ROIs/ROI_WMh_rh.mif \
			-exclude ROIs/ROI_WMc_rh.mif \
			-exclude ROIs/ROI_WMc_lh.mif \
			-minlength 90 \
			-angle 20 \
			-cutoff 0.2 \
			-step 1 \
			-seed_unidirectional \
			-samples 2 \
			wmfod_norm.mif track_CST_lh.tck \
			-force
				
      else
        exit
      fi
    }
    
    # 4D.Tract ML
	handleTractML() {
      if [ $EXIST -eq 1 ]; then
				
		time tckgen  \
			-act 5tt_coreg.mif \
			-backtrack \
			-seed_gmwmi ROIs/intersect_seed_ML_lh.mif \
			-select 20 \
			-seeds 100M \
			-include ROIs/ROI_ML_lh.mif \
			-include ROIs/ROI_PL_lh.mif \
			-include ROIs/ROI_BS_lh.mif \
			-exclude ROIs/ROI_WMf_rh.mif \
			-exclude ROIs/ROI_WMh_rh.mif \
			-exclude ROIs/ROI_WMc_rh.mif \
			-exclude ROIs/ROI_WMc_lh.mif \
			-exclude ROIs/ROI_BS_rh.mif \
			-minlength 40 \
			-angle 20 \
			-cutoff 0.1 \
			-step 1 \
			-seed_unidirectional \
			-samples 2 \
			wmfod_norm.mif track_ML_lh_teste.tck \
			-force
				
      else
        exit
      fi
    }
    
    # 5.Streamlines' filter
    handleStreamlinesfilter() {
      if [ $EXIST -eq 1 ]; then
        python "$SCRIPT_DIR/Python/streamline_filter.py"
      else
        exit
      fi
    }
    
    # 6.Statistics
    handleStatistics() {
      if [ $EXIST -eq 1 ]; then
		mkdir -p Contour
		mrgrid ../Segmentation/mask_lesion_float.nii.gz regrid -template ../Segmentation/T1_upsampled.nii.gz mask_lesion_float_up.nii.gz -interp linear -force
		mrgrid ../Segmentation/Contrast_raw_coreg_24.nii.gz regrid -template ../Segmentation/T1_upsampled.nii.gz Contrast_raw_coreg_24_up.nii.gz -force
		
		#AC-PC plan
		mkdir -p ACPC
		mrconvert ../Segmentation/T1_upsampled.nii.gz -datatype uint16 T1_raw.nii -force
		export ARTHOME=/home/brunobastos/Downloads/acpc
		export PATH=$ARTHOME/bin:$PATH
		acpcdetect -i T1_raw.nii -output-orient LPS -v
		rm T1_raw.mrx T1_raw_ACPC_axial.png T1_raw_ACPC_sagittal.png T1_raw_orion.png T1_raw_orion.txt T1_raw_orion_PIL.txt
		mv T1_raw_* ACPC/
		flirt -in Contrast_raw_coreg_24_up.nii.gz -applyxfm -init ACPC/T1_raw_FSL.mat -ref Contrast_raw_coreg_24_up.nii.gz -out ACPC/Contrast_raw_coreg_24_up_ACPC.nii.gz
		flirt -in mask_lesion_float_up.nii.gz -applyxfm -init ACPC/T1_raw_FSL.mat -ref mask_lesion_float_up.nii.gz -out ACPC/mask_lesion_float_up_ACPC.nii.gz
		flirt -in track_ndDRTT_lh.nii.gz -applyxfm -init ACPC/T1_raw_FSL.mat -ref track_ndDRTT_lh.nii.gz -interp nearestneighbour -out ACPC/track_ndDRTT_lh_ACPC.nii.gz
		flirt -in track_DRTT_lh.nii.gz -applyxfm -init ACPC/T1_raw_FSL.mat -ref track_DRTT_lh.nii.gz -interp nearestneighbour -out ACPC/track_DRTT_lh_ACPC.nii.gz
		flirt -in track_CST_lh.nii.gz -applyxfm -init ACPC/T1_raw_FSL.mat -ref track_CST_lh.nii.gz -interp nearestneighbour -out ACPC/track_CST_lh_ACPC.nii.gz
		flirt -in track_ML_lh.nii.gz -applyxfm -init ACPC/T1_raw_FSL.mat -ref track_ML_lh.nii.gz -interp nearestneighbour -out ACPC/track_ML_lh_ACPC.nii.gz
		#fslswapdim teste.nii.gz -x y z teste_corrigido.nii.gz
						
        python "$SCRIPT_DIR/Python/results.py"
      else
        exit
      fi
    }
    
    # 7.Streamlines creation
    handleStreamlines() {
      if [ $EXIST -eq 1 ]; then
        time tckgen -act 5tt_coreg.mif -backtrack -seed_gmwmi gmwmSeed_coreg.mif -select 10000000 wmfod_norm.mif tracks_10mio.tck -force
        tckedit tracks_10mio.tck -number 200k smallerTracks_200k.tck -force
      else
        exit
      fi
    }

    # 7.SIFT (Streamlines filtering)
    handleSift() {
      if [ $EXIST -eq 1 ]; then
        time tcksift2 -act 5tt_coreg.mif -out_mu sift_mu.txt -out_coeffs sift_coeffs.txt -nthreads 4 tracks_10mio.tck wmfod_norm.mif sift_weights.txt -force
      else
        exit
      fi
    }

    # MAIN FUNCTION
      
      cd "$OUT_PRE/Tractography"
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
          $'\n'"1.Response function and Fiber orientation distribution"\
          $'\n'"2.Mask GM/WM"\
          $'\n'"3.ROIs extraction"\
          $'\n'"4.Tract estimation"\
          $'\n'"5.Streamlines filter"\
          $'\n'"6.Creation of streamlines for connectivity matrix (Optional)"\
          $'\n'"7.Streamlines filtering (Optional)"
          read -p "Opção: " step
          
            case $step in
            1)
            FILE=$FILE_1
            fileExistence
            handleFunction;;
          
            2)
            FILE=$FILE_2
            fileExistence
            handleFringe;;          
          
            3)
            FILE=$FILE_3
            fileExistence
            handleRoiextraction;;
          
            4)
            hemisphere=$(< "../Segmentation/hemisphere.txt")		       
			echo "Deseja criar uma estimativa de qual trato?"\
			$'\n'"1.ndDRTT (non-decussating dentato-rubro-thalamic tract)"\
			$'\n'"2.dDRTT (decussating dentato-rubro-thalamic tract)"\
			$'\n'"3.CST (corticospinal tract)"\
			$'\n'"4.ML (medial lemniscus tract)"
			read -p "Opção: " tract
		  
			  case $tract in
			  1)
			  FILE=$FILE_4A
			  fileExistence
			  handleTractndDRTT;;
			  
			  2) 
			  FILE=$FILE_4B
              fileExistence
			  handleTractdDRTT;;
			  
			  3) 
			  FILE=$FILE_4C
              fileExistence
			  handleCST;;
			  
			  4) 
			  FILE=$FILE_4D
              fileExistence
			  handleML;;
			  
			  esac  
            ;;
			
			5)
            FILE=$FILE_5
            fileExistence
            handleStreamlinesfilter;;
            
            6)
            FILE=$FILE_6
            fileExistence
            handleStreamlines;;
            
            7)
            FILE=$FILE_7
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
    
