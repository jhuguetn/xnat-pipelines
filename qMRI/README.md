# qMRI pipeline (quantitative anatomical MRI mapping)

## Introduction
qMRI is subdivided in 3 XNAT pipelines:

- qMRI-dcm2niix
   - convert enhanced to classic dicom
   - convert dicom to nifti
   - split merged nifti’s in separate volumes
   - fix scale slope/intercept of T1-volumes (heuristic)
- qMRI-convertB1
   - identify on-scanner computed B1-map, and fix scale slope/intercept
   - compute B1 if non-existent
- qMRI (core)
   - coregistration of 2 T1 volumes
   - masking
   - fitting
   - GM/WM segmentation
   - compute summary metrics
 
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

Completed pipeline will generate imaging assessments with a full report of the analysis performed. 

Note that pipeline can also be initially setup to launch automatically when session is archived.

## Questions/Comments?

Submit an issue, fork and/or PR. Alternatively, reach me at jhuguetn(at)gmail.com
