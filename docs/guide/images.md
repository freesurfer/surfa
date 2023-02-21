Images
======

Surfa provides utilities for working with 3D and 2D multi-frame images. Image array data is structured in one of the following classes, based on spatial dimensionality:

**3D** volumetric images are represented by `Volume` objects.
<br>
**2D** image slices are represented by `Slice` objects.

These structures also encompass an inherent *geometry*, which defines the linear mapping of voxel coordinates on the image grid to Cartesian coordinates in 3D world space (sometimes referred to as scanner space).

## Framed Image Basics

From a high level, `Volume` and `Slice` are universal array objects that store an image buffer along with user-defined metadata. This array buffer, with a defined shape, also supports an additional non-spatial dimension to encode multiple image frames, for example, across time-series data or diffusion directions. Generally, this non-spatial dimension is represented by the last data axis, or the *frame axis*.

At the level of the underlying array, we can access data properties, such shape, data type, and number of frames. For example, a single-frame structural 3D MRI is loaded below as a `Volume` object.

```python
>>> import surfa as sf

>>> image = sf.load_volume('structural.nii.gz')
>>> image.shape
(256, 256, 256)
>>> image.dtype
dtype('uint8')
>>> image.nframes
1
```

Alternatively, a functional MRI aquistion might contain a series of timepoints stacked along the last axis. While the `shape` property includes this extra dimension, `baseshape` defines only the shape of the spatial domain.

```python
>>> image = sf.load_volume('functional.nii.gz')
>>> image.shape
(256, 256, 256, 16)
>>> image.baseshape
(256, 256, 256)
>>> image.nframes
16
```

This same concept applies to 2D `Slice` images:

```python
>>> image = sf.load_slice('slice.nii.gz')
>>> image.shape
(256, 256, 16)
>>> image.baseshape
(256, 256)
>>> image.basedim
2
```

The `basedim` member indicates the number of spatial dimension in the array. A `Slice` always has a `basedim` of 2 and a `Volume` always has a `basedim` of 3.

## Array Representation

At their core, `Volume` and `Slice` framed images operate like numpy arrays and can be constructed with such:

```python
data = np.random.rand(128, 128, 128)
image = sf.Volume(data)
```

In fact, the image buffer is internally stored as a `np.ndarray` instance, which can be retrieved directly via the `data` member. Note that when constructing a framed array, the input numpy array is not copied by default, and so the framed array will share its memory.

Framed images implement numpy's [array-like](https://numpy.org/doc/stable/user/basics.creation.html#converting-python-array-like-objects-to-numpy-arrays) functionality, meaning they can be implicitly converted to the `np.ndarray` class when necessary, for example, when used as input to a numpy function:

```python
mean = np.mean(image)
```

Framed images also emulate numpy-style operations, in-place modifications, and indexing.


```python
image += 10

mask = image < 20
image[mask] = 0

image = image1 * image2
```

Array-specific operations can also be called directly as class methods.

```python
imax = image.max()
mean = image.mean() 
perc = image.percentile(99)
```

This is only a handful of the array utilities. Visit the [Volume API reference](../reference/api/surfa.Volume) for more detailed class documentation.

## Geometry

An important component of these framed images is the mapping of their voxel coordinates to locations in a world, or scanner, coordinate system. This relationship is defined by the `geom` image geometry attribute. This `ImageGeometry` object represents position in two ways: **1)** using a set of linear parameters, including voxel size (resolution), image center, and rotation, and **2)** using a singular `vox2world` affine matrix that transforms voxel coordinates to world coordinates. When either of the parameters are updated, the affine is recomputed accordingly, and vice versa.

```python
>>> image.geom.voxsize
array([1., 1., 1.])
>>> image.geom.center
array([0., 0., 0.])
>>> image.geom.rotation
array([[ 1.,  0.,  0.],
       [ 0.,  1.,  0.],
       [ 0.,  0.,  1.]])
```

```python
>>> image.geom.vox2world
sf.Affine([
  [ 1., 0., 0., -127.],
  [ 0., 1., 0., -128.],
  [ 0., 0., 1., -127.],
  [ 0., 0., 0.,    1.]])
```

### Image Cropping

Numpy-style indexing can be used to crop `Volume` and `Slice` objects while correctly accounting for the underlying geometry. When an image is cropped, as shown below, the image geometry `center` and `vox2world` will be updated.

```python
>>> cropped = image[60:180, 60:180, 60:180]
>>> cropped.geom.center
array([-8., -8., -8.])
```

When the dimensionality of a `Volume` object is reduced by 1 during cropping, the resulting image is cast as a `Slice` object.

```python
>>> image
sf.Volume(shape=(256, 256, 256), dtype=uint8)
>>> sliced = image[:, :, 110]
>>> sliced
sf.Slice(shape=(256, 256), dtype=uint8)
```

### Reorienting

The anatomical *orientation* of the voxel array is implicitly defined by the rotation matrix of the image geometry. In surfa, the default world coordinate system corresponds to *Right-Anterior-Superior* (RAS) anatomical ordering of the *x, y, z* axes. So, the image geometry `orientation` can be coded by a tag that maps each anatomical axis (*Left/Right*, *Inferior/Superior*, *Anterior/Posterior*) to each image axis.

```python
>>> image.geom.orientation
'RAS'
```

To re-order the image data to a particular orientation while preserving the correct world-space position, use the `reorient` function.

```python
>>> image = image.reorient('LIA')
```

## Transforming and Resampling

Other functions can be used to modify the underlying image data while correctly updating (or preserving) image geometry. To resample the image data to a particular voxel size:

```python
>>> resized = image.resize((2, 2, 2), method='linear')
>>> resized.geom.voxsize
array([2., 2., 2.])
```

To fit the image to a particular shape by padding or cropping around the center:

```python
>>> reshaped = image.reshape((180, 256, 180))
>>> reshaped.shape
(180, 256, 180)
```

Images can be conformed to a particular set of geometric requirements all at once using the `conform` function:

```python
>>> conformed = image.conform(voxsize=2, orientation='LIA')
```

To resample an image with a particular target geometry, use the `resample_like` function.

```python
>>> resampled = conformed.resample_like(image)
```

### Affine Transformation

To linear resample the image data with an affine transform matrix, use the `transform` function.

```python
>>> affine = sf.transform.compose_affine(rotation=(10, 0, 0))
>>> rotated = image.transform(affine, method='linear', rotation='center')
```

### Deformation

Voxel displacement fields can also be applied to the image to transform it nonlinearly.

```python
>>> disp = sf.Volume(np.random.randn(*image.shape, 3))
>>> deformed = image.transform(disp, method='linear')
```
