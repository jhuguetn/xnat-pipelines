#!/usr/bin/env python

#   Copyright 2012 Integrated Brain Imaging Center
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

####################################
__author__      = 'Nolan Nichols' ##
__dateCreated__ = '20110427'      ##
__version__     = '0.3'           ##
__versionDate__ = '20140227'      ##
####################################

import dicom as dcm
import subprocess as sub
import os
from lxml import etree
from base64 import b64decode
import sys

from dicom.filereader import InvalidDicomError

def isSessionExamCard(dcm_file):
    """Helper function to check if dicom file is an Session ExamCard"""
    try:
        dcmFile = dcm.read_file(dcm_file)
    except IOError:
        print '[Warning] No such file: ',dcm_file
    except InvalidDicomError:
        print '[Warning] Invalid DICOM file: ',dcm_file 
    else:
        if dcmFile.SOPClassUID == '1.2.840.10008.5.1.4.1.1.66':
            if dcmFile.ProtocolName == 'ExamCard':
                return True
        return False

def isSeriesExamCard(dcm_file):
    """Helper function to check if dicom file is a Series ExamCard"""
    try:
        dcmFile = dcm.read_file(dcm_file)
    except IOError:
        print '[Warning] No such file: ',dcm_file
    except InvalidDicomError:
        print '[Warning] Invalid DICOM file: ',dcm_file
    else:
        if dcmFile.SOPClassUID == '1.2.840.10008.5.1.4.1.1.66':
            if dcmFile.ProtocolName != 'ExamCard':
                return True
        return False

def dcm_examcard(dcm_file):
    '''read examcard embedded in DICOM file and return an XML string containing the raw SessionExamCard'''
    dcmFile = dcm.read_file(dcm_file)
    rawExamCard = dcmFile[0x2005,0x1132][0][0x2005,0x1144].value #read private examcard tag
    dcmExamCard = rawExamCard[:rawExamCard.find('\x00')]
    return dcmExamCard

def dcm_examcard_write(dcm_file):
    '''parse the SessionExamCard xml string from dcm_examcard and write to file'''
    dcmExamCard = dcm_examcard(dcm_file)
    dcmExamCardXml = open('dcmExamCard.xml', 'w')
    dcmExamCardXml.write(dcmExamCard)
    dcmExamCardXml.close()
    print 'Finished writing dcmExamCard.xml'
    return

def dcm_examcard_map(dcm_file):
    '''takes an examcard dicom file and returns a list of series names and their UIDs'''
    map = {}
    NAMESPACE = {'ec':'http://tempuri.org/XMLSchema.xsd'}
    if isSessionExamCard(dcm_file):
        dcmExamCard = dcm_examcard(dcm_file)
        dicomObject = dcm.read_file(dcm_file)
        parseExamCard = etree.fromstring(dcmExamCard)
        map[dicomObject.StudyInstanceUID] = parseExamCard.xpath('/ec:ExamCard/ec:Name/text()',
                                                                namespaces=NAMESPACE)[0]
        singleScans = parseExamCard.xpath('//ec:SingleScan',
                                          namespaces=NAMESPACE)
        for scan in singleScans:
            for uid in scan.xpath('./ec:SeriesUids',
                                  namespaces = NAMESPACE):
                if type(uid.text) is str:
                    map[uid.text] = (scan.xpath('./ec:Name/text()',
                                                namespaces = NAMESPACE)[0],
                                     scan.xpath('./ec:State/text()',
                                                namespaces = NAMESPACE)[0])
    return map


def soap_examcard(dcm_file):
    '''parse the raw SessionExamCard Blob and write the decoded XML SOAP SessionExamCard message'''
    dcmExamCard = dcm_examcard(dcm_file)
    parseExamCard = etree.fromstring(dcmExamCard)
    '''get the last element (examCardBlob) value of the XML object'''
    examCardBlob = parseExamCard[-1].text
    soapExamCard = b64decode(examCardBlob)
    return soapExamCard[:soapExamCard.find('\r\n\x00')]

def soap_examcard_write(dcm_file):
    soapExamCard = soap_examcard(dcm_file)
    soapExamCardXml = open('soapExamCard.xml', 'w')
    soapExamCardXml.write(soapExamCard)
    soapExamCardXml.close()
    print 'Finished writing soapExamCard.xml'
    return

def examcard2xml(dcm_file,libexamcard ='examcard2xml'): #examcard2xml is the libexamcard binary
    '''run libexamcard's examcard2xml function'''
    soapExamCard = soap_examcard(dcm_file)
    cache = open('.cache', 'w')
    cache.write(soapExamCard)
    cache.close()
    examcard2xml = sub.Popen([libexamcard, '.cache'], stdout=sub.PIPE)
    examCard = ''.join(examcard2xml.stdout)
    os.remove('.cache')
    return examCard

def examcard2xml_write(dcm_file,proj_space):
    examCardXml = examcard2xml(dcm_file)
    examCard = open(proj_space + '/ExamCard.xml', 'w')
    examCard.write(examCardXml)
    examCard.close()
    print 'Finished writing ExamCard.xml'
    return

###                                            ###    
# Jordi Huguet: XNAT pipeline util functions                            #
###                                            ###

def locate_examcards(directory_URI):
    '''recurse over all the directory tree-structure of the DICOM study and locate ExamCard objects'''
    examcardList = []
    for root,dirs,files in os.walk(directory_URI):
        if len(files) > 0:            
            for n in xrange(len(files)):            
                if isSessionExamCard(os.path.join(root,files[n])):
                    dcmExamCard = os.path.join(root,files[n])
                    print '[Debug] Found a session examcard! --> ', dcmExamCard
                    examcardList.append(dcmExamCard)                                
            
    return examcardList

def extract_examcard_write(dcm_file,output_location):
    '''extract ExamCard from DICOM file and save it as an XML at specified location'''
    #examcard_filename = os.path.splitext(os.path.basename(dcm_file))[0]
    examcard_filename = 'examcard_'
    #examcard_filename += str(index)
    '''parse the series number from the absolute path to compose the examcard filename'''
    examcard_filename += os.path.basename(os.path.dirname(dcm_file))
    examcard_filename += '.xml'
    
    examcard_fullfilename = os.path.join(output_location,examcard_filename)    
    soapExamCard = soap_examcard(dcm_file)
    try:
        with open(examcard_fullfilename, "w") as outfile:
            outfile.write(soapExamCard)
    except IOError:
        print '[Error] Unable to create file on disk'
        return
    finally: 
        outfile.close()
    
    return examcard_fullfilename

def main(dir_IN,dir_OUT):
    '''Main function: Locate, parse and extract recursively all available Examcard files'''    
    '''[@arg] dir_IN :: location where Examcard DICOM data is located'''    
    '''[@arg] dir_OUT :: location where Examcard XML data should be placed'''    
    
    dcm_examcards = locate_examcards(dir_IN)
    for index,item in enumerate(dcm_examcards):
        examcard = extract_examcard_write(item,dir_OUT)
        #print '[Debug] Finished extracting examcard at: ', examcard
        print '[Debug] Series acquired under the examcard: ', examcard
        map = (dcm_examcard_map(item))
        for indexm,itemm in enumerate(map):
            if (map[itemm][1] == 'Completed'):
                print '\t',(map[itemm][0]),' - ',itemm
        print ''

###                                            ###    
# Main()                                                                #
###                                            ###
print ''
print 'examcard.py :: Tool for recursively locate, parse and extract Philips EXAMCARD objects from DICOM files'
print ''

if len(sys.argv) == 1 or sys.argv[1] == '-h' or sys.argv[1] == '--h' or sys.argv[1] == '-help' or sys.argv[1] == '--help':
    print 'examcard <input directory> <output directory>'
    
elif sys.argv[1] == '-v' or sys.argv[1] == '--v' or sys.argv[1] == '-version' or sys.argv[1] == '--version':
    print '%s v%s' %('examcard', __version__)
    
elif len(sys.argv) == 3:    
    #usage: main(usr_pwd, host, xnatProject, directory)
    print '[Debug] Source directory of DICOM file-set: ', sys.argv[1]
    print '[Debug] Location of the extracted examcards: ', sys.argv[2]
    main(sys.argv[1],sys.argv[2])
    
else :
    print '[Error] Wrong command'
    print 'Examcard <input directory> <output directory>'
    print ''
    sys.exit(1)
    
sys.exit(0)
