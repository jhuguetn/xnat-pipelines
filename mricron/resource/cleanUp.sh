#!/bin/bash
set -e

# Mricron dcm2nii tool for converting MRI scan data to NIFTI, creates by default (behaviour which cannot be modified) 2 NIFTI versions of the scan image
# making new upload client service fail due to number of files > scans (XnatDataClient). Script to workaround that.
				
if [ $# != 1 ]
  then
	#echo "No valid arguments supplied"
	echo "dcm2nii output clean-up - v1.0"	
	exit 1
  else
	INPUT_DIRECTORY=$1
	
	NII_FILES="$(find $INPUT_DIRECTORY  -maxdepth 1 -iname "*.nii")"
	
	fileArray=($NII_FILES)
	size=${#fileArray[@]}
	
	if [ $size == 2 ]; then
		for niiPath in $NII_FILES
		do
			niiFilename=$(basename "$niiPath")
			if [[ $niiFilename == x*.nii ]];
			then
				# delete the NIFTI file version where DWI is removed from DTI scan 
				rm -v $niiPath
			fi
		done
	fi
		
fi

