#!/bin/bash
##
## title:               organize_data.sh
## description:    Search for XNAT-downloaded MRI files and reshape the file/directory structure for running QAP (BIDS spec).
##                       Script recurses over a directory tree of XNAT downloaded data and reshapes it to meet QAP requirements on input datasets.
## inputs:           (1) XNAT project identifier (BIDS site)
##                       (2) XNAT subject label (BIDS subject ID)
##                       (3) XNAT MRI session label (BIDS session ID)
##                       (4) Type of scans to be processed (QAP requirement: should be included as prefix in the scan directory name)
##                       (5) A locally accessible location of XNAT retrieved imaging data (organized in folders per subject)
## author:           Jordi Huguet (AMC)
## date:              20160921
## version:          0.3
## usage:            bash organize_data.sh [project ID] [subject label] [MRI session label] [scans_type] [input directory]


if [ $# != 5 ]
  then
        echo "organize XNAT output to meet BIDS specification (QAP package) - v0.3"
        exit 1
        #echo "No valid arguments supplied"
        #echo ""
        #echo "organizer :: Organize XNAT outputs to meet QAP package requirements"
        #echo "arguments: <input directory>>"
        #echo ""
        #exit 1
  else
        PROJECT=$1
        SUBJECT_NAME=$2
        SESSION_NAME=$3
        SCANS_TYPE=$4
        INPUT_DIRECTORY=$5
        # compose the root directory where BIDS organized data will be hosted
        BIDS_DIRECTORY=$(dirname $INPUT_DIRECTORY)/BIDS

        # initial checkings for working directory names provided
        if [ ! -d $INPUT_DIRECTORY ]; then
            echo "[error] Directory not found: "$INPUT_DIRECTORY
            exit 1
        fi

        if [ ! -d $BIDS_DIRECTORY ]; then
            echo "[error] Directory not found: "$BIDS_DIRECTORY
            exit 1
        fi

        for scans_dir in $(find $INPUT_DIRECTORY -type d -iname "SCANS"); do
            for scanID_dir in $(find $scans_dir -maxdepth 1 -mindepth 1 -type d); do
                #create the per-scan proper directory structure in the BIDS directory

                bids_scan_path=$BIDS_DIRECTORY/$PROJECT/$SUBJECT_NAME/$SESSION_NAME/$SCANS_TYPE'_'$(basename $scanID_dir)
                echo $bids_scan_path
                # if [ $SCANS_TYPE == "anat" ]; then
                #     bids_scan_path=$BIDS_DIRECTORY/$PROJECT/$SUBJECT_NAME/$SESSION_NAME/anat_$(basename $scanID_dir)
                # elif [ $SCANS_TYPE == "func" ]; then
                #     bids_scan_path=$BIDS_DIRECTORY/$PROJECT/$SUBJECT_NAME/$SESSION_NAME/func_$(basename $scanID_dir)
                # fi

                mkdir -v -p $bids_scan_path

                #if no NIFTIs, lets desperately attempt to use DICOMs if available (converting them to NIFTI)
                NIFTI_DIR=$(find $scanID_dir -type d -iname "NIFTI")
                # -z checks for an empty string (i.e. no NIFTI data directories found)
                if [[ -z $NIFTI_DIR ]]
                  then
                    #no NIFTI data
                    DICOM_DIR=$(find $scanID_dir -type d -iname "DICOM")
                    if [[ -z $DICOM_DIR ]]
                      then
                        echo "[error] No valid data found: "$scanID_dir
                        exit 1
                      else
                        #dcm2nii --> convert to NIFTI (EXPERIMENTAL)!
                        mkdir -v -p $(dirname $DICOM_DIR)/NIFTI

                        source /etc/profile.d/modules.sh
                        module load mricron
                        dcm2nii -b /xnat/etc/dcm2nii.ini -p N -d N -e N -f N -g N -n Y -r N -x N -o $(dirname $DICOM_DIR)/NIFTI $DICOM_DIR

                        /xnat/pipeline/amc-catalog/mricron/resource/cleanUp.sh $(dirname $DICOM_DIR)/NIFTI
                        echo "[warning] NIFTI images automatically converted from DICOMs (experimental)"
                    fi
                fi

                #re-do the find search command for new NIFTI files
                NIFTIs=$(find $scanID_dir -type f -iname "*.nii") #-o -iname "*.bvec" -o -iname "*.bval" )
                # -z checks for an empty string (i.e. no NIFTI data directories found)
                if [[ -z $NIFTIs ]]
                  then
                    echo "[error] No valid imaging data found: "$scanID_dir
                    exit 1
                  else
                    for NIFTI_file in $NIFTIs; do
                        # for each NIFTI file move it to BIDS directory and gzip it (replacing uncompressed file)
                        mv -v $NIFTI_file $bids_scan_path
                        gzip -v $bids_scan_path/$(basename $NIFTI_file)
                    done
                fi
            done
        done
fi

exit 0

