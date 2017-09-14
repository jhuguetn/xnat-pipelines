#!/usr/bin/env python

# Created 2017-09-14, Jordi Huguet, Dept. Radiology AMC Amsterdam

####################################
__author__      = 'Jordi Huguet'  ##
__dateCreated__ = '20170914'      ##
__version__     = '0.1.1'         ##
__versionDate__ = '20170914'      ##
####################################

# qmri_output_ingestor.py
# load csv file, parse out all qMRI stats found, compose XNAT-compliant XML blobs and upload them to XNAT as assessments


# IMPORT FUNCTIONS
import os
import sys
import csv
import urllib
import traceback
from lxml import etree
from datetime import datetime
import xnatLibrary
#import qap_snapshot_creator


# GLOBAL NAMESPACES
ns_xnat = { 'xnat' : 'http://nrg.wustl.edu/xnat' }


# FUNCTIONS
def get_file_extension(fileName):
    ''' Helper function for extracting the file extension suffix (uppercase) '''

    extension = (os.path.splitext(fileName)[1][1:]).upper()

    return extension
    
    
def normalize_string(data):
    '''Helper function for replacing awkward chars for underscores'''
    '''Returns a normalized string valid as XNAT identifier/label/name'''

    data = data.replace("/", " ")
    data = data.replace(",", " ")
    data = data.replace(".", " ")
    data = data.replace("^", " ")
    data = data.replace(" ", "_")

    return data


def get_scan_type_xnat(xnat_connection,projectID,subjectName,experimentName,scanID):
    ''' Helper function to get the type of an existing scan resource in an XNAT imaging session '''
    ''' Returns a scan type definition '''

    #compose the URL for the REST call
    URL = xnat_connection.host + '/data/projects/%s/subjects/%s/experiments/%s/scans' %(projectID,subjectName,experimentName)

    #encode query options
    query_options = {}
    query_options['format'] = 'json'
    query_options = urllib.urlencode(query_options)

    #do the HTTP query
    response_data,response = xnat_connection.queryURL(URL,query_options)

    scan_type = [item['type'] for item in response_data if item['ID'] == scanID]
    assert len(scan_type) == 1

    return str(scan_type[0])


def upload_snapshot_resource(xnat_connection,project,subject,experiment,assessment,resource_filepath):
    ''' Uploads an snapshot image resource to the XNAT assessor report '''

    resource_collection_label = 'SNAPSHOTS'

    extension = get_file_extension(resource_filepath)
    resource_file_name = os.path.basename(resource_filepath)

    # compose main URL for the REST call
    URL =  '%s/data/projects/%s/subjects/%s/experiments/%s/assessors/%s' %(xnat_connection.host,project,subject,experiment,assessment)

    # compose URL part for the creation of a file resource collection and file resource itself
    sURL = URL + '/resources/%s/files/%s' %(resource_collection_label,resource_file_name)

    # Requested reconstruction could not be found (HTTP status code #404)!
    if xnat_connection.resourceExist(URL).status == 404 :
        print '[error] assessment %s not found' %(URL)
        sys.exit(1)

    if xnat_connection.resourceExist(sURL).status == 200 :
        print '[error] XNAT resource %s already existing' %(sURL)
        sys.exit(1)
    else:
        opts_dict = { 'format': extension, 'content': os.path.splitext(resource_file_name)[0].upper() }

        #Convert the options to an encoded string suitable for the HTTP request
        opts = urllib.urlencode(opts_dict)
        resp = xnat_connection.putFile(sURL, resource_filepath, opts)

        if resp.status != 200 :
            print '[error] Unable to create resource at %s' %(sURL)
            sys.exit(1)
    
    return

    
def upload_to_XNAT(xnat_connection,project,subject,session,assessor,xml_data,dateType_ID):
    '''Uploads an XML object representing an image-related assessment dataType instance'''
    '''Returns the unique ID of the created assessment'''

    #compose the URL for the REST call
    URL = xnat_connection.host + '/data/projects/'
    URL += project
    URL += '/subjects/'
    URL += subject
    URL += '/experiments/'
    URL += session
    URL += '/assessors/'
    URL += assessor

    if xnat_connection.resourceExist(URL).status == 200 :
        raise xnatLibrary.XNATException('Assessment with same name %s already exists' %assessor )
    else:
        #encode query options
        opts_dict = {}
        #opts_dict['xsiType'] = '%s' %dateType_ID
        opts_dict['inbody'] = 'true'
        opts = urllib.urlencode(opts_dict)

        # upload the XML data object via the proper XNAT REST API call
        resp,experiment_uid = xnat_connection.putData(URL, xml_data, opts)

        if resp.status == 201 :
            print '[info] Assessment %s (UID: %s) of type %s successfully created' %(assessor,experiment_uid,dateType_ID)

    return experiment_uid


def create_xml_header(namespace, main_object_id):
    ''' Helper for composing the header of an XML element containing the XNAT output data '''
    ''' Returns an etree structure (lxml module)'''

    # Start printing the XML document.
    xmlHeader_preamble = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xmlHeader_preamble += '<!-- XNAT XML generated by %s - %s on %s -->' %(os.path.basename(sys.argv[0]),__author__,str(datetime.now().replace(microsecond=0)))
    xmlHeader_start = ( '<'+namespace+ ':' + main_object_id+' '
                        'xmlns:'+namespace+'="http://nrg.wustl.edu/'+namespace+'" '
                        'xmlns:xnat="http://nrg.wustl.edu/xnat" '
                        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">' )
                        #'xsi:schemaLocation= ...">' )
    xmlHeader_end = '</'+namespace+ ':' + main_object_id+'>'

    xml_header = xmlHeader_preamble + '\n' + xmlHeader_start + '\n' + xmlHeader_end
    root_xml_element = etree.fromstring(xml_header)

    return root_xml_element


def add_xml_subElement(root_elem, namespace_uri, elem_name, elem_value):
    ''' Helper for creating XML object sub-elements and populating them '''
    ''' Returns an etree subelement (lxml module)'''

    elem = etree.SubElement(root_elem, "{%s}%s" %(namespace_uri,elem_name))
    elem.text = str(elem_value)

    return elem


def add_xml_attributes(elem, attributes):
    ''' Helper for creating XML object sub-elements and populating them '''
    ''' Returns an etree subelement (lxml module)'''

    for attribute_key in attributes.keys() :
        elem.attrib[attribute_key]=attributes[attribute_key]

    return elem


def populate_xml_obj(xml_root_elem, data, namespace, xml_element_type):
    ''' Function for inserting computed qMRI measurements into an (XNAT schema-compliant) XML object '''
    ''' Returns an XML root element populated with all data '''

    add_xml_subElement(xml_root_elem, ns_xnat['xnat'], 'date', datetime.now().date())
    add_xml_subElement(xml_root_elem, ns_xnat['xnat'], 'time', datetime.now().replace(microsecond=0).time())

    # Add computed measurements to XML object
    for measure in data.keys():
        # if a root XML element measure, just add the subelement
        add_xml_subElement(xml_root_elem, namespace.values()[0], measure.lower(), data[measure])

    return xml_root_elem


def create_xml_obj(data,xml_element_type):
    ''' main function for the creation of the XNAT-compliant XML object '''
    ''' Returns an XML root element populated with all derived data '''

    namespace,dataType_ID = xml_element_type.split(':')
    current_ns = { namespace : 'http://nrg.wustl.edu/'+namespace }

    # create & populate data into newly-created XML object (XNAT dataType schema compliant)
    xml_elem = create_xml_header(namespace,dataType_ID)
    xml_elem = populate_xml_obj(xml_elem, data, current_ns, xml_element_type)
    
    return xml_elem


def parse_csv_file(csv_filepath):
    ''' Parse out a CSV-formatted file to a python structure (list of dictionaries) '''
    ''' Each row entry will be coded as a dictionery (key = header) and all appended in a returned list '''

    rows_dict_list = []

    with open(csv_filepath, mode='r') as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            rows_dict_list.append(dict(row))

    return rows_dict_list


def main (argument_list):

    header_msg = '%s - v%s' %(os.path.basename(argument_list[0]),__version__)

    if len(argument_list) != 7 :
        print '[error] No valid arguments supplied (%s)' %header_msg
        sys.exit(1)

    # input argument list
    usr_pwd = argument_list[1]
    hostname = argument_list[2]
    project = argument_list[3]
    subject = argument_list[4]
    session = argument_list[5]
    csv_input_file = argument_list[6]
    
    # check the main XML element type (XNAT datatype)
    xml_element_type = 'AMCZ0:qMRIData'
    
    # parse out data from CSV file containing results generated by qMRI run
    parsed_results = parse_csv_file(csv_input_file)
    #parsed_results = fix_results_type(parsed_results)

    # connect to XNAT
    try:
        with xnatLibrary.XNAT(hostname,usr_pwd) as xnat_connection :

            # for each entry (row) in the results file, create an XML object instantiating an XNAT assessment/experiment
            for scan_results in parsed_results:

                xml_element = create_xml_obj(scan_results,xml_element_type)

                # Do some magic :: upload xml object into XNAT (instantiate a new dataType object)
                assessment_label = normalize_string( session + '_' + xml_element_type.split(':')[1] )
                assessment_uid = upload_to_XNAT(xnat_connection,project,subject,session,assessment_label,etree.tostring(xml_element),xml_element_type)
                
                # quality control image upload
                output_directory = os.path.dirname(os.path.realpath(csv_input_file))
                qc_image_file = os.path.join(output_directory, 'qmri_fits.png')
                if os.path.isfile(qc_image_file) :
                    upload_snapshot_resource(xnat_connection,project,subject,session,assessment_uid,qc_image_file)
                

    except xnatLibrary.XNATException as xnatErr:
        print '[error] XNAT-related issue(%s): %s' %(header_msg,xnatErr)
        sys.exit(1)

    except Exception as e:
        print '[error]', e
        print(traceback.format_exc())
        sys.exit(1)

# TOP-LEVEL SCRIPT ENVIRONMENT
if __name__=="__main__" :

    main(sys.argv)
    sys.exit(0)
