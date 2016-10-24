#!/usr/bin/env python

# Created 2016-10-04, Jordi Huguet, Dept. Radiology AMC Amsterdam

####################################
__author__      = 'Jordi Huguet'  ##
__dateCreated__ = '20161004'      ##
__version__     = '0.1.1'         ##
__versionDate__ = '20161024'      ##
####################################

# qap_snapshot_creator.py
# Script for uploading QAP-generated SNAPSHOT imaging files to XNAT as assessment resources


# IMPORT FUNCTIONS
import os
import sys
import urllib
from wand.image import Image as image_magick


# FUNCTIONS
def get_file_extension(fileName):
    ''' Helper function for extracting the file extension suffix (uppercase) '''

    extension = (os.path.splitext(fileName)[1][1:]).upper()

    return extension


def find_pdf_files(qap_output_directory, scan_dirname):
    ''' Function that traverses all QAP output directory tree and locates scan-specific target PDF files to be processed '''
    ''' Returns a list of matched files '''

    found_files = []
    target_file_types = [ 'fd.pdf', 'mosaic.pdf' ]

    for root1, dirs1, files1 in os.walk(qap_output_directory):
        if scan_dirname in dirs1 :
            for root2, dirs2, files2 in os.walk(os.path.join(root1, scan_dirname)):
                for filename in files2 :
                    if filename in target_file_types :
                        found_files.append(os.path.join(root2, filename))

    return found_files


def convert_to_img(pdf_input_file):
    ''' For better embedding in web-pages, we will convert syntethic PDFs to PNG-formatted images '''
    ''' Returns full path name of generated image file '''

    img_output_filename = os.path.splitext(pdf_input_file)[0] + '.png'
    assert( not os.path.isfile(img_output_filename) )

    with image_magick(filename=pdf_input_file, resolution=300) as pdf_img:
        #keep good quality
        pdf_img.compression_quality = 100
        #save it
        pdf_img.save(filename=img_output_filename)

    return img_output_filename


def upload_snapshot_resource(xnat_connection,project,subject,experiment,assessment,resource_filepath):
    ''' Uploads an snapshot image resource to the XNAT QA assessor report '''

    resource_collection_label = 'SNAPSHOTS'

    # security check
    if not os.path.isfile(resource_filepath) :
        print '[error] %s is not a valid image file' %(resource_filepath)
        sys.exit(1)

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


# if __name__=="__main__" :

    # if len(sys.argv) != 7 :
        # sys.exit(1)
    # else :
        # usr_pwd = sys.argv[1]
        # hostname = sys.argv[2]
        # projectID = sys.argv[3]
        # experimentID = sys.argv[4]
        # assessorID = sys.argv[5]
        # qap_output_directory = sys.argv[6]


        # if not os.path.isdir(qap_output_directory):
            # print '[error] %s is not a valid directory' %(qap_output_directory)
            # sys.exit(1)
        # with xnatLibrary.XNAT(hostname,usr_pwd) as xnat_connection :
            # matched_results = find_pdf_files(qap_output_directory)
            # if matched_results :
                # for file in matched_results :
                    # png_file = convert_to_img(file)
                    # upload_snapshot_resource(xnat_connection,projectID,experimentID,subjectID,assessorID,png_file)
                    # os.remove(png_file)

    # sys.exit(0)
