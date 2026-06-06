
if [[ -d "$PAT_DIR_PRE" && ! -d "$OUT_PRE" ]]; then
	cd "$PAT_DIR_PRE"
	# Directory creation for output
	mkdir -p Output_tract/{Raw,Preprocess,Segmentation,Tractography,Analysis}
	  
	for dir in "$PAT_DIR_PRE"/*/; do
		if [[ -d $dir && $dir != "$PAT_DIR_PRE/Output_tract/" ]]; then
			echo $dir
			cd $dir
			for FILENAME in *; do
				if [[ "$FILENAME" != *"dcm"* ]]; then
					mv "$FILENAME" "${FILENAME//./_}.dcm";
				fi
			done
			image_PRE=$(python $SCRIPT_DIR/Python/rename.py)
			
			case $image_PRE in
			
			T1)
			echo $image_PRE
			mrconvert $dir "$OUT_PRE/Raw/T1_raw.mif" -force ;;
			
			T2)
			echo $image_PRE
			mrconvert $dir "$OUT_PRE/Raw/T2_raw.mif" -force 
			mrconvert "$OUT_PRE/Raw/T2_raw.mif" "$OUT_PRE/Segmentation/T2_raw.nii.gz" -force ;;
			
			DWI_PA)
			echo $image_PRE
			mrconvert $dir "$OUT_PRE/Raw/dwi_PA_raw.mif" -force ;;
			
			DWI)
			echo $image_PRE
			mrcat I_*.dcm "$OUT_PRE/Raw/dwi_raw.mif" -force ;;
			
			WMNULL)
			echo $image_PRE
			mrconvert $dir "$OUT_PRE/Raw/Contrast_raw.mif" -force 
			mrconvert "$OUT_PRE/Raw/Contrast_raw.mif" "$OUT_PRE/Segmentation/Contrast_raw.nii.gz" -force ;;
			
			esac
		fi
	done
fi

if [[ -d "$PAT_DIR_24" && ! -d "$OUT_24" ]]; then
	cd "$PAT_DIR_24"
	# Directory creation for output
	mkdir -p Output_tract/{Raw,Preprocess,Segmentation,Tractography,Analysis}
	  
	for dir in "$PAT_DIR_24"/*/; do
			if [[ -d $dir && $dir != "$PAT_DIR_24/Output_tract/" ]]; then
			echo $dir
			cd $dir
			for FILENAME in *; do
				if [[ "$FILENAME" != *"dcm"* ]]; then
					mv "$FILENAME" "${FILENAME//./_}.dcm";
				fi
			done
			image_24=$(python $SCRIPT_DIR/Python/rename.py)
			
			case $image_24 in
			
			T1)
			echo $image_24
			mrconvert $dir "$OUT_24/Raw/T1_raw.mif" -force ;;
			
			T2)
			echo $image_24
			mrconvert $dir "$OUT_24/Raw/T2_raw.mif" -force 
			mrconvert "$OUT_24/Raw/T2_raw.mif" "$OUT_24/Segmentation/T2_raw.nii.gz" -force ;;
			
			DWI_PA)
			echo $image_24
			mrconvert $dir "$OUT_24/Raw/dwi_PA_raw.mif" -force ;;
			
			DWI)
			echo $image_24
			mrcat I_*.dcm "$OUT_24/Raw/dwi_raw.mif" -force ;;
			
			WMNULL)
			echo $image_24
			mrconvert $dir "$OUT_24/Raw/Contrast_raw.mif" -force 
			mrconvert "$OUT_24/Raw/Contrast_raw.mif" "$OUT_24/Segmentation/Contrast_raw.nii.gz" -force ;;
			
			esac
			fi
		
	if [[ -d "$OUT_PRE" && -d "$OUT_24" ]]; then
		cp "$OUT_PRE/Raw/T1_raw.mif" "$OUT_24"
	fi
	done
fi

for file in $FILE_RAW_1 $FILE_RAW_2 $FILE_RAW_3 $FILE_RAW_4 $FILE_RAW_5 $FILE_RAW_6 $FILE_RAW_7 $FILE_RAW_8 $FILE_RAW_9 $FILE_RAW_10; do
	FILE=$file
	if [[ -a $FILE ]]; then
		FLAG_RAW=$(($FLAG_RAW-1))
	else 
		echo "$file not found."	
	fi       
done 

if [ $FLAG_RAW -ne 0 ]; then
	echo "Please check the image files. The folder currently configured is missing $FLAG_RAW .mif files."
	exit
fi

if [[ -d "$OUT_PRE" && -d "$OUT_24" ]]; then
	echo "Data treatment concluded"
fi
