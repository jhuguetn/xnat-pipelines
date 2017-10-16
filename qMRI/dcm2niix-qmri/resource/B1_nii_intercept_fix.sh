#!/bin/bash
set -e

# Script for fixing scale intercept value on NIFTI-converted (dcm2niix) B1 scans 
# creator: jhuguet (AMC)
# project: fab4v (2017)
# version: 0.0.1
 
 
function run_fslmaths() {
    if hash fslmaths 2>/dev/null; then
        echo fslmaths "$@"
        fslmaths "$@"
    else
        module load fsl
        echo fslmaths "$@"
        fslmaths "$@"
    fi
}

 
if [ $# != 3 ]
  then
    echo "$0 <scale_intercept_value> <input_filename> <output_filename>"
    exit 1
  else
    INTERCEPT_VAL=$1
    INPUT_FILE=$2
    OUTPUT_FILE=$3
    
    OUTPUT_DIR=$(dirname "$OUTPUT_FILE")
    
    # initial checkings for valid input files/directories
    if [ ! -f $INPUT_FILE ]; then
        echo "[error] Input file not found: "$INPUT_FILE
        exit 1
    fi
    if [ ! -d $OUTPUT_DIR ]; then
        echo "[error] Output directory not found: "$OUTPUT_DIR
        exit 1
    fi
    
    command_params="$INPUT_FILE -sub $INTERCEPT_VAL $OUTPUT_FILE"
    run_fslmaths $command_params
    
    # fslmaths ALWAYS creates a gziped version of the modified file
    # let's add the following control flow statement for consistency
    # (if name extension was non-compressed NIFTI, decompress file)
    if [ ${OUTPUT_FILE: -4} == ".nii" ]; then
        gzip -d "$OUTPUT_FILE.gz"
    fi
    
fi

