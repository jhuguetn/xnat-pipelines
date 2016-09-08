#!/usr/bin/env python

# Created 2014-09-30, Jordi Huguet, Dept. Radiology AMC Amsterdam

####################################
__author__      = 'Jordi Huguet'  ##
__dateCreated__ = '20141008'      ##
__version__     = '1.1'           ##
__versionDate__ = '20160908'      ##
####################################

# TO DO:
# - ...

import os
import sys
from lxml import etree
from datetime import datetime
from pprint import pprint
from os.path import basename

class FileStats(object):
    def __init__(self, globalMeasures, structures):
		self.globalMeasures = globalMeasures
		self.structures = structures	
	
def parseStructures(headers, structsTextLines) :
	
	structures = {}
	
	# Add column descriptors (headers) to the dict's 1rst place for future reference
	structures.update({ 'headers' : headers })
	# Check the headers for the 'structure name' column used as key in the output dict
	keyIndex = headers.index('StructName')	
	# Per each text line, split values (structure calculated attributes)
	for line in structsTextLines :
		lineElems = line.split()
		# Build a dictionary using struct names as keys and its attributes (whole list) as value
		structures.update({ ((lineElems[keyIndex]).replace('-', '_')).lower() : lineElems})
		
	return structures

def parseGlobalMeasures(measureTextLines) :
	
	globalMeasures = {}
	# Per each text line, split comma sepparated values (measure attributes)
	for csvLine in measureTextLines:
		mlineElems = csvLine.split(', ')		
		#pieces = map(lambda x: x.strip(), mlineElems)
		# Build a dictionary using measure names as keys and its numerical measurements as values
		globalMeasures.update({ ((mlineElems[1]).replace('-', '_')).lower() : mlineElems[3]})
		
	return globalMeasures
	
def parseFile(fileName):
		
	with open(fileName) as pFile:
		# Read the file content out and split it in a list of file lines
		fileContentList = map(lambda x: x.strip(), pFile.read().splitlines())
	
	globalMeasures = {}
	# From the list of lines pulled out, filter those starting with Measure and parse them to get a suitable dictionary object
	globalMeasures = parseGlobalMeasures(filter(lambda x: x.startswith('# Measure'), fileContentList))  
	
	structures = {}
	colHeaders = ( (filter(lambda x: x.startswith('#'), fileContentList)[-1]).split() )[2:]
	structures = parseStructures(colHeaders, filter(lambda x: not x.startswith('#'), fileContentList))	
	
	return  FileStats(globalMeasures, structures)
	
# if __name__=="__main__" :
	# print ''
	
	# if basename(sys.argv[1]).lower() == 'aseg.stats' :
		# asegData = (parseFile(sys.argv[1]))
		# pprint (asegData.globalMeasures.keys())
		# pprint (asegData.structures.keys())
