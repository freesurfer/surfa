# Changelog

All notable changes to the surfa package are documented in this file.

## [0.6.2] - 2025-09-08
- Added support for voxel package conversions
- Added complete fix for numpy 2 builds

## [0.6.1] - 2024-09-20
- Added temporary fix to prevent numpy 2 build errors

## [0.6.0] - 2023-06-30
- Added surface distance metrics
- Added signed distance transform utilities for image data
- Support wavefront obj file IO

## [0.5.0] - 2023-06-15
- Replaced embree based ray tracing with a pure python implementation
- Improved label map utilities
- Fixed intersection, overlay, and orientation bugs

## [0.4.2] - 2023-02-13
- Set numpy as automatic build dependency

## [0.4.1] - 2023-02-13
- Fixed an installation bug caused by missing headers in sdist

## [0.4.0] - 2023-02-12
- Added mesh transforming and fast self-intersection detection and removal
- Improved management of image geometry and transformations
- Account for image shear when saving to MGZ style file types
- NIFTI IO accounts for xyzt units and does not modify pixdim values
- Fixed bugs in freeview wrapping, spherical interpolation, and dice score

## [0.3.7] - 2022-12-23
- Fixed resampling error introduced by numpy deprecations

## [0.3.6] - 2022-12-14
- Fixed installation error from deprecated packaging tools

## [0.3.5] - 2022-11-30
- Fixed fatal import error of missing utils directory

## [0.3.4] - 2022-11-29
- Fixed bug preventing image transformations with displacement fields

## [0.3.3] - 2022-11-19
- Fixed qform and sform propagation for NIFTI IO
- Fixed bug in image smoothing

## [0.3.2] - 2022-08-09
- Fixed NIFTI slice and overlay loading.
- Fixed overlay frame cropping.
- Added substantial documentation.

## [0.3.1] - 2022-08-04
- Fixed header codes when writing NIFTI files.

## [0.3.0] - 2022-08-04
- Added mesh self-intersection removal.
- Fixed ndarray and overlay casting.
- Fixed casting of ndarray to overlay.

## [0.2.0] - 2022-07-26
- Added interpolation of image coordinates.
- Added segmentation recoding utilities.
- Added freesurfer-specific functions for surface label reading and label-lookups.
- Fixed propagation of label lookups.

## [0.1.0] - 2022-07-20
- Added ray intersection, mesh knn, mesh smoothing, and spherical parameterization.
- Added auto-computing mesh properties.
- Fixed multi-frame overlay and slice writing and volume reshaping.
- Support for loading FS surface labels
- Support quadrangular FS mesh file loading.

## [0.0.12] - 2022-06-29
- Added direct indexing support for overlays.
- Fixed bug when loading MGH files writen by ITK.

## [0.0.11] - 2022-06-20
- Fixed NIFTI loading for newer nibabel versions.

## [0.0.10] - 2022-06-19
- Fixed bug when loading MGH/MGZ files with no embedded FOV.
- Fixed broken `LabelLookup` initialization.

## [0.0.9] - 2022-05-30
- Fixed error when loading NIFTI files.

## [0.0.8] - 2022-05-20
- First public release of the package.
