#!/usr/bin/python

# Created 2016-08-09, Jordi Huguet, Dept. Radiology AMC Amsterdam

####################################
__author__      = 'Jordi Huguet'  ##
__dateCreated__ = '20160809'      ##
__version__     = '0.0.3'         ##
__versionDate__ = '20160920'      ##
####################################

# get_mri_data
# get suitable raw MRI scan data for computing QAP measuments (distinguishing between structural and functional scan types)


# IMPORT FUNCTIONS
import os
import sys
import StringIO
import urllib
import zipfile
import xnatLibrary

# FUNCTIONS
def get_scan_type_philips_info(xnat_connection,project,subjectID,experimentID, scan_id):
    ''' Figures out which type of MRI scans are contained in such session by querying XNAT for some Philips private DICOM attributes'''
    ''' Returns a dict with scansIDs and their Philips-specific attribute (values list) to be used afterwards for scan type detection'''

    # Use dcmdump service to pull out the scan DICOM attributes
    # compose the URL's resource path
    URL_path = '/data/services/dicomdump'
    # encode query options
    options = 'src=/archive/projects/%s/subjects/%s/experiments/%s/scans/%s&field=2005140f' %(project,subjectID,experimentID,scan_id)
    # compose the whole URL string
    URL = xnat_connection.host + URL_path + '?' + options
    # query XNAT dcmdump service
    dcmdump_result,response = xnat_connection.queryURL(URL, options)

    # get the relevant DICOM attribute value "Acquisition Contrast" : Philips private nested tag (2005,140f).(0008,9209)
    # get the relevant DICOM attribute value "Pulse Sequence Name"  : Philips private nested tag (2005,140f).(0018,9005)
    matching_dcm_attribute_value1 = [current_dump['value'] for current_dump in dcmdump_result if current_dump['tag2'] == '(0008,9209)']
    matching_dcm_attribute_value2 = [current_dump['value'] for current_dump in dcmdump_result if current_dump['tag2'] == '(0018,9005)']
    assert(len(matching_dcm_attribute_value1) <= 1 and len(matching_dcm_attribute_value2) <= 1)

    # compose a dict with scanID and the values of the Philips private attributes (replace unicode by string)
    if ( len(matching_dcm_attribute_value1) == 1 and len(matching_dcm_attribute_value2) == 1 ):
        #acquisitionTypes[str(scan_id)] = [ str(matching_dcm_attribute_value1[0]), str(matching_dcm_attribute_value2[0]) ]
        scan_type_params = [ str(matching_dcm_attribute_value1[0]), str(matching_dcm_attribute_value2[0]) ]
    else:
        # either is not Philips or has been anonymized, thus private group 0x2005 removed
        scan_type_params = None

    return scan_type_params


def is_func_scan(philips_scan_type_info, scan_type, scanID):

    functional_type_tokens = ['resting', 'rsmri', 'fmri']
    is_func = None

    if philips_scan_type_info :
    # Philips dataset
        acq_contrast,pulse_seq = philips_scan_type_info
        if acq_contrast == 'PROTON_DENSITY' and 'EPI' in pulse_seq :
            is_func = True
    else :
    # Not Philips data or private group 0x2005 removed/emptied'
        if [scanID for ftype in functional_type_tokens if ftype in scan_type.lower()] :
            # let's asume it is a functional scan
            is_func = True

    return is_func


def is_struct_scan(philips_scan_type_info, scan_type, scanID):

    structural_type_tokens = ['t1', 'adni', 'mprage']
    is_struct = None

    if philips_scan_type_info :
    # Philips dataset
        acq_contrast,pulse_seq = philips_scan_type_info
        if acq_contrast == 'T1' and 'T1' in pulse_seq :
            is_struct = True
    else :
    # Not Philips data or private group 0x2005 removed/emptied'
        if [scanID for ftype in structural_type_tokens if ftype in scan_type.lower()] :
            # let's asume it is an structural scan
            is_struct = True

    return is_struct


def get_scans_list(connection,project,subjectID,experimentID,required_type):
    ''' Given an XNAT connection and project>subject>experiment IDs, return a list of scans (IDs) which are of required type '''
    ''' Being required_type either functional or structural types'''

    process_scan_list = []

    # get FULL scan list of the given session
    options = { 'columns' : 'ID,type' }
    scans = connection.getScans(experimentID, options)

    for scanID in scans :
        # first get Philips scan type info (if available!)
        philips_scan_type_info = get_scan_type_philips_info(connection,project,subjectID,experimentID,scanID)

        if 'anat' == required_type.lower() and is_struct_scan(philips_scan_type_info,scans[scanID]['type'],scanID):
            process_scan_list.append(scanID)

        elif 'func' == required_type.lower() and is_func_scan(philips_scan_type_info,scans[scanID]['type'],scanID):
            process_scan_list.append(scanID)

    return process_scan_list


def download_scan_list_files(connection,experimentID,scan_list,resource_format,out_dir):
    ''' Given an XNAT connection, an experiment ID and a list of scans, download such scans' data to the specified output directory '''

    # convert Python list to CSV string
    scans_list_string = ",".join(scan_list)
    URL = connection.host + '/data/experiments/' + experimentID + '/scans/' + scans_list_string + '/resources/' + resource_format + '/files'

    # add URL option to download all scan files in a single compressed file
    options = {}
    options['format'] = 'zip'
    options['structure'] = 'legacy'
    options = urllib.urlencode(options)

    # GET the resource files blob
    responseOutput,_ = connection.getResource(URL, options)

    # extract the content of the ZIP file to the given output location
    zfile = zipfile.ZipFile(StringIO.StringIO(responseOutput))
    zfile.extractall(out_dir)

    return


def main():

    if len(sys.argv) != 8 :
        print '[error] No valid arguments supplied'
        sys.exit(1)

    usr_pwd = sys.argv[1]
    hostname = sys.argv[2]
    project = sys.argv[3]
    subjectID = sys.argv[4]
    experimentID = sys.argv[5]
    required_type = sys.argv[6]
    output_directory = sys.argv[7]

    resource_format = 'DICOM,NIFTI'

    #basic checkings on output directory status
    if not os.path.isdir(output_directory):
        print '[error] Download location specified is not a valid directory'
        sys.exit(1)

    # connect to XNAT
    with xnatLibrary.XNAT(hostname,usr_pwd) as xnat_connection :

        # get a list of affected scans for the given imaging session
        process_scan_list = get_scans_list(xnat_connection,project,subjectID,experimentID,required_type)

        # if the list is empty, no valid scans found for the given imaging session, close and exit
        if not process_scan_list :
            print '[error] Unable to find a suitable %s scan for %s' %(required_type,experimentID)
            sys.exit(1)

        # retrieve the scans from XNAT
        download_scan_list_files(xnat_connection,experimentID,process_scan_list,resource_format,output_directory)


if __name__=="__main__" :

    main()
    sys.exit(0)

