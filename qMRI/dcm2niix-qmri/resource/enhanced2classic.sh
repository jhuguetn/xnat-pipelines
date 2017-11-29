#!/bin/bash
# Usage: ./enhanced2classic.sh <input_folder> [<output_folder>]
#
# This script converts enhanced DICOM files to non-enhanced series. The input folder can
# contain a mixture of enhanced and non-enhanced dicom files, but only the enhanced files will be
# converted. Each enhanced file will be replaced by a folder with identical name, containing
# a series of single-frame files. A separate log-file will be created for each converted file.
# Non-enhanced files will be left as-is.
#
# Requirements: dcmtk and dicom3tools.
#
# Created 2016-06-23, Paul F.C. Groot. Academic Medical Center, Amsterdam, The Netherlands
# 
#   $Rev:: 40                   $:  Revision of last commit
#   $Author:: pfgroot           $:  Author of last commit
#   $Date:: 2016-06-23 17:12:06#$:  Date of last commit
#

set -e

if [ $# -lt 1 ]
then
	echo "Usage: ./enhanced2classic.sh <input_folder> [<output_folder>]"
	exit -1
fi

SRC="$1"
if [ $# -eq 1 ]
then
	DST="${1}_classic"
else
	DST="$2"
fi

if [ ! -e "$SRC" ]
then
	echo "Dicom source not found: $DST"
	echo "Aborting!"
	exit -1
fi

if [ -e "$DST" ]
then
	echo "Destination already exists: $DST"
	echo "Aborting!"
	exit 1
fi

WORK="${DST}~"

if [ -e "$WORK" ]
then
	echo "Working folder already exists: $WORK"
	echo "Aborting!"
	exit 2
fi

echo "Creating a copy of ${SRC}..."
cp -ra "$SRC" "$WORK"

find "${WORK}" -type f -print0 | while read -d $'\0' file
do
	SOPClass=`dcmdump "$file" -s -M +p +P 'SOPClassUID' | awk '{ print $3 }'`
	case "$SOPClass" in
		=Enhanced*)
			echo "unenhancing [$SOPClass]: $file"
			DIR=`dirname "$file"`
			BASE=`basename "$file"`
			TMPDIR="${DIR}~"
			mkdir "${TMPDIR}"
			TMPFILE="${TMPDIR}/${BASE}"
			cp "$file" "${TMPFILE}"
			if dcuncat -unenhance -sameseries "${TMPFILE}" -of "${TMPDIR}/I_" &> "${file}.log"
			then
				mv "${file}.log" "${file}.warn.log"
				
				for DCM in "${TMPDIR}"/I_*
				do
					# remove ContentQualification=RESEARCH and ImageComments='research-only bla'
					if ! dcmodify -nb -e '0018,9004' -e '0020,4000' "$DCM" 2>> "${file}.error.log"
					then
						rm -f "$DCM"
					fi
				done			
			else
				mv "${file}.log" "${file}.error.log"
			fi
			rm -f "${TMPFILE}"
			rm -f "$file"
			mv "${TMPDIR}" "$file"
			;;
		*) echo "Skipping conversion of non-enhanced [$SOPClass] object: $file"
			;;
	esac

done

# remove empty logfiles
find "${WORK}" -type f -name '*.log' -empty -delete

# move results to specified folder
echo "Moving copy to ${DST}"
mv -n "$WORK" "${DST}"

# display warning logs
N_warn=`find "${DST}" -type f -name '*.warn.log' | wc -l`
if [ $N_warn -gt 0 ]
then
	echo
	echo "Logfiles containing warnings (#=$N_warn):"
	# Jordi Huguet modification for programatic usage as a pipeline (20171123)
    find "${DST}" -type f -name '*.warn.log' -delete
    
fi

# display error logs
N_error=`find "${DST}" -type f -name '*.error.log' | wc -l`
if [ $N_error -gt 0 ]
then
	echo
	echo "Logfiles containing errors (#=$N_error):"
	# Jordi Huguet modification for programatic usage as a pipeline (20171123)
    #find "${DST}" -type f -name '*.error.log'
    find "${DST}" -type f -name '*.error.log' -delete
fi

echo
echo "Ready"

