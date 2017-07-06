#!/bin/bash
##
## title:            dti_preprocessing_core.sh
## description:      Prepare data and compute preprocessing corrections on MRI DTI scans
##                   Running MATLAB from command-line (resource): https://nl.mathworks.com/help/matlab/ref/matlablinux.html
## inputs:           (1) Matlab toolboxes directory
##                   (2) input data directory
##                   (3) output data directory
## author:           Jordi Huguet (AMC)
## date:             20170228
## version:          0.6
## usage:            bash dti_preprocessing_core.sh [toolboxes_dir] [input_dir] [output_dir]

#So Matlab can use some system calls, lets specify a SHELL
export SHELL=/bin/bash

if [ $# != 3 ]
  then
        echo "Prepare data and compute preprocessing corrections on MRI DTI scans - v0.6"
        exit 1
  else
        TOOLBOXES_DIR=$1
        INPUT_DIR=$2
        OUTPUT_DIR=$3

    #LOG_FILENAME=$OUTPUT_DIR/matlab_$(date +"%Y%m%d%H%M%S").log

    # initial checkings for working directory names provided
    if [ ! -d $INPUT_DIR ]; then
        echo "[error] Directory not found: "$INPUT_DIR
        exit 1
    fi
    if [ ! -d $TOOLBOXES_DIR ]; then
        echo "[error] Directory not found: "$TOOLBOXES_DIR
        exit 1
    fi
    if [ ! -d $OUTPUT_DIR ]; then
        echo "[error] Directory not found: "$OUTPUT_DIR
        exit 1
    fi

    #Spinoza environment Setting:
    #source /etc/profile.d/modules.sh; module load fsl; module load matlab; module load matlab/toolbox/spm8; module load dtitk; module load matlab/toolbox/dipimage; module load matlab/toolbox/NIfTI 
    #RADIAN Setting (NIFTI matlab toolbox is not a module there):
    #source /etc/profile.d/modules.sh; module load fsl; module load matlab; module load matlab/toolbox/spm8; module load dtitk; module load dipimage #; module load matlab/toolbox/NIfTI
    #source /etc/profile.d/modules.sh; module list
    
    for scans_dir in $(find $INPUT_DIR -type d -iname "SCANS"); do
        for scanID_dir in $(find $scans_dir -maxdepth 1 -mindepth 1 -type d); do
        
            #create a subdirectory (SCAN-ID named) under main output directory
            OUTPUT_SCAN_DIR=$OUTPUT_DIR/$(basename $scanID_dir)
            mkdir -v -p $OUTPUT_SCAN_DIR
            
            #get a NIFTI (preferably) or a DICOM random file from the SCAN raw data directory
            INPUT_FILE=$(find $scanID_dir -type f -iname '*.nii' -o -iname '*.nii.gz' | shuf -n 1)
            # -z checks for an empty string (i.e. no NIFTI data directories found)
            if [[ -z $INPUT_FILE ]]; then    
                #no NIFTI data, lets look for DICOMs
                INPUT_FILE=$(find $scanID_dir -type f -iname '*.dcm' | shuf -n 1)
                if [[ -z $INPUT_FILE ]]; then
                    echo "[error] No valid data found: "$scanID_dir
                    exit 1
                fi
              else
                #good: NIFTI data found!
                
                #[workaround] since code does not accept gzipped NIFTIs, if is the case is gzip -> decompress it 
                if [[ $(basename $INPUT_FILE) == *.nii.gz ]]
                  then
                    gzip -d $INPUT_FILE
                    INPUT_FILE=${INPUT_FILE::-3}
                fi
                
                # check for existence of required bvec/bval files
                filedirpath=$(dirname "$INPUT_FILE")
                
                BVEC_FILE=$(find $filedirpath -type f -iname '*.bvec' | shuf -n 1)
                if [[ -z $BVEC_FILE ]]; then
                    echo "[error] BVEC file not found for: "$INPUT_FILE
                    exit 1
                fi
                BVAL_FILE=$(find $filedirpath -type f -iname '*.bval' | shuf -n 1)
                if [[ -z $BVAL_FILE ]]; then
                    echo "[error] BVAL file not found for: "$INPUT_FILE
                    exit 1
                fi
            
            fi
            
            LOG_FILENAME=$OUTPUT_DIR/matlab_s$(basename $scanID_dir)_$(date +"%Y%m%d%H%M%S").log
    
            #-nojvm flag option is making figure() crash with latest MATLAB versions (R2016 or so), skip it
            matlab -nodisplay -nosplash -r "try addpath(genpath('$TOOLBOXES_DIR')); addpath(genpath(spm('dir'))); mainConvertDTI('$INPUT_FILE','$OUTPUT_SCAN_DIR'); catch; end; exit" -logfile $LOG_FILENAME
        done
    done
fi

exit 0
