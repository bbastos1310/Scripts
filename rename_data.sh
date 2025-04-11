     
     
      if [[ -d "$PAT_DIR_PRE" && ! -d "$OUT_PRE" ]]; then
          cd "$PAT_DIR_PRE"
          # Directory creation for output
          mkdir -p Output_tract/{Raw,Preprocess,Segmentation,Tractography,Analysis}
          mkdir Output_general

          # For each component in the base directory, verify if it is a folder to rename the files inside
          for dir in "$PAT_DIR_PRE"/*/; do
            if [[ -d $dir && "$dir" != "$PAT_DIR_PRE/Output_tract/" && "$dir" != "$PAT_DIR_PRE/Output_general/" ]]; then
              cd $dir
              echo "Replacing . for _ and rename to .dcm: $dir"
              # Rename each file in each directory
              for FILENAME in *; do
                if [[ "$FILENAME" != *"dcm"* ]]; then
                  mv "$FILENAME" "${FILENAME//./_}.dcm";
                fi
              done
              
              size=$(mrinfo "$dir"/I_001.dcm -size)
              size_x=$(echo $size | awk '{print $1}')
              size_y=$(echo $size | awk '{print $2}')           
              size_z=$(echo $size | awk '{print $3}')
              # Verify the name folder to create a MIF file  (Folder 12: dwi, folder 9: T1)
              if [ "$dir" == "$PAT_DIR_PRE/012/" ]; then
              mrcat I_*.dcm ../Output_tract/Raw/dwi_raw.mif -force
              elif [ "$dir" == "$PAT_DIR_PRE/009/" ]; then
              mrconvert ../009/ ../Output_tract/Raw/T1_raw.mif -force
              elif [ "$dir" == "$PAT_DIR_PRE/007/" ]; then
              mrconvert ../007/ ../Output_tract/Raw/T2_raw.mif -force
              elif [ "$dir" == "$PAT_DIR_PRE/021/" ]; then
              mrconvert ../021/ ../Output_tract/Raw/Contrast_raw.mif -force
              elif [ "$size_x" -eq 1 ] || [ "$size_y" -eq 1 ] || [ "$size_z" -eq 1 ] ; then
              mrconvert "$dir" ../Output_general/${PWD##*/}_raw.mif -force
              else
              mrcat I_*.dcm ../Output_general/${PWD##*/}_raw.mif -force
              fi
            fi
          done
          if [[ -d "$OUT_PRE" && -d "$OUT_24" ]]; then
            cp "$OUT_PRE/T1_raw.mif" "$OUT_24"
          fi
      fi
      
      if [[ -d "$PAT_DIR_24" && ! -d "$OUT_24" ]]; then
          cd "$PAT_DIR_24"
          # Directory creation for output
          mkdir -p Output_tract/{Raw,Preprocess,Segmentation,Tractography,Analysis}
          mkdir Output_general

          # For each component in the base directory, verify if it is a folder to rename the files inside
          for dir in "$PAT_DIR_24"/*/; do
            if [[ -d $dir && "$dir" != "$PAT_DIR_24/Output_tract/" && "$dir" != "$PAT_DIR_24/Output_general/" ]]; then
              cd $dir
              echo "Replacing . for _ and rename to .dcm: $dir"
              # Rename each file in each directory
              for FILENAME in *; do
                if [[ "$FILENAME" != *"dcm"* ]]; then
                  mv "$FILENAME" "${FILENAME//./_}.dcm";
                fi
              done
              
              size=$(mrinfo "$dir"/I_001.dcm -size)
              size_x=$(echo $size | awk '{print $1}')
              size_y=$(echo $size | awk '{print $2}')           
              size_z=$(echo $size | awk '{print $3}')
              # Verify the name folder to create a MIF file  (Folder 12: dwi, folder 9: T1)
              if [ "$dir" == "$PAT_DIR_24/012/" ]; then
              mrcat I_*.dcm ../Output_tract/Raw/dwi_raw.mif -force
              elif [ "$dir" == "$PAT_DIR_24/009/" ]; then
              mrconvert ../009/ ../Output_tract/Raw/T1_raw_24.mif -force
              elif [ "$dir" == "$PAT_DIR_24/007/" ]; then
              mrconvert ../007/ ../Output_tract/Raw/T2_raw.mif -force
              elif [ "$dir" == "$PAT_DIR_PRE/021/" ]; then
              mrconvert ../021/ ../Output_tract/Raw/Contrast_raw.mif -force
              elif [ "$size_x" -eq 1 ] || [ "$size_y" -eq 1 ] || [ "$size_z" -eq 1 ] ; then
              mrconvert "$dir" ../Output_general/${PWD##*/}_raw.mif -force
              else
              mrcat I_*.dcm ../Output_general/${PWD##*/}_raw.mif -force
              fi
            fi
          done
          if [[ -d "$OUT_PRE" && -d "$OUT_24" ]]; then
            cp "$OUT_PRE/T1_raw.mif" "$OUT_24"
          fi
      fi
      
      if [[ -d "$OUT_PRE" && -d "$OUT_24" ]]; then
        echo "Data treatment concluded"
      fi
       

