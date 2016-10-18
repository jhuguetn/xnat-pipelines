# QAP pipelines (structural/functional MRI QA analysis)

## Introduction
QAP contains 2 XNAT pipelines (qap_anat_processing and qap_fmri_processing) for computing QAP-related Quality Assessment metrics. Both pipelines share most of its resources thus they are logically and phisically kept in the same location. 

The QAP pipelines are designed for automatically: 

1. fetch suited MRI scan data from XNAT instance given an MRSession
2. analyse structural and/or functional MRI running QAP tools
3. and finally store back into XNAT the resulting measuments as derived but linked data (image session assessments)

[Quality Assessment Protocol](http://preprocessed-connectomes-project.org/quality-assessment-protocol/) (QAP) is a Python-based package for computing functional and anatomical MRI data quality measures.
More information about the QAP computed metrics/measurements can be found [here] (http://preprocessed-connectomes-project.org/quality-assessment-protocol/#taxonomy-of-qa-measures).

### qap_anat_processing:
Analizes the quality of structural/anatomical scan(s) in an MRI session. Pipeline automatically searches for T1, ADNI or MPRAGE alike scans to process.

### qap_fmri_processing:
Analizes the quality of functional scan(s) —either or both in the temporal and the spatial domains— in an MRSession. Pipeline automatically searches for fMRI, RESTING, rsMRI alike scans to process.

## Requisites

- QAP package (1.0.4 or +) and its prerequisites should be installed in the system before installing these XNAT pipelines.

- The QAP pipelines ingest computed QA metrics to XNAT database as customized data-types. Thus, [QAPdata module](https://github.com/jhuguetn/xnat-modules/tree/master/QAPdata-0.4) must be conveniently installed in the XNAT instance before running such pipelines. QAPdata module aims at modelling and structuring QAP measurements into custom XNAT data-types.

- Python version 2.7.X is required for running the pythonic scripts. Additionally, Wand (ImageMagick), urllib, lxml and httplib Python modules are also needed.

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

Submit an issue, fork and/or PR. Alternatively, reach me at j.huguet(at)amc.uva.nl
