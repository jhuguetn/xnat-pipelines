#!/bin/bash
set -e

# FreeSurfer recon-all wrapper or launcher script to get the first file of the input volume (using bash trick) 
# Executing process priority is lowered a bit to enfasten the overall processing

# Creates analysis directory $OUT_DIR/$SUBJECT_NAME, 
# converts one or more input volumes to MGZ format in subjectname/mri/orig, 
# and runs all processing steps/stages. 
# Note: If $SUBJECT_NAME exists, then an error is returned when -i is used


if [ $# != 3 ]
  then
        #echo "No valid arguments supplied"
        echo "FreeSurfer recon-all launcher - v1.2"    
        exit 1
  else
        IN_DIR=$1
        SUBJECT_NAME=$2
        OUT_DIR=$3
        
        #try using NIFTI scan files if available
        IN_FILE=$(find $IN_DIR -type f -iname '*.nii' | sort -n | head -1)
        
        #use DICOM-formatted data otherwise
        if [[ -z $IN_FILE ]]
        then 
            IN_FILE=$(find $IN_DIR -type f -iname '*.dcm' | sort -n | head -1)
        fi
        
        # Jordi Huguet - 20160912 - workaround to fix an issue where FreeSurfer assumes structural scan is DWI and crashes
        # log message:
        #   ERROR: GetDICOMInfo(): dcmGetDWIParams() 7
        #   IsDWI = 1, IsPhilipsDWI = 1
        #   This is a philips DWI, so ignorning the last frame, nframes = 0
        export FS_LOAD_DWI=0
        
        #lower down process priority by max. 19 not to hog resources
        nice -n 19 recon-all -i $IN_FILE -s $SUBJECT_NAME -sd $OUT_DIR -autorecon-all #-autorecon1        
fi

exit 0

