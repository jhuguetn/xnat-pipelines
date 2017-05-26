# Automated facial identifiable traits removal (defacing) of anatomical MRI scan data

## Introduction
Due to the increasing concerns for subject privacy in neuroimaging field, the ability to automatically deidentify structural MR scan images so that they do not provide identifiable details is desirable. This pipeline wraps [mri_deface](https://surfer.nmr.mgh.harvard.edu/fswiki/mri_deface), a tool that uses models of nonbrain structures for removing potentially identifying facial features.

The mri_deface tool locates the subject's facial features and removes them without disturbing brain tissue. The algorithm was devised to work on T1-weighted structural MRI; it outputs a defaced structural image. 

Note I: The mri_deface algorithm is under the validation phase, use it at your own risk.
Note II: Differently from FreeSurfer suite, a license file is no longer necessary to use these tool.

All credits to the authors of mri_deface for their work. Cite this paper if using mri_deface standalone or via this pipeline: [A Technique for the Deidentification of Structural Brain MR Images](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2408762)

The mri_anat_deface pipeline is designed for automatically: 

1. fetch T1/anatomical scans in XNAT MRI sessions, note that pipeline supports data either in DICOM or NIFTI format
2. process the scans to obtain a defaced output image per each
3. and finally store back into XNAT the resulting images as additional resources (NIFTI files)

## TO-DO: Add pipeline workflow

## Requisites

- XNAT platform (1.6 or +) and XNAT pipeline engine.  

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
