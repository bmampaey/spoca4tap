# Pipeline to create coronal hole maps and extract the parameters for the ROB TAP service

The following steps are executed to generate the parameters for the TAP service:
 1. calibrate SDO/AIA images from level 1 to level 2 and calibrate SDO/HMI images from level 1 to level 1.5
 2. compute class centers using the SPoCA suite software on the SDO/AIA level 2 images
 3. create segmentation maps using the SPoCA suite software and the class centers on the SDO/AIA level 2 images
 4. create coronal hole maps using the SPoCA suite software, the segmentation maps, and SDO/AIA level 2 and SDO/HMI level 1.5 images for the coronal hole statistics
 5. track the coronal hole detections in time using the SPoCA suite software and the coronal hole maps
 6. clean the tracked maps by removing all coronal holes that have a lifetime below 3 days
 7. create coronal hole maps previews using the SPoCA suite software and the cleaned maps
 8. extract the TAP parameters for the TAP service using the tracked maps and the cleaned maps

The following python scripts are used to execute steps 2 to step 8:
 * scripts/get_class_centers.py : (Step 2) Execute the SPoCA classification program on image FITS files to compute the class centers
 * scripts/get_segmentation_map.py : (Step 3) Execute the SPoCA attribution program on image FITS files to create a segmentation map
 * scripts/get_region_map.py : (Step 4) Execute the SPoCA get_ch_map or get_ar_map program on a segmentation map to create a region map
 * scripts/get_tracked_map.py : (Step 5) Execute the SPoCA tracking program on region maps
 * scripts/get_longlived_regions_colors.py : (Step 6) Compute the lifespan of regions on tracked region maps and create the list of longlived regions colors
 * scripts/get_cleaned_map.py : (Step 6) Clean a region map to only keep the long lived regions
 * scripts/get_overlay_image.py : (Step 7) Execute the SPoCA overlay program on a region map to display the contours of the regions on top of an image FITS file
 * scripts/get_epn_core_tap_parameters.py : (Step 8) Extract the TAP parameters for the epn_core table
 * scripts/get_tracking_tap_parameters.py : (Step 8) Extract the TAP parameters for the tracking table
 * scripts/get_datalink_tap_parameters.py : (Step 8) Extract the TAP parameters for the datalink table
 * scripts/rob_spoca_ch_pipeline.py: Execute the steps 3 to 8 in

All the scripts expect configuration files :
 * configs/rob_spoca_ch.ini__: Global configuration file for the pipeline
 * configs/ch_attribution.config : Configuration file for the ch_attribution.x SPoCA program
 * configs/ch_classification.config : Configuration file for the ch_classification.x SPoCA program
 * configs/get_ch_map.config : Configuration file for the get_ch_map.x SPoCA program
 * configs/overlay.config : Configuration file for the overlay.x SPoCA program
 * configs/tracking.config : Configuration file for the tracking.x SPoCA program

Notes:
 * The SPoCA software suite can be obtained at https://github.com/bmampaey/SPoCA, the above scripts expect the software to be installed in the SPoCA subfolder. The makefiles to build the necessary SPoCA programs are also located in the SPoCA subfolder.
 * Step 1 is done independently of this pipeline.
 * The class centers used at step 3 are computed by taking the median of the class centers computed at step 2 over an 11 year period starting January 1st 2012
 * For step 2 to 7, activity logs are recorded to JSON files to create provenance documentation.
 * The TAP parameters from step 8 are written to CSV files.
 * When running the rob_spoca_ch_pipeline script, the cleaned maps will not be created for the last 3 days, and the TAP parameters will no be extracted. Indeed it is not possible to know if the lifetime of the coronal holes for these maps are longer than 3 days. The tracked maps for which no cleaned maps have been created, must be passed to the next execution of the script as the tracked-ch-maps parameter.
