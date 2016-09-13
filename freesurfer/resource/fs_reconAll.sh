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
        echo "FreeSurfer recon-all launcher - v1.1"    
        exit 1
  else
        IN_DIR=$1
        SUBJECT_NAME=$2
        OUT_DIR=$3
        DCM_FILE=$(find $IN_DIR -type f -iname '*.dcm' | sort -n | head -1)
        
        #module load freesurfer/5.3.0
        #export FREESURFER_HOME=/opt/amc/freesurfer-5.3.0
        #export NO_FSFAST=1
        #source /opt/amc/freesurfer-5.3.0/FreeSurferEnv.sh
        
        # Jordi Huguet - 20160912 - workaround to fix an issue where FreeSurfer assumes structural scan is DWI and crashes
        #   ERROR: GetDICOMInfo(): dcmGetDWIParams() 7
        #   IsDWI = 1, IsPhilipsDWI = 1
        #   This is a philips DWI, so ignorning the last frame, nframes = 0
        export FS_LOAD_DWI=0
        
        echo nice -n 19 recon-all -i $DCM_FILE -s $SUBJECT_NAME -sd $OUT_DIR -autorecon-all #-autorecon1        
        nice -n 19 recon-all -i $DCM_FILE -s $SUBJECT_NAME -sd $OUT_DIR -autorecon-all #-autorecon1        
fi

exit 0

