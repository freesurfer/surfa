import copy
import numpy as np

from surfa.core.array import conform_ndim


class FramedArray:
    """
    Abstract class defining an ND array with data frames and additional meta information. This is
    the base type for volumes, slices, and overlays, which represent 3D, 2D, and 1D objects,
    respectively. This class should only be used as an internal base class and never be initialized
    directly.

    A `FramedArray` contains two distinct properties: buffer data and associated metadata. The data
    is always represented internally as a numpy array with an explicit number of dimensions. ND arrays
    can be optionally stacked along the last dimension, which represents individual 'data frames'. For
    example, a single-frame 3D `FramedArray` (defined as a `Volume`) might be of shape `(64, 64, 64)`,
    while a multi-frame `Volume` with the same 'base shape' might be `(64, 64, 64, 3)`. The frame axis
    is designed to represent a non-spatial dimension.

    The internal data buffer is wrapped, such that the `FramedArray` can be treated much like a numpy
    array. It can be manipulated with standard math and assignment operators, and it will be automatically
    converted to a numpy ndarray object if necessary.
    """

    def __init__(self, basedim, data, metadata=None):
        """
        The input data is not copied, and the array should have ndims equal to the subclass' basedim (or
        basedim + 1). Any extra dimension is assumed to represent data frames.
        """

        # ensure abstract class isn't being used directly
        if not isinstance(basedim, int):
            raise TypeError('FramedArray cannot be initialized without setting a valid basedim.')

        # set internal base dimension
        self._basedim = basedim

        # set data array
        self.data = data

        # set metadata dictionary
        self._metadata = {}
        if metadata is not None:
            self._metadata.update(metadata)

    def __repr__(self):
        """
        Print out some basic information regarding shape and dtype. Should keep it simple.
        """
        return f'sf.{self.__class__.__name__}(shape={self.shape}, dtype={self.dtype})'

    @property
    def basedim(self):
        """
        Base dimensionality of the array (excludes frame dimension).
        """
        return self._basedim

    @property
    def data(self):
        """
        Core data numpy ndarray.
        """
        return self._data

    @data.setter
    def data(self, value):
        """
        Setter for the private data array. Ensures dimensionality is correct. If the base-shape of
        the data has changed after updating, the private `_shape_changed()` hook will be called.
        """

        # make sure a string (filename) isn't being provided for input data - a common mistake
        if isinstance(value, str):
            raise TypeError('Unexpected string for `data` parameter. Expected a {basedim}D array.')

        # existing arrays are not copied
        value = np.asarray(value)

        # run a few sanity checks on the input data shape
        if value.ndim < 1:
            raise ValueError('Array data cannot be set to scalar.')

        # instead of throwing an error, data with fewer dimensions than
        # expected should be reshaped with added axes
        if value.ndim < self._basedim:
            value = conform_ndim(value, self._basedim)

        # single-framed arrays will always be represented by an array with
        # dimensionality equivalent to basedim
        if value.ndim == (self._basedim + 1) and value.shape[-1] == 1:
            value = value.squeeze(axis=-1)

        # throw an error if input array has more dimensions than the framed base
        if value.ndim > self._basedim + 1:
            raise ValueError(f'Array data cannot be set from data with {value.ndim} dims.')

        # check for shape changes, so we can update geometry if necessary
        current = getattr(self, '_data', None)
        shaped_changed = current is not None and current.shape[:self.basedim] != value.shape[:self.basedim]

        # actually set the data
        setattr(self, '_data', value)

        # send signal if the underlying shape has been modified
        if shaped_changed:
            self._shape_changed()

    @property
    def framed_data(self):
        """
        Core data array reshaped to always include the frame dimension, regardless of nframes.
        """
        return conform_ndim(self.data, self.basedim + 1)

    @property
    def nframes(self):
        """
        Number of data frames.
        """
        return self.shape[-1] if self.data.ndim == self.basedim + 1 else 1

    @property
    def shape(self):
        """
        True shape of the internal data array.
        """
        return self.data.shape

    @property
    def baseshape(self):
        """
        Base shape of the data array (excludes the frame dimension).
        """
        return self.data.shape[:self.basedim]

    @property
    def size(self):
        """
        Total number of elements in the data array.
        """
        return self.data.size

    @property
    def dtype(self):
        """
        Data type.
        """
        return self.data.dtype

    def astype(self, dtype, copy=True, order='K'):
        """
        Copy of the array, cast to a specified type.

        TODO might need to change the dtype equivolence to check
        for abstract comparisons
        """
        if dtype == self.dtype and not copy:
            return self
        return self.new(self.data.astype(dtype=dtype, order=order))

    def _shape_changed(self):
        """
        Event hook that is called when the internal data array shape is updated.
        """
        pass

    @property
    def metadata(self):
        """
        Metadata dictionary.
        """
        return self._metadata

    @metadata.setter
    def metadata(self, value):
        """
        Replace the metadata dictionary. Will always make a shallow copy of the new dictionary.
        """
        self._metadata = copy.copy(value)

    def copy(self):
        """
        Return a deep copy of the instance.
        """
        return copy.deepcopy(self)

    def new(self, data):
        """
        Return a new instance of the array with updated data. Metadata is not replaced.
        """
        return self.__class__(data=data, metadata=self.metadata)

    def save(self, filename):
        """
        Write array to file.
        """
        io.ndarray.save_nd_array(self, filename)

    def min(self, nonzero=False):
        """
        Compute the minimum.
        """
        data = self.data
        if nonzero:
            data = data[data.nonzero()]
        return data.min()

    def max(self):
        """
        Compute the maximum.
        """
        return self.data.max()

    def mean(self, nonzero=False):
        """
        Compute the mean.
        """
        data = self.data
        if nonzero:
            data = data[data.nonzero()]
        return data.mean()

    def percentile(self, percentiles, method='linear', nonzero=False):
        """
        Compute the q-th percentile of the data.
        """
        data = self.data
        if nonzero:
            data = data[data.nonzero()]
        return np.percentile(data, percentiles, interpolation=method)

    def unique(self):
        """
        Find all unique elements of an array, sorted.
        """
        return np.unique(self)

    def onehot(self, mapping, dtype='uint32'):
        """
        Convert discrete labels to a one-hot encoded probabilistic map.
        """
        if self.nframes > 1:
            raise RuntimeError(f'Cannot onehot-encode labels with more than 1 frame, but array has {self.nframes} frames.')

        mapping = np.asarray(mapping)
        if mapping.ndim != 1:
            raise ValueError('Label mapping must be a 1D list.')

        nlabels = len(mapping)
        inttype = np.uint16 if nlabels < np.iinfo(np.uint16).max else np.uint32
        recoder = np.zeros(self.max() + 1, dtype=inttype)
        recoder[mapping] = np.arange(nlabels)

        dsize = self.data.size
        flat = np.zeros((dsize, nlabels), dtype=dtype)
        flat[np.arange(dsize), recoder[self.data.ravel()]] = 1
        flat.shape = (*self.baseshape, nlabels)
        return self.new(flat)

    def collapse(self, mapping=None):
        """
        Collapse a one-hot encoded probabilistic map to discrete labels.
        """
        if self.nframes == 1:
            raise RuntimeError('Cannot collapse probabilities with only 1 frame.')
        
        inttype = np.uint16 if self.nframes < np.iinfo(np.uint16).max else np.uint32
        seg = np.zeros(self.baseshape, dtype=inttype)
        np.argmax(self, axis=-1, out=seg)
        
        if mapping is not None:
            mapping = np.asarray(mapping)
            if mapping.ndim != 1:
                raise ValueError('Label mapping must be a 1D list.')
            seg = mapping[seg]

        return self.new(seg)

    # numpy array wrapping

    def __array__(self):
        return self.data

    # comparison operators

    def __eq__(self, other):
        return self.new(self.data == np.asarray(other))
    
    def __ne__(self, other):
        return self.new(self.data != np.asarray(other))

    def __lt__(self, other):
        return self.new(self.data < np.asarray(other))

    def __le__(self, other):
        return self.new(self.data <= np.asarray(other))

    def __gt__(self, other):
        return self.new(self.data > np.asarray(other))

    def __ge__(self, other):
        return self.new(self.data >= np.asarray(other))

    # unary operators

    def __pos__(self):
        return self.new(+self.data)

    def __neg__(self):
        return self.new(-self.data)

    # binary operators

    def __and__(self, other):
        return self.new(self.data & np.asarray(other))

    def __or__(self, other):
        return self.new(self.data | np.asarray(other))

    def __add__(self, other):
        return self.new(self.data + np.asarray(other))

    def __radd__(self, other):
        return self.new(np.asarray(other) + self.data)

    def __sub__(self, other):
        return self.new(self.data - np.asarray(other))

    def __rsub__(self, other):
        return self.new(np.asarray(other) - self.data)

    def __mul__(self, other):
        return self.new(self.data * np.asarray(other))

    def __rmul__(self, other):
        return self.new(np.asarray(other) * self.data)

    def __truediv__(self, other):
        return self.new(self.data / np.asarray(other))

    def __rtruediv__(self, other):
        return self.new(np.asarray(other) / self.data)

    def __pow__(self, other):
        return self.new(self.data ** np.asarray(other))

    # assignment operators

    def __setitem__(self, key, value):
        if isinstance(key, FramedArray):
            key = np.asarray(key)
        if isinstance(value, FramedArray):
            value = np.asarray(value)
        self.data[key] = value

    def __iadd__(self, other):
        self.data += np.asarray(other)
        return self

    def __isub__(self, other):
        self.data -= np.asarray(other)
        return self

    def __imul__(self, other):
        self.data *= np.asarray(other)
        return self

    def __itruediv__(self, other):
        self.data /= np.asarray(other)
        return self
