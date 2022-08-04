# Changelog

All notable changes to the surfa package are documented in this file.

## [0.3.0] - 2022-08-04
- Added mesh self-intersection removal
- Fixed ndarray and overlay casting
- Fixed casting of ndarray to overlay

## [0.2.0] - 2022-07-26
- Added interpolation of image coordinates
- Added segmentation recoding utilities
- Added freesurfer-specific functions for surface label reading and label-lookups
- Fixed propagation of label lookups

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
