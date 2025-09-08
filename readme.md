# Surfa

![PyPi Version](https://img.shields.io/pypi/v/surfa?color=lightgrey&style=for-the-badge)
![Test Status](https://img.shields.io/github/actions/workflow/status/freesurfer/surfa/test.yml?branch=master&label=tests&style=for-the-badge)

Surfa is a collection of Python utilities for medical image analysis and mesh-based surface processing. It provides tools that operate on 3D image arrays and triangular meshes with consideration of their representation in a world (or scanner) coordinate system. While broad in scope, surfa is developed with particular emphasis on neuroimaging applications. To install, run:

```
pip install surfa
```

Note: The above command should run smoothly and require no further steps, but if your system does not have a c compiler installed it will throw an error.  To resolve this potential issue, review the [suggested steps](https://surfer.nmr.mgh.harvard.edu/docs/surfa/guide/installation.html) in the compiling section.

### Documentation

The surfa [documentation and API reference](https://surfer.nmr.mgh.harvard.edu/docs/surfa) is currently a work-in-progress, and any additions are welcome. The documentation source code lives under the `docs` subdirectory.

### Development

Pull requests are always welcome! For local development of the codebase, be sure to build the `.pyx` files in the package before importing:

```
python setup.py  build_ext --inplace
```

Feel free to open [an issue](https://github.com/freesurfer/surfa/issues) if you encounter a bug or have a feature request.
