Labels
======

Surfa provides utilities for working with image label mappings. Label mappings
store information to correlate integer values in the image with a label name and
RGBA color representation in an image viewer. The classes that surfa provides
for working with labels are primarily built on top of dictionaries.

**LabelLookup** objects hold the label information in an ordered dictionary,
where each key is the int corresponding to the label value in the image, and each value is a `LabelElement`.

**LabelElement** objects are mutable objects with two fields, `name` and `color`
- `name` is a string representing the label name
- `color` is a 4 element list of integer values representing the RGBA values

## Label Basics

`LabelLookup` objects can be instantiated by loading a FreeSurfer color lookup
table file or defined manually by the user. There are also some utilities for
creating `LabelLookup` objects representing label mapping commonly used in
FreeSurfer.

```python
>>> import surfa as sf

# instantiate `LabelLookup` from a file
>>> labels_from_file = sf.load_label_lookup('/usr/local/freesurfer/7.4.1/luts/FreeSurferColorLUT.txt')

# instantiate from a commonly used label mapping (Destrieux cortical atlas)
>>> destrieux_labels = sf.freesurfer.destrieux()

# instantiate manually
>>> manual_labels = sf.LabelLookup()
>>> manual_labels[0] = ('Unknown', [0,0,0,0])
>>> manual_labels[24] = ('CSF', [255,255,255,0])
>>> manual_labels[100] = ('CSF-Ventricle', [128,128,128,0])

>>> manual_labels[24].name
'CSF'
>>> manual_labels[24].color
array([255., 255., 255.,   0.])
```

Labels can be accessed by indexing the label value in the `LabelLookup`. The
index of a label can be searched for by passing a string to the `search` method.
By default the search is greedy and not case sensitive, this can be changed to
an exact match via the `exact` arg.

```python
# greedy search
>>> manual_labels.search('CSF')
[24, 100]

# exact search
>>> manual_labels.search('CSF',exact=True)
24
```

Subsets of a `LabelLookup` can be extracted into `LabelLookup` objects if
working with the full label mapping contains lots of unused labels.

```python
>>> import numpy as np

# load an aseg, find unique labels
>>> aseg = sf.load_volume('aseg.mgz')
>>> aseg_label_indices = np.unique(aseg.data)
>>> aseg_label_indices
array([  0,   2,   3,   4,   5,   7,   8,  10,  11,  12,  13,  14,  15,
        16,  17,  18,  24,  26,  28,  30,  31,  41,  42,  43,  44,  46,
        47,  49,  50,  51,  52,  53,  54,  58,  60,  62,  63,  72,  77,
        85, 251, 252, 253, 254, 255], dtype=int32)

>>> aseg_label_lookup = sf.freesurfer.labels().extract(aseg_label_indices)

# sanity check
>>> np.array([*aseg_label_lookup.keys()], dtype='int32') == aseg_label_indices
array([ True,  True,  True,  True,  True,  True,  True,  True,  True,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
        True,  True,  True,  True,  True,  True,  True,  True,  True,
        True,  True,  True,  True,  True,  True,  True,  True,  True])

>>> aseg_label_lookup
0   Unknown                          0,    0,    0,  1.00
2   Left-Cerebral-White-Matter     245,  245,  245,  1.00
3   Left-Cerebral-Cortex           205,   62,   78,  1.00
4   Left-Lateral-Ventricle         120,   18,  134,  1.00
5   Left-Inf-Lat-Vent              196,   58,  250,  1.00
...
85  Optic-Chiasm                   234,  169,   30,  1.00
251 CC_Posterior                     0,    0,   64,  1.00
252 CC_Mid_Posterior                 0,    0,  112,  1.00
253 CC_Central                       0,    0,  160,  1.00
254 CC_Mid_Anterior                  0,    0,  208,  1.00
255 CC_Anterior                      0,    0,  255,  1.00
```

## Label Recoding

Often times, label indices do not match up between label lookups, especially in
the case we are recoding labels to merge classes. The `LabelRecoder` class
provides the functionality to do this.

The `LabelRecoder` class has two fields:

- `mapping` a dictionary where the keys are the indices of the labels in the
current `LabelLookup`, and the values are the index to recode it to
- `target_labels` a `LabelLookup` that defines the target label names/colors. 
Can be `None`

> [!NOTE]
> The `target_labels` field will be assigned to the `labels` field of a label
> volume that is recoded using a `LabelRecoder`. If this field is `None`, then
> the recoded segmentation volume will have no label mapping, however, that can
> be assigned to after the recoded segmentation volume is created

Some predefined `LabelLookup` and `LabelRecoder` objects can be found under
`surfa.freesurfer`

```python
# recode the aseg volume labels to the tissue type
>>> recoder = sf.freesurfer.tissue_type_recoder()
>>> seg_tissue_types = sf.labels.recode(aseg,recoder)
>>> seg_tissue_types.labels
0 Unknown                    0,    0,    0,  1.00
1 Cortex                   205,   62,   78,  1.00
2 Subcortical-Gray-Matter  230,  148,   34,  1.00
3 White-Matter             245,  245,  245,  1.00
4 CSF                      120,   18,  134,  1.00
5 Head                     150,  150,  200,  1.00
6 Lesion                   255,  165,    0,  1.00
```

## Label Metrics

There are also some utilities for calculating the dice score and jaccard
coefficients for two sets of label volumes. By default both will compute the
metric for all unique labels found in the label volumes, or the user can specify
a list of label indices to compute the metrics for.

```python
# load another segmentation to compare to the aseg
>>> seg = sf.load_volume('aseg_2.mgz')

>>> target_labels = [2,3,4,255]
>>> sf.labels.dice(aseg,seg, target_labels)
{2: 0.5299304443534139, 3: 0.42780355492851396, 4: 0.29737467850730337, 255: 0.21085134539038378}
>>> sf.labels.jaccard(aseg,seg, target_labels)
{2: 0.3604798441801161, 3: 0.2721056622851365, 4: 0.1746565581713504, 255: 0.1178500986193294}
```
