#!/bin/bash
##
## title:            mri_deface.sh
## description:      Prepare data and compute mri_deface for facial identifiable traits removal
##                   
## inputs:           (1) input data directory
##                   (2) output data directory
##                   (3) XNAT session label
## author:           Jordi Huguet (AMC)
## date:             20170525
## version:          0.1
## usage:            bash mri_deface.sh [input_dir] [output_dir] [session_label]

if [ $# != 3 ]
  then
        echo "Prepare data and compute mri_deface for facial identifiable traits removal - v0.1"
        exit 1
  else
        INPUT_DIR=$1
        OUTPUT_DIR=$2
        SESSION_NAME=$3

    # initial checkings for working directory names provided
    if [ ! -d $INPUT_DIR ]; then
        echo "[error] Directory not found: "$INPUT_DIR
        exit 1
    fi
    if [ ! -d $OUTPUT_DIR ]; then
        echo "[error] Directory not found: "$OUTPUT_DIR
        exit 1
    fi
    
    # few additional naive checkings for the mri_deface binary files existence
    CURRENT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    echo $CURRENT_DIR
    if [ ! -f $CURRENT_DIR/mri_deface_bin/mri_deface ]; then
        echo "[error] Binary file not found: "$CURRENT_DIR/mri_deface_bin/mri_deface
        exit 1
    fi
    BRAIN_TEMPLATE_FILE=$(find $CURRENT_DIR/mri_deface_bin -type f -iname 'talairach_mixed_with_skull.gca' | shuf -n 1)
    if [ -z "$BRAIN_TEMPLATE_FILE" ]; then
        echo "[error] Template file not found: "$CURRENT_DIR/mri_deface_bin/templates/talairach_mixed_with_skull.gca
        exit 1
    fi
    FACE_TEMPLATE_FILE=$(find $CURRENT_DIR/mri_deface_bin -type f -iname 'face.gca' | shuf -n 1)
    if [ -z "$FACE_TEMPLATE_FILE" ]; then
        echo "[error] Template file not found: "$CURRENT_DIR/mri_deface_bin/templates/face.gca
        exit 1
    fi

    for scans_dir in $(find $INPUT_DIR -type d -iname "SCANS"); do
        for scanID_dir in $(find $scans_dir -maxdepth 1 -mindepth 1 -type d); do
        
            #create a subdirectory (SCAN-ID named) under main output directory
            OUTPUT_SCAN_DIR=$OUTPUT_DIR/$(basename $scanID_dir)
            mkdir -v -p $OUTPUT_SCAN_DIR
            
            #get a NIFTI (preferably) or a DICOM random file from the SCAN raw data directory
            INPUT_FILE=$(find $scanID_dir -type f -iname '*.nii' -o  -iname '*.nii.gz' | shuf -n 1)
            # -z checks for an empty string (i.e. no NIFTI data directories found)
            if [[ -z $INPUT_FILE ]]; then    
                #no NIFTI data, lets look for DICOMs
                INPUT_FILE=$(find $scanID_dir -type f -iname '*.dcm' | shuf -n 1)
                if [[ -z $INPUT_FILE ]]; then
                    echo "[error] No valid data found: "$scanID_dir
                    exit 1
                fi              
            fi
            
            #LOG_FILENAME=$OUTPUT_DIR/matlab_s$(basename $scanID_dir)_$(date +"%Y%m%d%H%M%S").log
            OUTPUT_FILE=$OUTPUT_SCAN_DIR/${SESSION_NAME}_s$(basename $scanID_dir)_defaced.nii.gz
            
            $CURRENT_DIR/mri_deface_bin/mri_deface $INPUT_FILE $BRAIN_TEMPLATE_FILE $FACE_TEMPLATE_FILE $OUTPUT_FILE

        done
    done
fi

exit 0
