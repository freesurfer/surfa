# Surfa

Surfa is a collection of Python (3.5+) utilities for medical image analysis and mesh-based surface processing. It provides tools that operate on 3D image arrays and triangular meshes with consideration of their representation in a world (or scanner) coordinate system. While broad in scope, surfa is developed with particular emphasis on neuroimaging applications, as it is an extension of the [FreeSurfer](https://surfer.nmr.mgh.harvard.edu) brain analysis software suite. To install, run:

```
pip install surfa
```

Currently, cython-based utilies are built upon install, so an error will be thrown if a C compiler is not available on the system.

### Development

The library is still in alpha stages of development, so expect code to change frequently across versions. Pull requests are always welcome!

For local development of the codebase, be sure to build the `.pyx` files in the package before importing:

```
python setup.py  build_ext --inplace
```
