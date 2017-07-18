#!/usr/bin/env python

# Created 2017-07-07, Jordi Huguet, Dept. Radiology AMC Amsterdam

####################################
__author__      = 'Jordi Huguet'  ##
__dateCreated__ = '20170707'      ##
__version__     = '0.2.3'         ##
__versionDate__ = '20170718'      ##
####################################

# get_scan_details
# Given an MRI scan image, get some scan details for later usage (qMRI pipeline analysis)


# IMPORT FUNCTIONS
import os
import sys
import json
import fnmatch
import traceback
import xnatLibrary
import urllib
import zipfile
import StringIO
import subprocess
import shutil


# FUNCTIONS
def get_dcm_echotime_values(file) :
    ''' Given a filename of a MRI DICOM file, parse out the existing Echo Time value(s) '''
    ''' Return a list of TE values found '''
    
    #execute the bash script (DCMTK underneath) for getting the TE values
    #bashScript = os.path.join(os.getcwd(),'dcmdump_echotimes.sh')
    command = "dcmdump +P EchoTime %s" %file
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    raw_output, error = process.communicate()  
    
    output = raw_output.splitlines()
    
    # trim unnecessary stuff out (just keep TE values) and remove duplicates
    te_values = []
    for i,line in enumerate(output) :
        trimmed_line = str(line.split('[')[1].split(']')[0])
        if trimmed_line not in te_values:
            te_values.append(trimmed_line)
        
    return te_values
    

def split_numlist_by_proximity(numerical_list):
    ''' Helper function for clustering/spliting a numerical valued list into 2 based on neighbourhood proximity '''
    ''' Returns the position of last element of the first sublist '''
    
    #define the maximum difference item i and item i+1 (position in the list and absolute differential value)
    max_diff = [ -1, 0 ]
    
    for i,value in enumerate(numerical_list):
        if i+1 < len(numerical_list):
            if ( abs(value-numerical_list[i+1]) > max_diff[1] ) :
                max_diff = [i, abs(value-numerical_list[i+1])]
    
    return max_diff[0]
    

def find_dir(name, path):
    ''' Helper function mimicking the behaviour of find command for directories'''
    ''' Search for the first occurrence that matches a directory with an specific name, case sensitive '''
    
    for root, dirs, files in os.walk(path):
        if name in dirs:
            return os.path.join(root, name)
    
    return None


def find_files(pattern, path):
    ''' Helper function mimicking the behaviour of find command for files'''
    ''' Search for the all matching occurrences for files, case sensitive '''
    
    result = []
    
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                result.append(os.path.join(root, name))
    
    return result

    
def parse_scan_dir_name(directory_name):
    ''' Helper function that extracts scan ID and type from directory name '''
    
    scan_ID, scan_type = os.path.basename(directory_name).split('-', 1)
    
    return scan_ID, scan_type


def query_scan_details(connection, experimentID, scanID):
    ''' Atomic function for fetching scan details '''
    ''' Expects an XNAT connection, an XNAT image session unique ID, an scan ID ''' 
    
    # compose the URL's resource path
    URL_path = '/data/experiments/%s/scans/%s' %(experimentID, scanID)
    # encode query options
    options = 'format=json'
    # compose the whole URL string
    URL = connection.host + URL_path# + '?' + options
    # query XNAT 
    result,response = connection.getResource(URL, options)
    
    scan_data = json.loads(result)['items'][0]
    
    flip_angle = ""
    tr = ""
    te = {}
        
    if 'parameters/flip' in scan_data['data_fields']:
        flip_angle = scan_data['data_fields']['parameters/flip']
    if 'parameters/tr' in scan_data['data_fields']:
        tr = scan_data['data_fields']['parameters/tr']
    if 'parameters/te' in scan_data['data_fields'] :
        te['SingleEcho'] = scan_data['data_fields']['parameters/te']
    else : 
        try :
            # case TE is  empty since is a multiEcho:
            children_items = scan_data['children'][0]
            for child in children_items['items'] :
                if 'multiecho' in (child['data_fields']['name']).lower() :
                   te[str(child['data_fields']['name'])] = str(child['data_fields']['addField'])
        except KeyError as e:
            print '[Debug] query_scan_details(): No multiEcho info found for %s - %s' %(experimentID,scanID)
        
    return flip_angle,tr,te
    
    
def create_scan_details_struct(file_list, flip_angle, tr, te, image_type):
    ''' Create a dict structure with the scan file details '''
    
    scan_files_struct = {}
    
    file_list.sort(key=lambda f: int(filter(str.isdigit, f)))           
    sorted_te_keys = te.keys()
    sorted_te_keys.sort(key=lambda f: int(filter(str.isdigit, f)))
    
    for i,file in enumerate(file_list) :
        file_dirname = os.path.dirname(file)
        file_basename = os.path.basename(file)
        file_extension = ''
        
        if file_basename[-7:].lower() == '.nii.gz' :
            file_basename = file_basename[:-7]
            file_extension = '.nii.gz'
        elif file_basename[-4:].lower() == '.nii' :
            file_basename = file_basename[:-4]
            file_extension = '.nii'
        
        scan_files_struct[file_basename] = {'dirname' : file_dirname, 'flip_angle' : flip_angle, 'tr' : tr }                    
        if len(te) == 1 :
            scan_files_struct[file_basename].update({'te': te['SingleEcho']})
        else :
            scan_files_struct[file_basename].update({'te': te[sorted_te_keys[i]]})
            
        # WARNING: renaming will come later!                    
        #if file_basename[-5] == '_0000' :
        #    # is a magnitude NIFTI image created with fslsplit
        #    filename = file_basename[:-5] + '_M' + file_extension
        #    os.rename(file, os.path.join(file_dirname,filename))
        #elif file_basename[-5] == '_0001' :
        #    # is a phase NIFTI image created with fslsplit
        #    filename = file_basename[:-5] + '_P' + file_extension
        #    os.rename(file, os.path.join(file_dirname,filename))
        #
        #elif fnmatch.fnmatch(file_basename, '*_e*_ph_*') :
        #    dir_files = [name for name in os.listdir(file_dirname) if (os.path.isfile(os.path.join(file_dirname, name)) and ('.nii' in name))]
        #    dir_files.sort(key=lambda f: int(filter(str.isdigit, f)))
        #    num_files = len(dir_files)
        #    
        #    if dir_files.index(file) < num_files/2 :
        #        # dcm2niix/mricrogl tool codes magnitude images first and then phase ones
        #        os.rename(file, os.path.join(file_dirname,filename))
        
    return scan_files_struct
    
    
def get_scans_details(connection,experimentID,in_directory):
    ''' Given an XNAT connection and downloaded datasets pull out some scan details '''
    
    # find scans subdirectory in the main input directory
    scans_dir = find_dir('scans', in_directory)
    assert(scans_dir)
    
    # loop over scan directories 
    for scan_dir in os.listdir(scans_dir) :
        
        scan_abs_dir = os.path.join(scans_dir, scan_dir)
        
        # parse scan ID/type from meaningful directory names
        scan_id, scan_type = parse_scan_dir_name(scan_abs_dir)
        
        # determine what kind of image the current scan is (either Phase, Magnitude or both combined)
        t1_image_type = None
        
        if fnmatch.fnmatch(scan_type, '*T1*PM') :
            t1_image_type = "PHASE_MAGNITUDE"
        elif fnmatch.fnmatch(scan_type, '*T1*M') :
            t1_image_type = "MAGNITUDE"
        elif fnmatch.fnmatch(scan_type, '*T1*P') :
            t1_image_type = "PHASE"
        
        scan_details = {}
            
        if t1_image_type :
            print scan_id, scan_type, t1_image_type
            
            # find all NIFTI files
            scan_nii_files = find_files('*.nii*', scan_abs_dir)
            
            # get scan details needed (FLIP, TR and TE) 
            flip_angle,tr,te = query_scan_details(connection, experimentID, scan_id)
            
            if not te or len(te) < 1 :
                # Enhanced DICOM scan? Deal with the issue
                te = {}
                
                # Get the DICOMs
                dicom_download_location = os.path.join(scan_abs_dir,'resources/DICOM')
                if not os.path.exists(dicom_download_location):
                    os.makedirs(dicom_download_location)
                download_dicom_files(connection,experimentID,scan_id,dicom_download_location)
                
                # find all DICOM files
                scan_dcm_files = find_files('*.dcm', dicom_download_location)
                
                te_values = []
                for dcm_file in scan_dcm_files :
                    current_file_te_values = get_dcm_echotime_values(dcm_file)
                    
                    for te_value in current_file_te_values :
                        if te_value not in te_values :
                            te_values.append(float(te_value))
                
                #print '[Debug] MULTI EchoTime %s' %te_values
                # create a dict with sorted TE values
                for i,te_value in enumerate(sorted(te_values)) :
                    key_name = 'MultiEcho_TE%s' %(str(i+1))
                    te[key_name] = te_value
                
                # finally remove the downloaded DICOM directory tree
                shutil.rmtree(dicom_download_location)
                
                ### ------ ###
                #check images to TE values consistency
                assert( (len(te) == len(scan_nii_files) and t1_image_type != "PHASE_MAGNITUDE") or (len(scan_nii_files)%2 == 0 and len(te) == len(scan_nii_files)/2) )
                
                if len(te) == len(scan_nii_files) and t1_image_type == "MAGNITUDE":
                    # magnitude case --> good to go!
                    scan_details = create_scan_details_struct(scan_nii_files, flip_angle, tr, te, t1_image_type)
                    
                    #if t1_image_type == "PHASE" : do nothing
                        
                elif len(te) == len(scan_nii_files)/2 :
                    # phase and magnitude case
                    
                    # detect and exclude phase images (ASSUMPTION: phase images are double size the magnitude ones)
                    # create an ordered struct with filenames and sizes of the given files
                    sizes_struct = { file : os.path.getsize(file) for file in scan_nii_files }
                    sizes_sorted_tuple = sorted(sizes_struct.items(), key=lambda x:x[1])
                    sorted_sizes_list = [i[1] for i in sizes_sorted_tuple]
                    
                    # determine the largest size gap between neighbouring ordered files        
                    last_item_index = split_numlist_by_proximity(sorted_sizes_list)
                    assert(last_item_index > -1)
                    
                    for i,tuple in enumerate(sizes_sorted_tuple):
                        #discard all phase image files        
                        if i > last_item_index :
                            # big file size difference --> phase image
                            scan_nii_files.remove(tuple[0])
                    
                    assert(len(te) == len(scan_nii_files))
                    scan_details = create_scan_details_struct(scan_nii_files, flip_angle, tr, te, t1_image_type) 
                
                
            elif len(te) == 1 :
                assert 'SingleEcho' in te.keys()
                
                scan_details = create_scan_details_struct(scan_nii_files, flip_angle, tr, te, t1_image_type)
                #print '[Info] single EchoTime'
                
            else :
                
                #check images to TE values consistency
                assert( (len(te) == len(scan_nii_files) and t1_image_type != "PHASE_MAGNITUDE") or (len(scan_nii_files)%2 == 0 and len(te) == len(scan_nii_files)/2) )
                
                if len(te) == len(scan_nii_files) and t1_image_type == "MAGNITUDE":
                    # magnitude case --> good to go!
                    scan_details = create_scan_details_struct(scan_nii_files, flip_angle, tr, te, t1_image_type)
                    
                    #if t1_image_type == "PHASE" : do nothing
                        
                elif len(te) == len(scan_nii_files)/2 :
                    # phase and magnitude case
                    
                    # detect and exclude phase images (ASSUMPTION: phase images are double size the magnitude ones)
                    # create an ordered struct with filenames and sizes of the given files
                    sizes_struct = { file : os.path.getsize(file) for file in scan_nii_files }
                    sizes_sorted_tuple = sorted(sizes_struct.items(), key=lambda x:x[1])
                    sorted_sizes_list = [i[1] for i in sizes_sorted_tuple]
                    
                    # determine the largest size gap between neighbouring ordered files        
                    last_item_index = split_numlist_by_proximity(sorted_sizes_list)
                    assert(last_item_index > -1)
                    
                    for i,tuple in enumerate(sizes_sorted_tuple):
                        #discard all phase image files        
                        if i > last_item_index :
                            # big file size difference --> phase image
                            scan_nii_files.remove(tuple[0])
                    
                    assert(len(te) == len(scan_nii_files))
                    scan_details = create_scan_details_struct(scan_nii_files, flip_angle, tr, te, t1_image_type)                    
                    
        if scan_details :
            for item in scan_details :
                
                json_filename = os.path.join(scan_details[item]['dirname'], item+'.json')
                assert( not os.path.isfile(json_filename) )
                
                with open(json_filename, 'w') as json_file:
                    json.dump(scan_details[item], json_file, sort_keys=True, indent=4)                
                    print '[Info] JSON file created for item!'
    return 


def download_dicom_files(connection,experimentID,scan,out_dir):
    ''' Quick fix for grabbing the TE values on those cases that neither NIFTI nor XNAT has any clue about their value(s) '''

    URL = connection.host + '/data/experiments/' + experimentID + '/scans/' + scan + '/resources/DICOM/files'

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

    header_msg = '%s - v%s' %(os.path.basename(sys.argv[0]),__version__)
    
    if len(sys.argv) != 5 :
        print '[error] No valid arguments supplied (%s)' %header_msg
        sys.exit(1)

    usr_pwd = sys.argv[1]
    hostname = sys.argv[2]
    expID = sys.argv[3]
    in_directory = sys.argv[4]

    #basic checkings
    if not os.path.isdir(in_directory):
        print '[error] Input data location specified is not a valid directory (%s)' %in_directory
        sys.exit(1)
    
    try:
        with xnatLibrary.XNAT(hostname,usr_pwd) as xnat_connection :

            get_scans_details(xnat_connection,expID,in_directory)            
    
    except xnatLibrary.XNATException as xnatErr:
        print '[error] XNAT-related issue(%s): %s' %(header_msg,xnatErr)
        sys.exit(1)
    except Exception as e:
        print '[Error]', e	
        print(traceback.format_exc())
        sys.exit(1)

if __name__=="__main__" :

    main()
    sys.exit(0)
