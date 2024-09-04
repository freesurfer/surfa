import collections
import numpy as np
import warnings
from copy import deepcopy
import surfa as sf


def dice(a, b, labels=None):
    """
    Compute dice coefficients for each label between two hard segmentations.
    
        dice = 2 * |A ∩ B| / |A| + |B|

    Parameters
    ----------
    a, b : array_like
        Label map arrays to compute dice between.
    labels : list
        List of labels to include in the computation. If labels are not
        provided, all unique non-zero integers are used.

    Returns
    -------
    result : dict
        Dictionary of dice scores for each label. If a label is missing
        from both segmentations, it is not included in the result.
    """
    if labels is None:
        labels = np.unique(np.concatenate([a, b]))
        labels = np.delete(labels, np.where(labels == 0))

    result = {}
    for l in labels:
        mask1 = a == l
        mask2 = b == l
        top = 2.0 * np.logical_and(mask1, mask2).sum()
        bottom = np.sum(mask1) + np.sum(mask2)
        if bottom != 0:
            result[l] = top / bottom
    
    return result


def jaccard(a, b, labels=None):
    """
    Compute jaccard coefficients for each label between two hard segmentations.
    
        jaccard = |A ∩ B| / |A ∪ B|

    Parameters
    ----------
    a, b : array_like
        Label map arrays to compute the jaccard between.
    labels : list
        List of labels to include in the computation. If labels are not
        provided, all unique non-zero integers are used.

    Returns
    -------
    result : dict
        Dictionary of jaccard scores for each label. If a label is missing
        from both segmentations, it is not included in the result.
    """
    if labels is None:
        labels = np.unique(np.concatenate([a, b]))
        labels = np.delete(labels, np.where(labels == 0))
    
    result = {}
    for l in labels:
        mask1 = a == l
        mask2 = b == l
        top = np.logical_and(mask1, mask2).sum()
        bottom = np.logical_or(mask1, mask2).sum()
        if bottom != 0:
            result[l] = top / bottom
    
    return result


def recode(seg, recoder):
    """
    Recode the labels of a discrete segmentation.

    Parameters
    ----------
    seg : ndarray or framed array
        Segmentation array to recode.
    recoder : dict or LabelRecoder
        Label to label mapping.
    
    Returns
    -------
    recoded : ndarray or framed array
    """
    if isinstance(recoder, LabelRecoder):
        mapping = recoder.mapping
    elif not isinstance(recoder, dict):
        raise ValueError(f'invalid label recoder type: {type(recoder).__name__}')
    else:
        mapping = recoder

    old = np.array(list(mapping.keys()))
    new = np.array(list(mapping.values()))
    
    m = np.zeros(np.max((seg.max(), old.max())) + 1, dtype=np.int64)
    m[old] = new
    recoded = m[seg]

    if isinstance(seg, sf.core.framed.FramedArray):
        recoded = seg.new(recoded)
        if isinstance(recoder, LabelRecoder):
            recoded.labels = recoder.target

    return recoded


class LabelElement:

    def __init__(self, name=None, color=None):
        """
        Base LabelLookup element to define label name and color.

        Parameters
        ----------
        name : str
            Label name
        color : array_like
            Label color indicated by RGB or RGBA array.
        """
        self.name = name
        self.color = color

    @property
    def name(self):
        """
        Label name.
        """
        return self._value

    @name.setter
    def name(self, value):
        self._value = '' if value is None else str(value)

    @property
    def color(self):
        """
        Label color stored as an RGBA array of type (uchar, uchar, uchar, float).
        """
        return self._color

    @color.setter
    def color(self, value):
        if value is None:
            self._color = [0, 0, 0]
        if len(value) == 3:
            value = (*value, 1.0)
        elif len(value) != 4:
            raise ValueError('label color must be a 4-element RGBA array')
        color = np.array(value, dtype=np.float64)
        color[:3] = color[:3].clip(0, 255).astype(np.uint8).astype(np.float64)
        self._color = color


class LabelLookup(collections.OrderedDict):
    """
    Dictionary storing a label lookup mapping integer indices to labels names and colors.
    """

    def __setitem__(self, key, value):
        if not np.issubdtype(type(key), np.integer):
            raise ValueError(f'cannot convert object of type {key.__class__.__name__} to LabelLookup integer index')
        if isinstance(value, LabelElement):
            value = deepcopy(value)
        elif isinstance(value, str):
            value = LabelElement(name=value)
        elif isinstance(value, tuple) or isinstance(value, list) and len(value) == 2:
            value = LabelElement(name=value[0], color=value[1])
        else:
            raise ValueError(f'cannot convert object of type {value.__class__.__name__} to LabelLookup element')
        return super().__setitem__(int(key), value)

    def __repr__(self):
        col1 = len(str(max(self.keys()))) + 1
        col2 = max([len(elt.name) for elt in self.values()]) + 2
        lines = []
        for idx, elt in self.items():
            rgb = elt.color[:3].astype(np.uint8).astype(str)
            color_str = ',  '.join([str(c).rjust(3) for c in rgb]) + f',  {elt.color[-1]:.2f}'
            lines.append(str(idx).ljust(col1) + elt.name.ljust(col2) + color_str)
        return '\n'.join(lines)

    def save(self, filename, fmt=None):
        """
        Write label lookup to file.

        Parameters
        ----------
        filename : str
            Target filename to write lookup to.
        """
        from surfa.io.labels import save_label_lookup
        save_label_lookup(self, filename, fmt)

    def search(self, name, exact=False):
        """
        Search for matching labels.

        Parameters
        ----------
        name : str
            String or substring to search for.
        extact : bool
            If enabled, label must match search name exactly.

        Returns
        -------
        int or list of int
            Matching label indices. If `exact`, returns single index or None.
            Otherwise, a list of matches are returned.
        """
        if exact:
            return next((idx for idx, elt in self.items() if name == elt.name), None)
        else:
            allcaps = name.upper()
            return [idx for idx, elt in self.items() if allcaps in elt.name.upper()]

    def extract(self, labels):
        """
        Extract a new LabelLookup from a list of label indices.

        Parameters
        ----------
        labels : array_like of int
            List of label indices to extract.

        Returns
        -------
        LabelLookup
            Label lookup with extracted label indices.
        """
        lookup = LabelLookup()
        for label in labels:
            elt = self.get(label)
            if elt is None:
                raise ValueError(f'index {label} does not exist in the LabelLookup')
            lookup[label]= (elt.name, elt.color)
        return lookup

    def copy_colors(self, lookup):
        """
        Copy colors of matching label indices from a source LabelLookup.

        Parameters
        ----------
        lookup : LabelLookup
            Label lookup to copy colors from.
        """
        for label in self.keys():
            elt = lookup.get(label)
            if elt is not None and elt.color is not None:
                self[label].color = elt.color

    def copy_names(self, lookup):
        """
        Copy names of matching label indices from a source LabelLookup.

        Parameters
        ----------
        lookup : LabelLookup
            Label lookup to copy names from.
        """
        for label in self.keys():
            elt = lookup.get(label)
            if elt is not None:
                self[label].name = elt.name


class LabelRecoder:

    def __init__(self, mapping, target=None):
        """
        Map to recode the label indices of a segmentation.

        Parameters
        ----------
        mapping : dict
            Integer label to label mapping diction.
        target : LabelLookup
            Label lookup corresponding to the recoded target segmentation.
        """
        self.mapping = dict(mapping)
        self.target = target

    def invert(self, target_labels=None, strict=False):
        """
        Invert the label mapping dictionary

        Parameters
        ----------
        target_labels : LabelLookup, optional
            LabelLookup that will be assigned as the target of the returned LabelRecoder
            If not assigned, the output volume using this recoder will not have a LabelMapping
        strict : bool, optional
            Enforce the inverted label recoding is 1-to-1
            
        Returns
        -------
        LabelRecoder
            A LabelRecoder object with the k,v pairs of the original mapping swapped
            
            If the input mapping is many-to-1, the function will raise a `KeyError` unless
            the `strict` param is set to `False`. In the case where the input mapping is
            many-to-1 and `strict` is set to `False`, the returned LabelRecoder will map
            to the minimum value of the 'many' labels. e.g {1:0, 2:0} the inverse will
            be {0:1}.
            
        Raises
        ------
        KeyError
            If `strict` is set to `True` and inverted label mapping is not 1-to-1

        Examples
        --------
        Load an aseg volume, recode the labels to tissue types using the tissue_type_recoder,
        then invert the tissue_type_recoder and remap the labels back.
        Note that the tissue_type_recoder is not 1-to-1, so labels classes in the second
        remapped volume will be merged.
        
        # load the aseg
        >>> aseg = sf.load_volume('aseg.mgz')

        # create the tissue_type_recoder obj
        >>> lr = sf.freesurfer.tissue_type_recoder()

        # remap the aseg labels
        >>> aseg_to_tissue = sf.labels.recode(aseg,lr)

        # invert the label recoder and assign the standard cLUT as target labels
        >>> inv_lr = lr.invert(target_labels=sf.freesurfer.labels())

        # re-remap the aseg labels
        >>> tissue_to_aseg = sf.labels.recode(aseg,inv_lr)
        """
        # invert the mapping dictionary, handling many-to-1 mapping case
        inv_mapping = {}
        for k,v in self.mapping.items():
            if v not in inv_mapping.keys():
                inv_mapping[v] = [k]
            else:
                inv_mapping[v].append(k)
        
        test = [len(x) == 1 for x in inv_mapping.values()]

        # raise key error if many-to-1 and strict
        if False in test and strict:
            raise KeyError('Cannot strictly invert a many-to-1 LabelRecoder')
        elif False in test:
            warnings.warn('The label remapping is not 1-to-1, some classes will be merged.')
        
        [x.sort() for x in inv_mapping.values()]
        inv_mapping = {k:v[0] for k,v in inv_mapping.items()}

        return LabelRecoder(inv_mapping, target_labels)
