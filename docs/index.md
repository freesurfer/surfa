Surfa: Medical Imaging and Surface Processing
=============================================

Surfa is a collection of Python utilities for medical image analysis and mesh-based surface processing. It provides tools that operate on 3D image arrays and triangular meshes with consideration of their representation in a world (or scanner) coordinate system.

**Citing Surfa in a Publication**

Surfa was originally built in part for the development of learning-based cortical surface reconstruction and it is a derivation of the FreeSurfer software suite. If you find this package useful in your analysis, please cite:

- Andrew Hoopes et al. **"TopoFit: Rapid Reconstruction of Topologically-Correct Cortical Surfaces."** *Medical Imaging with Deep Learning*. 2021.

- Bruce Fischl. **"FreeSurfer."** *NeuroImage* vol. 62,2 (2012): 774-81.

**Acknowledgments**

While broad in scope, surfa is an derivative of the [FreeSurfer](https://surfer.nmr.mgh.harvard.edu) brain analysis software suite. Further, the implementation of many mesh-based algorithms were inspired by the [open-source](https://github.com/mikedh/trimesh/blob/main/LICENSE.md) [trimesh](https://github.com/mikedh/trimesh) python library.


```{toctree}
---
maxdepth: 1
hidden:
caption: User Guide
---

guide/installation
guide/images
guide/meshes
guide/visualization
guide/coordinates
```

```{toctree}
---
maxdepth: 1
hidden:
caption: API Reference
---

reference/image
reference/mesh
reference/geometry
reference/affine
reference/io
reference/visualization
reference/system
```
