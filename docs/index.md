Surfa: Medical Imaging and Surface Processing
=============================================

Surfa is a collection of Python utilities for medical image analysis and mesh-based surface processing. It provides tools that operate on 3D image arrays and triangular meshes with consideration of their representation in a world (or scanner) coordinate system.

[**Installation:**](guide/installation) How to install surfa via pip
<br>
[**User Guide:**](guide/index) Getting set up and familiar with surfa
<br>
[**API Reference:** ](reference/index) Documentation of the user facing API


**Citation:** If you find this package useful in your work, please cite:

1. Hoopes, Andrew, Juan Eugenio Iglesias, Bruce Fischl, Douglas N. Greve, and Adrian V. Dalca. **"TopoFit: Rapid Reconstruction of Topologically-Correct Cortical Surfaces."** *Medical Imaging with Deep Learning*. 2021.

2. Fischl, Bruce. **"FreeSurfer."** *NeuroImage* vol. 62,2 (2012): 774-81.

**Acknowledgments:** While broad in scope, surfa is an extension of the [FreeSurfer](https://surfer.nmr.mgh.harvard.edu) brain analysis software suite. Further, the implementation of many mesh-based algorithms were inspired by the [open-source](https://github.com/mikedh/trimesh/blob/main/LICENSE.md) [trimesh](https://github.com/mikedh/trimesh) python library.


```{toctree}
---
maxdepth: 1
hidden:
caption: Getting Started
---

guide/index
reference/index
```
