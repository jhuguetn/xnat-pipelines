#!/bin/bash
##
## title:            organize_b1_data.sh
## description:      Reorganize B1 scan files and directory tree structure
## inputs:           (1) Locally accessible copy of imaging data files
## author:           Jordi Huguet (AMC)
## date:             20171205
## version:          0.3.3
## usage:            bash organize_b1_data.sh [input directory]


if [ $# != 1 ]
  then
        echo "Organize XNAT downloaded scan data for convertB1 pipeline analysis - v0.3.3"
        exit 1        
  else
        INPUT_DIRECTORY=$1
        
        SCANS_DIR=$(find $INPUT_DIRECTORY -type d -iname "SCANS")
        if [ ! -d $SCANS_DIR ]; then
            echo "[error] Directory not found: "$SCANS_DIR
            exit 1
        fi
        
        mkdir -v -p $INPUT_DIRECTORY/SORTED
        
        for SCAN_DIR in $(find $SCANS_DIR -mindepth 1 -maxdepth 1 -type d -iname '*B1'); do
            
            B1_NIFTIs=$(find $SCAN_DIR -type f -iname "*.nii" -o -iname "*.nii.gz")
            if [[ -z $B1_NIFTIs ]]; then
                echo "[error] No valid B1 datasets found: "$SCAN_DIR
                exit 1
            fi
            
            for B1_NII_FILE in $B1_NIFTIs; do
            
                mv -v $B1_NII_FILE $INPUT_DIRECTORY/SORTED
                NEW_FILE_PATH=$INPUT_DIRECTORY/SORTED/$(basename $B1_NII_FILE)
                
                #decompress (gzip) for harmonizing and/or compatibility with Matlab code?
                if [[ $(basename $B1_NII_FILE) == *.nii.gz ]]
                  then
                    gzip -v -d $NEW_FILE_PATH
                    NEW_FILE_PATH=${NEW_FILE_PATH::-3}
                fi
                                
            done            
        done
        
fi

exit 0

