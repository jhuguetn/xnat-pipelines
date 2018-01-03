# xnat-pipelines

## Intro
XNAT Pipeline-engine is a Java-based workflow framework nicely integrated (that's basically its inception purpose) in XNAT. Pipeline-engine uses XML-based workflow definitions for processing data hosted in XNAT by linking sequential activities or steps. 


## Main features
- Provides mechanisms for [batch-mode triggering](https://github.com/jhuguetn/xnat-scripts/tree/master/pipeline_launcher) pipeline instances (via REST API).
- Enables submission of jobs to a Distributed Resource Management (DRM) system supporting the Distributed Resource Management Application API (DRMAA) specification, e.g. [SGE](https://en.wikipedia.org/wiki/Oracle_Grid_Engine).  


## Content list
XNAT pipelines repository, see the [wishlist](https://github.com/jhuguetn/xnat-pipelines/wiki/Wishlist) for incomming apps.

* [ExamCard extractor](https://github.com/jhuguetn/xnat-pipelines/tree/master/examcardExtractor) :: Extracts Philips ExamCard objects embedded in DICOM object files
* [FreeSurfer](https://github.com/jhuguetn/xnat-pipelines/tree/master/freesurfer) :: FreeSurfer recon-all pipeline with XNAT assessor output with stats metrics
* [mricron](https://github.com/jhuguetn/xnat-pipelines/tree/master/mricron) :: DICOM and PARREC flavoured pipelines for imaging data conversion to NIFTI format (using dcm2nii)
* [Quality Assessment Protocol](https://github.com/jhuguetn/xnat-pipelines/tree/master/QAP) :: QA analysis on functional/structural MRI data
* [mricrogl](https://github.com/jhuguetn/xnat-pipelines/tree/master/mricrogl) :: New generation of DICOM-to-NIFTI format conversion pipeline (using dcm2niix)
* [DTI-preprocessing](https://github.com/jhuguetn/xnat-pipelines/tree/master/dti_preprocessing) ::  Compute preprocessing corrections on MRI DTI scans
* [MRI bias field correction](https://github.com/jhuguetn/xnat-pipelines/tree/master/bias_correction) :: correcting intensity non-uniformity (i.e. bias fields)
* [MRI anatomical defacer](https://github.com/jhuguetn/xnat-pipelines/tree/master/mri_anat_deface) :: Automated facial traits removal (defacing) of anatomical scan data.
* [qMRI](https://github.com/jhuguetn/xnat-pipelines/tree/master/qMRI) :: Calculate quantitative anatomical MRI (qMRI) mapping. qMRI provides MRI measures that are comparable across sites and time points. More background [here](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3677134). 


## Contributors
Jordi Huguet, Department of Neuroradiology & Brain Imaging Centre, AMC-UvA Amsterdam


## License
This work is licensed under the terms of the GNU GPLv3 license.


