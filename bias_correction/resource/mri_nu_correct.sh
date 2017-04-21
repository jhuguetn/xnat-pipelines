#!/bin/bash
##
## title:            mri_nu_correct.sh
## description:      Prepare data and compute mri_nu_correct for bias correction  
##                   
## inputs:           (1) input data directory
##                   (2) output data directory
##                   (3) debug flag
##                   (4) XNAT session label
## author:           Jordi Huguet (AMC)
## date:             20170421
## version:          0.3
## usage:            bash mri_nu_correct.sh [input_dir] [output_dir] [debug_flag] [session_label]

if [ $# != 4 ]
  then
        echo "Prepare data and compute mri_nu_correct for bias correction - v0.2"
        exit 1
  else
        INPUT_DIR=$1
        OUTPUT_DIR=$2
        DEBUG_FLAG=$3
        SESSION_NAME=$4

    # initial checkings for working directory names provided
    if [ ! -d $INPUT_DIR ]; then
        echo "[error] Directory not found: "$INPUT_DIR
        exit 1
    fi
    if [ ! -d $OUTPUT_DIR ]; then
        echo "[error] Directory not found: "$OUTPUT_DIR
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
            OUTPUT_FILE=$OUTPUT_SCAN_DIR/$SESSION_NAME_s$(basename $scanID_dir)_biascorr.nii.gz
            
            if [ "$DEBUG_FLAG" == "Y" ]; then
                mri_nu_correct.mni --debug --i $INPUT_FILE --o $OUTPUT_FILE
            else
                mri_nu_correct.mni --i $INPUT_FILE --o $OUTPUT_FILE
            fi
        done
    done
fi

exit 0
