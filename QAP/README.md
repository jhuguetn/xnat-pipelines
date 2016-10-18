#QAP pipelines (structural/functional MRI QA analysis)

##Introduction
QAP contains 2 XNAT pipelines (qap_anat_processing and qap_fmri_processing) for computing QAP-related Quality Assessment metrics. Both pipelines share most of its resources thus they are logically and phisically kept in the same location. 

[Quality Assessment Protocol](http://preprocessed-connectomes-project.org/quality-assessment-protocol/) (QAP) is a Python-based package for computing functional and anatomical MRI data quality measures.
More information about the QAP computed metrics/measurements can be found [here] (http://preprocessed-connectomes-project.org/quality-assessment-protocol/#taxonomy-of-qa-measures).

The QAP pipelines are designed for automatically: 
0. fetch suited MRI scan data from XNAT instance given an MRSession
0. analyse structural and/or functional MRI running QAP tools
0. and finally storing back into XNAT the resulting measuments as derived but linked data (image session assessments)

## qap_anat_processing:
Analizes the quality of structural/anatomical MRI scans. Pipeline automatically looks for T1, ADNI or MPRAGE alike scans to process.

## qap_fmri_processing:
Analizes the quality of functional MRI scans, either or both in the temporal and the spatial domain. Pipeline automatically looks for fMRI, RESTING, rsMRI alike scans to process.

## Requisites

* QAP package (1.0.4 or +) and its prerequisites should be installed in the system before installing these XNAT pipelines.

* The QAP pipelines ingest computed QA metrics to XNAT database as customized data-types. Thus, [QAPdata module](https://github.com/jhuguetn/xnat-modules/tree/master/QAPdata-0.4) must be conveniently installed in the XNAT instance before running such pipelines. QAPdata module aims at modelling and structuring QAP measurements into custom XNAT data-types.

* Python version 2.7.X is required for running the pythonic scripts. Additionally, Wand (ImageMagick), urllib, lxml and httplib Python modules are also needed.

##Installation procedure

Get the lattest version of the pipeline(s) as follows: 
  ```
  git clone https://github.com/jhuguetn/xnat-pipelines.git {pipeline catalog location}
  ```

## Running the script:
  
##Questions/Comments?

Submit an issue, fork and/or PR. Alternatively, reach me at j.huguet(at)amc.uva.nl
