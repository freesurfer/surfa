# Changelog

All notable changes to the surfa package are documented in this file.

## Unreleased
- Added ray intersection, mesh knn, mesh smoothing, and spherical parameterization.
- Added auto-computing mesh properties.
- Fixed multi-frame Overlay and Slice writing and Volume reshaping.
- Support for loading FS surface labels
- Support quadrangular FS mesh file loading.

## [0.0.12] - 2020-06-29
- Added direct indexing support for Overlays.
- Fixed bug when loading MGH files writen by ITK.

## [0.0.11] - 2020-06-20
- Fixed NIFTI loading for newer nibabel versions.

## [0.0.10] - 2020-06-19
- Fixed bug when loading MGH/MGZ files with no embedded FOV.
- Fixed broken `LabelLookup` initialization.

## [0.0.9] - 2020-05-30
- Fixed error when loading NIFTI files.

## [0.0.8] - 2020-05-20
- First public release of the package.
