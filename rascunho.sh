BASE_DIR="/home/brunobastos/Mestrado/Dados"
SCRIPT_DIR="/home/brunobastos/Mestrado/Scripts"
SUBJECTS_DIR="$BASE_DIR/fs_subjects"
ATLAS_DIR="$BASE_DIR/Atlas" 
TESTE_DIR="$BASE_DIR/Teste"
PAT_DIR="$BASE_DIR/Pat547/Pat547_PRE/Output_tract"

 
dDRTT_labels=(219 220 221 252 222 283 314 350 381 382)
		  
cmd_lh="mrcalc"
cmd_rh="mrcalc"

# Primeiro termo (sem -or)
first=1
for label in "${dDRTT_labels[@]}"; do
  if [ $first -eq 1 ]; then
	  cmd_lh="$cmd_lh seg_left_resampled.nii.gz $label -eq"
	  cmd_rh="$cmd_rh seg_right_resampled.nii.gz $label -eq"
	  first=0
  else
	  cmd_lh="$cmd_lh seg_left_resampled.nii.gz $label -eq -or"
	  cmd_rh="$cmd_rh seg_right_resampled.nii.gz $label -eq -or"
  fi
done

# Adiciona a saída e força bit
cmd_lh="$cmd_lh dDRTT_nucleus_lh.nii.gz -datatype bit -force"
cmd_rh="$cmd_rh dDRTT_nucleus_rh.nii.gz -datatype bit -force"

# Mostra e executa
echo "Executando: $cmd_lh"
eval "$cmd_lh"
echo "Executando: $cmd_rh"
eval "$cmd_rh"

ndDRTT_labels=(224 225 253 284 285 286 303 312 313 379 380 396 397 398 441 454 478 479 508 517 519 578 811 813)
		  
cmd_lh="mrcalc"
cmd_rh="mrcalc"

# Primeiro termo (sem -or)
first=1
for label in "${ndDRTT_labels[@]}"; do
  if [ $first -eq 1 ]; then
	  cmd_lh="$cmd_lh seg_left_resampled.nii.gz $label -eq"
	  cmd_rh="$cmd_rh seg_right_resampled.nii.gz $label -eq"
	  first=0
  else
	  cmd_lh="$cmd_lh seg_left_resampled.nii.gz $label -eq -or"
	  cmd_rh="$cmd_rh seg_right_resampled.nii.gz $label -eq -or"
  fi
done

# Adiciona a saída e força bit
cmd_lh="$cmd_lh ndDRTT_nucleus_lh.nii.gz -datatype bit -force"
cmd_rh="$cmd_rh ndDRTT_nucleus_rh.nii.gz -datatype bit -force"

# Mostra e executa
echo "Executando: $cmd_lh"
eval "$cmd_lh"
echo "Executando: $cmd_rh"
eval "$cmd_rh"


