BASE_DIR="/home/brunobastos/Mestrado/Dados"
SCRIPT_DIR="/home/brunobastos/Mestrado/Scripts"
SUBJECTS_DIR="$BASE_DIR/fs_subjects"
ATLAS_DIR="$BASE_DIR/Atlas" 

#ROIs(LEFT HEMISPHERE)
mrcalc Julich_parcels_mrtrix.mif 47 -eq Julich_parcels_mrtrix.mif 48 -eq -or ROI_PMC_lh.mif -force
mrcalc Julich_parcels_mrtrix.mif 148 -eq ROI_ML_lh.mif -force
mrcalc Julich_parcels_mrtrix.mif 149 -eq ROI_CP_lh.mif -force
mrcalc Julich_parcels_mrtrix.mif 150 -eq ROI_NR_lh.mif -force
mrcalc Julich_parcels_mrtrix.mif 151 -eq ROI_SN_lh.mif -force
mrcalc Julich_parcels_mrtrix.mif 152 -eq ROI_DN_lh.mif -force

#ROIs(LEFT HEMISPHERE)
mrcalc Julich_parcels_mrtrix.mif 199 -eq Julich_parcels_mrtrix.mif 200 -eq -or ROI_PMC_rh.mif -force
mrcalc Julich_parcels_mrtrix.mif 300 -eq ROI_ML_rh.mif -force
mrcalc Julich_parcels_mrtrix.mif 301 -eq ROI_CP_rh.mif -force
mrcalc Julich_parcels_mrtrix.mif 302 -eq ROI_NR_rh.mif -force
mrcalc Julich_parcels_mrtrix.mif 303 -eq ROI_SN_rh.mif -force
mrcalc Julich_parcels_mrtrix.mif 304 -eq ROI_DN_rh.mif -force

#ML track (LEFT HEMISPHERE)
tckedit tracks_10mio.tck ml_track_lh.tck -include ROI_ML_lh.mif -include ROI_PMC_lh.mif -tck_weights_in sift_weights.txt -minweight 0.5 -force

#mrcalc Julich_parcels_mrtrix.mif 148 -eq ROI1.mif -force
#mrcalc Julich_parcels_mrtrix.mif 47 -eq Julich_parcels_mrtrix.mif 48 -eq -or ROI2.mif -force
#mrcalc ROI1.mif 1 -mult ROI2.mif 2 -mult -add parcels_ML.mif -force
#tck2connectome tracks_10mio.tck parcels_ML.mif connectome_ML.csv -out_assignments assignments_ML.txt -tck_weights_in sift_weights.txt -force
#connectome2tck tracks_10mio.tck assignments_ML.txt ml_track.tck tck_weights_in sift_weights.txt -nodes 1,2 -exclusive -force
#mrview T2_resampled.nii.gz -tractography.load ml_track.tck 

#CST track (LEFT HEMISPHERE)
tckedit tracks_10mio.tck cst_track_lh.tck -include ROI_CP_lh.mif -include ROI_PMC_lh.mif -tck_weights_in sift_weights.txt -minweight 0.5 -force

#nDRTT track (LEFT HEMISPHERE)
tckedit tracks_10mio.tck nDRTT_track_lh.tck -include ROI_DN_lh.mif -include ROI_NR_lh.mif -include ROI_PMC_lh.mif -tck_weights_in sift_weights.txt -minweight 0.5 -force

#DRTT track (LEFT HEMISPHERE)
tckedit tracks_10mio.tck DRTT_track_lh.tck -include ROI_DN_rh.mif -include ROI_NR_lh.mif -include ROI_PMC_lh.mif -tck_weights_in sift_weights.txt -minweight 0.5 -force

#ML track (RIGHT HEMISPHERE)
tckedit tracks_10mio.tck ml_track_rh.tck -include ROI_ML_rh.mif -include ROI_PMC_rh.mif -tck_weights_in sift_weights.txt -minweight 0.5 -force

#CST track (RIGHT HEMISPHERE)
tckedit tracks_10mio.tck cst_track_rh.tck -include ROI_CP_rh.mif -include ROI_PMC_rh.mif -tck_weights_in sift_weights.txt -minweight 0.5 -force

#nDRTT track (RIGHT HEMISPHERE)
tckedit tracks_10mio.tck nDRTT_track_rh.tck -include ROI_DN_rh.mif -include ROI_NR_rh.mif -include ROI_PMC_rh.mif -tck_weights_in sift_weights.txt -minweight 0.5 -force

#DRTT track (RIGHT HEMISPHERE)
tckedit tracks_10mio.tck DRTT_track_rh.tck -include ROI_DN_lh.mif -include ROI_PMC_rh.mif -tck_weights_in sift_weights.txt -minweight 0.5 -force
mrview T2_resampled.nii.gz -tractography.load DRTT_track_rh.tck 
