#!/bin/bash
##
## title:             qap_config_generator.sh
## description:  Create a QAP specific configuration file (YAML format) for running the QAP package.
##                      Script simply writes baseline configuration options to file line-by-line and additionally enters
##                      argument-based output and working directories.
##
## inputs:          (1) output directory
##                      (2) working directory
##                      (3) generated configuration file name
##                      (4) scans type, either {anat,func}
## author:          Jordi Huguet (AMC)
## date:             20160922
## version:         0.1
## usage:           bash qap_config_generator.sh [output_qap_directory] [working_qap_directory] [config_file_path] [scans_type]


if [ $# != 4 ]
  then
        echo "generate QAP configuration file (QAP package) - v0.1"
        exit 1

  else
        OUTPUT_DIRECTORY=$1
        WORKING_DIRECTORY=$2
        CONFIG_FILENAME=$3
        SCANS_TYPE=$4

        echo "num_cores_per_subject: 1" >> $CONFIG_FILENAME
        echo "num_subjects_at_once: 1" >> $CONFIG_FILENAME
        echo "output_directory: "$OUTPUT_DIRECTORY >> $CONFIG_FILENAME
        echo "working_directory: "$WORKING_DIRECTORY >> $CONFIG_FILENAME
        # Jordi Huguet (20160510) - "IOError: Duplicate node name datasink_qap_mosaic found"
        # Error fix not yet available, workaround: choose between having 'write_reports' or 'write_all_outputs' set to True.
        #write_all_outputs: True
        echo "write_all_outputs: False" >> $CONFIG_FILENAME
        echo "write_report: True" >> $CONFIG_FILENAME
        echo "write_graph: True" >> $CONFIG_FILENAME
        if [ $SCANS_TYPE == "func" ]; then

            # check those below with the fMRI experts!
            echo "start_idx: 0" >> $CONFIG_FILENAME
            echo "stop_idx: End" >> $CONFIG_FILENAME
            echo "slice_timing_correction: True" >> $CONFIG_FILENAME
            # 'ghost_directorion' allows specifying the phase encoding used to acquire the scan. Omitting this option will default to y.
            # Options: x - RL/LR, y - AP/PA, z - SI/IS, or all
            echo "ghost_direction: y" >> $CONFIG_FILENAME

        #elif [ $SCANS_TYPE == "anat" ]; then
            # Template brain to be used during anatomical registration, as a reference
            #echo "template_brain_for_anat: XXX" >> $CONFIG_FILENAME
        fi
fi

exit 0

