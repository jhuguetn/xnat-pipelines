# DTI-preprocessing pipeline (compute preprocessing corrections on MRI DTI/DWI scan datasets)

## Introduction
DTI-preprocessing is based on work from [Matthan Caan](http://www.lebic-amc.nl/matthan). The pipeline applies several advanced techniques for correction to the diffusion weighted scans, such as eddy-current correction and motion correction. The output consists of the corrected scan and the diffusion tensor parameters extracted from the corrected scan. The output can be viewed in Freesurfer's [Freeview](https://surfer.nmr.mgh.harvard.edu/fswiki/FreeviewGuide) or any other viewer application that supports compressed NIFTI files. The output can be further processed with FSL's [BedpostX](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FDT/UserGuide) to obtain probabilistic diffusion parameters.
 
Pipeline checks for potential DTI scans in XNAT MRI sessions where is executed against, imaging data shall be either in DICOM or NIFTI format. The core of the pipeline is written in MATLAB, including several required home-brewed and third-pary toolboxes (MATLAB packages).

The DTI-preprocessing pipeline is designed for automatically: 

1. fetch DTI scans in XNAT MRI sessions, note that pipeline supports data either in DICOM or NIFTI format
2. compute the preprocessing corrections
3. and finally store back into XNAT the resulting outputs 

## Taxonomy of DTI-preprocessing output results

output filename | description
| ------------ | ------------ |
b0.nii.gz | The non-diffusion-weighted (b=0s/mm^2) images extracted from the original
dwi(R).{bvec,bval} | The diffusion gradient orientations (bvec) and strength (bval) extracted from the original scan, and rotated values (R) after motion and eddy current correction
dti_{FA,MD,RA,RD}.nii.gz | The estimated fraction anisotropy (FA), mean diffusivity (MD), relative anisotropy (RA), and radial diffusivity (RD) measures
dti_{S0}.nii.gz | The estimated base signal after noise filtering
dti_{L1,L2,L3}.nii.gz | The principle (L1) and radial (L2 and L3) eigenvalues of the diffusion tensor model
dti_{V1,V2,V3}.nii.gz | The principle (V1) and radial (V2 and V3) eigenvectors of the diffusion tensor model
dwiaoecl.nii.gz | The diffusion-weighted scan after all corrections and noise filtering
mask.nii.gz | The brain mask estimated from the non-diffusion-weighted images
resn_dwiaoecl.nii.gz | The residuals after tensor fitting
sigma_dwiaoecl.nii.gz | The estimated noise levels used in the adaptive LMMSE noise filter
bedpostX.tgz | Files that are used by BedpostX to estimate probabilistic diffusion parameters
exploreDTI.mat | File that can be used by the ExploreDTI toolbox
dti_{FA,L1}.dat | Files that can be used by DTIStudio for fiber tracking


## TO-DO: Add pipeline workflow

## Requisites

- XNAT platform (1.6 or +) and XNAT pipeline engine.  

- MATLAB (version R2012b or +) and the following prerequisites.
  ...
- Python version 2.7.X is required for running the pythonic scripts.

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
