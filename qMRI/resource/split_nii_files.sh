#!/bin/bash
##
## title:            split_nii_files.sh
## description:      Browse for NIFTI-formatted MRI scan files and split/reshape 
##                   the multivolumetric NIFTI files easing its processing.
## inputs:           (1) Locally accessible copy of XNAT retrieved imaging data 
## author:           Jordi Huguet (AMC)
## date:             20170711
## version:          0.2
## usage:            bash split_nii_files.sh [input directory]


if [ $# != 1 ]
  then
        echo "Split NIFTI N-volumed files in N single-volumed files for qMRI pipeline analysis - v0.1"
        exit 1        
  else
        INPUT_DIRECTORY=$1
        
        # find and assert that the scans parent directory (XNAT) exists conveniently
        SCANS_DIR=$(find $INPUT_DIRECTORY -type d -iname "SCANS")
        if [ ! -d $SCANS_DIR ]; then
            echo "[error] Directory not found: "$SCANS_DIR
            exit 1
        fi
        
        # loop over scans-named directories
        for SCAN_DIR in $(find $SCANS_DIR -mindepth 1 -maxdepth 1 -type d); do
            
            # check the initial number of files
            #FILES_DIR=$(find $SCAN_DIR -type d -iname "files")
            #NUM_FILES=$(ls -1 $FILES_DIR/*.nii* | wc -l )
            
            #if [[ $(basename "$SCAN_DIR") == *"B1"* ]] && [[ NUM_FILES == 4 ]]; then
            #   echo remove 3 and 4
            #elif [[ $(basename "$SCAN_DIR") == *"T1"*"PM" ]] && [[ NUM_FILES == 10 ]]; then
            #   echo remove 6 to 10
            #fi
            
            # get all files recursively found in the current scan directory
            NIFTIs=$(find $SCAN_DIR -type f -iname "*.nii" -o -iname "*.nii.gz")
            
            if [[ -z $NIFTIs ]]; then
                echo "[error] No valid NIFTI files found: "$SCAN_DIR
                exit 1
            fi
            
            # if there are some, loop over the NIFTI files 
            for NII_FILE in $NIFTIs; do
                
                # get via FSL fslinfo tool the 4th dimension of the NIFTI file
                if hash fslinfo 2>/dev/null; then
                    NII_FILE_DIM4_RAW=$(fslinfo "$NII_FILE" | grep dim4)
                else
                    module load fsl
                    NII_FILE_DIM4_RAW=$(fslinfo "$NII_FILE" | grep dim4)
                fi 
                IFS=' ' read -ra PARSED_STR <<< "$NII_FILE_DIM4_RAW"
                NII_FILE_DIM4=${PARSED_STR[1]}
                
                # if current file is a multivolumetric NIFTI image file, SPLIT it!
                if [ $NII_FILE_DIM4 -gt 1 ]; then
                    
                    NII_FILE_BASENAME=$(basename "$NII_FILE")
                    NII_FILE_DIRNAME=$(dirname "$NII_FILE")
                    
                    # trim extension out
                    NII_FILE_ROOT=${NII_FILE_BASENAME%%.*}
                    #NII_FILE_EXT=${NII_FILE_BASENAME#*.}
                    
                    # dcm2niix naming inconsistency, rename original names 
                    #if [[ ${NII_FILE_ROOT: -3} != "_e"* ]]; then
                    #    NII_FILE_ROOT="$NII_FILE_ROOT"_e1
                    #fi
                    
                    if hash fslsplit 2>/dev/null; then
                        fslsplit "$NII_FILE" "$NII_FILE_DIRNAME"/"$NII_FILE_ROOT"_ -t
                    else
                        module load fsl
                        fslsplit "$NII_FILE" "$NII_FILE_DIRNAME"/"$NII_FILE_ROOT"_ -t
                    fi
                    
                    # remove the original (multivolumetric scan image file)
                    rm -vf "$NII_FILE"
                    
                    # reloop over scan directory and remove the recently generated phase-only scan files
                    #for NIFTI_PHASE_IMG in $(find $SCAN_DIR -type f -iname "*_T1*_0001.nii.gz"); do
                    #    rm -vf "$NIFTI_PHASE_IMG"                
                    #done                        
                fi
            done                                               
                        
        done          
fi

exit 0

