#!/bin/env python

####################################
__author__      = 'Jordi Huguet'  ##
__dateCreated__ = '20170616'      ##
__version__     = '0.1.1'         ##
__versionDate__ = '20171016'      ##
####################################

# B1_nii_intercept_fix
# Fixes scale intercept values (using FSL tools) in wrongly converted B1 scan NIFTI files


# IMPORT FUNCTIONS
import os,sys
import nibabel
import numpy
import subprocess
import argparse


def process_B1_files(b1_indir, b1_outdir):
    
    in_files = [file for file in os.listdir(b1_indir) if os.path.isfile(os.path.join(b1_indir, file))]

    #load NIFTI files and parse their headers out
    for current_file in in_files :
        
        if current_file.endswith('.nii') or current_file.endswith('.nii.gz') :
        
            b1_img = nibabel.load(os.path.join(b1_indir,current_file))
            
            curr_slope = b1_img.dataobj.slope 
            curr_inter = b1_img.dataobj.inter
            
            #if curr_inter < 0 and (('e2_ph_1.nii' in current_file) or ('e2_ph_2.nii' in current_file)) :
            if curr_inter < 0 :
                # wrong intercept: let's do something (fix)
                
                data = b1_img.get_data()
                
                #print out some useful info (values of the scale intercept header attribute)
                print '[info] File: %s, Slope: %f, Intercept: %f' %(current_file, curr_slope,curr_inter)
                print '[info] Data range [%f : %f]' %(data.min(), data.max())
                
                #execute the bash script (FSL underneath) for creating a modified version of the image file
                bashScript = os.path.join(os.getcwd(),'B1_nii_intercept_fix.sh')
                bashCommand = "bash %s %f %s %s" %(bashScript,curr_inter, os.path.join(b1_indir,current_file), os.path.join(b1_outdir,current_file))
                process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
                output, error = process.communicate()
                
                #print output 
                #print error
                scaled_b1_img = nibabel.load(os.path.join(b1_outdir,current_file))
                scaled_slope = scaled_b1_img.dataobj.slope 
                scaled_inter = scaled_b1_img.dataobj.inter
                scaled_data = scaled_b1_img.get_data()
                print '[info] File: %s, Slope: %f, Intercept: %f' %(current_file, scaled_slope,scaled_inter)
                print '[info] Data range [%f : %f]' %(scaled_data.min(), scaled_data.max())
                print ''


def main():
    ''' main script function '''

    parser = argparse.ArgumentParser(description='Fix B1 scan NIFTI files')
    parser.add_argument('-indir', type=unicode, required=True, help='input directory name')
    parser.add_argument('-outdir', type=unicode, required=True, help='output directory name')
    args = parser.parse_args()

    process_B1_files(args.indir, args.outdir)
    
    
# TOP-LEVEL SCRIPT ENVIRONMENT
if __name__ == '__main__':
    main()


