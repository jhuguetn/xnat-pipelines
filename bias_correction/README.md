# MRI bias field correction pipeline (correcting intensity non-uniformity, i.e. bias fields)

## Introduction
In MRI images, intensity inhomogeniety caused by magnetic settings, patient position and/or other factors is usual. This pipeline can be used to correct such intensity non-uniformity (i.e. bias fields).

MRI bias field correction pipeline uses [mri_nu_correct.mni](http://ftp.nmr.mgh.harvard.edu/pub/docs/wiki/mri_nu_correct.mni.help.xml.html) tool from FreeSurfer that wraps nu_correct from the suite [Non-parametric Non-uniformity Normalization (N3)](http://www.bic.mni.mcgill.ca/software/N3/), Montreal Neurological Institute. All credits to the authors for their respective work.

The bias-correction pipeline is designed for automatically: 

1. fetch FLAIR scans in XNAT MRI sessions, note that pipeline supports data either in DICOM or NIFTI format
2. compute the bias field corrections
3. and finally store back into XNAT the resulting processed images as additional resources (NIFTI files)

## TO-DO: Add pipeline workflow

## Requisites

- XNAT platform (1.6 or +) and XNAT pipeline engine.  

- FreeSurfer (5.3 or +) must be installed

## Installation procedure

* Get the lattest version of the pipeline(s) as follows: 

  ```
  git clone https://github.com/jhuguetn/xnat-pipelines.git {pipeline catalog location}
  ```
  
* Place it in a location of choice (make sure is accessible/executable by the XNAT pipeline engine).
* An XNAT administrator should [enable the pipeline(s)](https://wiki.xnat.org/display/XNAT16/Installing+Pipelines+in+XNAT) to make it available for the whole XNAT setting.
* As a project owner, follow [these instructions](https://wiki.xnat.org/display/XNAT16/Working+with+Processing+Pipelines) to enable the pipeline for a project of yours.

## Running the pipeline

Once enabled, pipeline can be easily triggered for an imaging session in the project.

* From the XNAT GUI, see [here](https://wiki.xnat.org/display/XNAT16/Working+with+Processing+Pipelines#WorkingwithProcessingPipelines-RunningPipelinesonyourProject)

* Programmatically (RESTful API), via an HTTP-post command at the following resource: 

  ```
  [POST] /data/archive/projects/{PROJECT_ID}/pipelines/{PIPELINE_ID}/experiments/{EXPERIMENT_ID}
  ```
  
  See also [here](https://github.com/jhuguetn/xnat-scripts/tree/master/pipeline_launcher).

Note that pipeline can also be initially setup to launch automatically when session is archived.

## Questions/Comments?

Submit an issue, fork and/or PR. Alternatively, reach me at j.huguet(at)amc.uva.nl
