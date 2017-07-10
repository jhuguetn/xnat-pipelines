#!/bin/bash
##
## title:            organize_data.sh
## description:      Search for XNAT-downloaded MRI scan files, clean up unnecessary stuff
##                   and reshape the file/directory structure for simplicity.
## inputs:           (1) Locally accessible copy of XNAT retrieved imaging data 
## author:           Jordi Huguet (AMC)
## date:             20170710
## version:          0.2
## usage:            bash organize_data.sh [input directory]


if [ $# != 1 ]
  then
        echo "organize XNAT downloaded scan data for qMRI pipeline analysis - v0.2"
        exit 1        
  else
        INPUT_DIRECTORY=$1
        
        SCANS_DIR=$(find $INPUT_DIRECTORY -type d -iname "SCANS")
        if [ ! -d $SCANS_DIR ]; then
            echo "[error] Directory not found: "$SCANS_DIR
            exit 1
        fi
        
        PARENT_SCANS_DIR=$(dirname "$SCANS_DIR")
        mkdir -v -p $PARENT_SCANS_DIR/SORTED/B1
        mkdir -v -p $PARENT_SCANS_DIR/SORTED/T1
        
        for SCAN_DIR in $(find $SCANS_DIR -mindepth 1 -maxdepth 1 -type d -iname '*B1'); do
            
            # TO-DO: assert that there are 4 files (2 Magn + 2 Phase)
            
            B1_NIFTIs=$(find $SCAN_DIR -type f -iname "*.nii" -o -iname "*.nii.gz")
            if [[ -z $B1_NIFTIs ]]; then
                echo "[error] No valid B1 datasets found: "$SCAN_DIR
                exit 1
            fi
            
            for B1_NII_FILE in $B1_NIFTIs; do
            
                # TO-DO: rename or refactor the name scheme used to be homogeneous (?)
                # HINT --> use file size to distinguish between Phase and Magnitude files
                
                mv -v $B1_NII_FILE $PARENT_SCANS_DIR/SORTED/B1
                NEW_FILE_PATH=$PARENT_SCANS_DIR/SORTED/B1/$(basename $B1_NII_FILE)
                
                #decompress (gzip) for harmonizing and/or compatibility with Matlab code?
                if [[ $(basename $B1_NII_FILE) == *.nii.gz ]]
                  then
                    gzip -v -d $NEW_FILE_PATH
                    NEW_FILE_PATH=${NEW_FILE_PATH::-3}
                fi
                
                # TO-DO: move json/csv file as well (with scan details from get_scan_details step)?
            done            
        done
        
        for SCAN_DIR in $(find $SCANS_DIR -mindepth 1 -maxdepth 1 -type d -iname '*T1*M'); do
            
            # TO-DO: assert that there are either 5 (Magn only) or 10 files (5 Magn + 5 Phase)
            
            T1_NIFTIs=$(find $SCAN_DIR -type f -iname "*.nii" -o -iname "*.nii.gz")
            if [[ -z $T1_NIFTIs ]]; then 
                echo "[error] No valid B1 datasets found: "$SCAN_DIR
                exit 1
            fi
            
            for T1_NII_FILE in $T1_NIFTIs; do
                
                # TO-DO: rename or refactor the name scheme used to be homogeneous (?)
                # TO-DO: remove unnecessary Phase files
                # HINT --> use file size to distinguish between Phase and Magnitude files
                
                mv -v $T1_NII_FILE $PARENT_SCANS_DIR/SORTED/T1
                NEW_FILE_PATH=$PARENT_SCANS_DIR/SORTED/T1/$(basename $T1_NII_FILE)
                
                #decompress (gzip) for compatibility with Matlab code?
                if [[ $(basename $T1_NII_FILE) == *.nii.gz ]]
                  then
                    gzip -v -d $NEW_FILE_PATH
                    NEW_FILE_PATH=${NEW_FILE_PATH::-3}
                fi
                
                # TO-DO: move json/csv file as well (with scan details from get_scan_details step)?
            done            
        done
        
fi

exit 0

