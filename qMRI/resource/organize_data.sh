#!/bin/bash
##
## title:            organize_data.sh
## description:      Organize XNAT-downloaded MRI scan files, clean up unnecessary stuff
##                   and reshape the file/directory structure for simplicity.
## inputs:           (1) Locally accessible copy of XNAT retrieved imaging data 
## author:           Jordi Huguet (AMC)
## date:             20171205
## version:          1.1.1
## usage:            bash organize_data.sh [input directory]


if [ $# != 2 ]
  then
        echo "organize XNAT downloaded scan data for qMRI pipeline analysis - v1.1.1"
        exit 1        
  else
        INPUT_DIRECTORY=$1
        B1_DIRECTORY=$2
        
        SCANS_DIR=$(find $INPUT_DIRECTORY -type d -iname "SCANS")
        if [ ! -d $SCANS_DIR ]; then
            echo "[error] Directory not found: "$SCANS_DIR
            exit 1
        fi
        
        PARENT_SCANS_DIR=$(dirname "$SCANS_DIR")
        mkdir -v -p $PARENT_SCANS_DIR/SORTED/B1
        mkdir -v -p $PARENT_SCANS_DIR/SORTED/T1
        
        # B1 map data sorting    
        #
        B1_NIFTIs=$(find $B1_DIRECTORY -type f -iname "*.nii" -o -iname "*.nii.gz")
        if [[ -z $B1_NIFTIs ]]; then
            echo "[error] No valid B1 maps found: "$B1_DIRECTORY
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
                            
        done            
        
        # T1w scan data sorting
        #
        for SCAN_DIR in $(find $SCANS_DIR -mindepth 1 -maxdepth 1 -type d -iname '*T1*M' -o -iname '*T1*P' ); do
            
            # TO-DO: assert that there are either 5 (Magn/Phase only) or 10 files (5 Magn + 5 Phase)
            
            T1_NIFTIs=$(find $SCAN_DIR -type f -iname "*.nii" -o -iname "*.nii.gz")
            if [[ -z $T1_NIFTIs ]]; then 
                echo "[error] No valid B1 datasets found: "$SCAN_DIR
                exit 1
            fi
            
            for T1_NII_FILE in $T1_NIFTIs; do
                
                # TO-DO: rename or refactor the name scheme used to be homogeneous (?)
                # TO-DO: remove unnecessary Phase files (??)
                # HINT --> use file size to distinguish between Phase and Magnitude files
                T1_NII_FILE_BASENAME=$(basename "$T1_NII_FILE")
                T1_NII_FILE_DIRNAME=$(dirname "$T1_NII_FILE")
                    
                mv -v $T1_NII_FILE $PARENT_SCANS_DIR/SORTED/T1
                NEW_FILE_PATH=$PARENT_SCANS_DIR/SORTED/T1/$T1_NII_FILE_BASENAME
                
                #decompress (gzip) for compatibility with Matlab code?
                if [[ $T1_NII_FILE_BASENAME == *.nii.gz ]]
                  then
                    gzip -v -d $NEW_FILE_PATH
                    NEW_FILE_PATH=${NEW_FILE_PATH::-3}
                fi
                
                # TO-DO: move json/csv file as well (with scan details from get_scan_details step)
                if [[ $T1_NII_FILE_BASENAME == *.nii.gz ]]; then 
                    T1_NII_FILE_BASENAME_NO_EXT=${T1_NII_FILE_BASENAME::-7}
                elif [[ $T1_NII_FILE_BASENAME == *.nii ]]; then 
                    T1_NII_FILE_BASENAME_NO_EXT=${T1_NII_FILE_BASENAME::-3}
                fi
                if [ -f $T1_NII_FILE_DIRNAME/$T1_NII_FILE_BASENAME_NO_EXT.json ]; then
                    mv -v $T1_NII_FILE_DIRNAME/$T1_NII_FILE_BASENAME_NO_EXT.json $PARENT_SCANS_DIR/SORTED/T1
                fi
            done            
        done
        
fi

exit 0

