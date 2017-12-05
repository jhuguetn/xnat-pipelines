#!/bin/bash
##
## title:            matlab_runner.sh
## description:      Execute MATLAB code within an XNAT pipeline
##                   Running MATLAB from command-line (resource): https://nl.mathworks.com/help/matlab/ref/matlablinux.html
## inputs:           (1) Matlab toolboxes directory
##                   (2) input data directory
##                   (3) output data directory
## author:           Jordi Huguet (AMC)
## date:             20170228
## version:          0.9
## usage:            bash matlab_runner.sh [toolboxes_dir] [input_dir] [output_dir]

#So Matlab can use some system calls, lets specify a SHELL
export SHELL=/bin/bash

if [ $# != 3 ]
  then
        echo "Execute MATLAB code within an XNAT pipeline - v0.9"
        exit 1
  else
        TOOLBOXES_DIR=$1
        INPUT_DIR=$2
        OUTPUT_DIR=$3

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

    # search and check if SORTED data directory exists
    SORTED_SCANS_DIR=$(find $INPUT_DIR -type d -iname "SORTED")
    if [ ! -d $SORTED_SCANS_DIR ]; then
        echo "[error] Directory not found: "$SORTED_SCANS_DIR
        exit 1
    fi
        
    LOG_FILENAME=$OUTPUT_DIR/matlab_$(date +"%Y%m%d%H%M%S").log

    #-nojvm flag option is making figure() crash with latest MATLAB versions (R2016 or so), skip it
    echo matlab -nodisplay -nosplash -r "try addpath(genpath('$TOOLBOXES_DIR')); addpath(genpath(spm('dir'))); xnat_convert_B1_wrapper('$SORTED_SCANS_DIR','$OUTPUT_DIR'); catch; end; exit" -logfile $LOG_FILENAME
    
fi

exit 0
