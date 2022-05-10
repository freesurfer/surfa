import os
import numpy as np
import gzip

from surfa.core.array import pad_vector_length
from surfa.core import FramedArray
from surfa.image import Volume
from surfa.image import Slice
from surfa.image.framed import FramedImage
from surfa.transform import ImageGeometry
from surfa.io import fsio
from surfa.io import protocol
from surfa.io.utils import read_bytes
from surfa.io.utils import write_bytes
from surfa.io.utils import check_file_readability


def load_volume(filename, fmt=None):
    """
    Load an image `Volume` from a 3D array file.

    Parameters
    ----------
    filename : str
        File path to read.
    fmt : str, optional
        Explicit file format. If None (default), the format is extrapolated
        from the file extension.

    Returns
    -------
    Volume
        Loaded volume.
    """
    return load_framed_array(filename=filename, atype=Volume, fmt=fmt)


def load_slice(filename, fmt=None):
    """
    Load an image `Slice` from a 2D array file.

    Parameters
    ----------
    filename : str
        File path to read.
    fmt : str, optional
        Explicit file format. If None (default), the format is extrapolated
        from the file extension.

    Returns
    -------
    Slice
        Loaded slice.
    """
    return load_framed_array(filename=filename, atype=Slice, fmt=fmt)


def load_overlay(filename, fmt=None):
    """
    Load a surface `Overlay` from a 1D array file.

    Parameters
    ----------
    filename : str
        File path to read.
    fmt : str, optional
        Explicit file format. If None (default), the format is extrapolated
        from the file extension.

    Returns
    -------
    Overlay
        Loaded overlay.
    """
    return load_framed_array(filename=filename, atype=Overlay, fmt=fmt)


def load_framed_array(filename, atype, fmt=None):
    """
    Generic loader for `FramedArray` objects.

    Parameters
    ----------
    filename : str
        File path to read.
    atype : class
        Particular FramedArray subclass to read into.
    fmt : str, optional
        Forced file format. If None (default), file format is extrapolated
        from extension.

    Returns
    -------
    FramedArray
        Loaded framed array. 
    """
    check_file_readability(filename)

    if fmt is None:
        iop = protocol.find_protocol_by_extension(array_io_protocols, filename)
        if iop is None:
            raise ValueError(f'cannot determine file format from extension for {filename}')
    else:
        iop = protocol.find_protocol_by_name(array_io_protocols, fmt)
        if iop is None:
            raise ValueError(f'unknown file format {fmt}')

    return iop().load(filename, atype)


def save_framed_array(arr, filename, fmt=None):
    """
    Save a `FramedArray` object to file.

    Parameters
    ----------
    arr : FramedArray
        Object to write.
    filename: str
        Destination file path.
    fmt : str
        Forced file format. If None (default), file format is extrapolated
        from extension.
    """
    if fmt is None:
        iop = protocol.find_protocol_by_extension(array_io_protocols, filename)
        if iop is None:
            raise ValueError(f'cannot determine file format from extension for {filename}')
    else:
        iop = protocol.find_protocol_by_name(array_io_protocols, fmt)
        if iop is None:
            raise ValueError(f'unknown file format {fmt}')
        filename = iop.enforce_extension(filename)

    iop().save(arr, filename)


class MGHArrayIO(protocol.IOProtocol):
    """
    Array IO protocol for MGH and compressed MGZ files.
    """

    name = 'mgh'
    extensions = ('.mgz', 'mgh', '.mgh.gz')

    def dtype_from_id(self, id):
        """
        Convert a FreeSurfer datatype ID to a numpy datatype.

        Parameters
        ----------
        id : int
            FreeSurfer datatype ID.

        Returns
        -------
        np.dtype
            Converted numpy datatype.
        """
        mgh_types = {
            0:  '>u1',  # uchar
            1:  '>i4',  # int32
            2:  '>i8',  # int64
            3:  '>f4',  # float
            4:  '>i2',  # short
            6:  '>f4',  # tensor
            10: '>u2',  # ushort
        }
        dtype = mgh_types.get(id)
        if dtype is None:
            raise NotImplementedError(f'unsupported MGH data type ID: {id}')
        return np.dtype(dtype)

    def load(self, filename, atype):
        """
        Read array from an MGH/MGZ file.

        Parameters
        ----------
        filename : str
            File path to read.
        atype : class
            FramedArray subclass to load.

        Returns
        -------
        FramedArray
            Array object loaded from file.
        """

        # check if the file is gzipped
        fopen = gzip.open if filename.lower().endswith('gz') else open
        with fopen(filename, 'rb') as file:

            # skip version tag
            file.read(4)

            # read shape and type info
            shape = read_bytes(file, '>u4', 4)
            dtype_id = read_bytes(file, '>u4')
            dof = read_bytes(file, '>u4')

            # read geometry
            geom_params = {}
            unused_header_space = 254
            valid_geometry = bool(read_bytes(file, '>u2'))

            # ignore geometry if flagged as invalid
            if valid_geometry:
                geom_params = dict(
                    voxsize=read_bytes(file, '>f4', 3),
                    rotation=read_bytes(file, '>f4', 9).reshape((3, 3), order='F'),
                    center=read_bytes(file, '>f4', 3),
                )
                unused_header_space -= 60

            # skip empty header space
            file.read(unused_header_space)

            # read data buffer (MGH files store data in fortran order)
            dtype = self.dtype_from_id(dtype_id)
            data = read_bytes(file, dtype, int(np.prod(shape))).reshape(shape, order='F')

            # init array
            arr = atype(data.squeeze())

            # read scan parameters
            scan_params = {
                'tr': read_bytes(file, dtype='>f4'),
                'fa': read_bytes(file, dtype='>f4'),
                'te': read_bytes(file, dtype='>f4'),
                'ti': read_bytes(file, dtype='>f4'),
            }

            # ignore fov
            fov = read_bytes(file, dtype='>f4')
 
            # update image-specific information
            if isinstance(arr, FramedImage):
                arr.geom.update(**geom_params)
                arr.metadata.update(scan_params)

            # read metadata tags
            while True:
                tag, length = fsio.read_tag(file)
                if tag is None:
                    break

                # command history
                elif tag == fsio.tags.history:
                    history = file.read(length).decode('utf-8').rstrip('\x00')
                    if arr.metadata.get('history'):
                        arr.metadata['history'].append(history)
                    else:
                        arr.metadata['history'] = [history]

                # embedded lookup table
                elif tag == fsio.tags.old_colortable:
                    arr.labels = fsio.read_binary_lookup_table(file)

                # phase encode direction
                elif tag == fsio.tags.pedir:
                    pedir = file.read(length).decode('utf-8').rstrip('\x00')
                    if pedir != 'UNKNOWN':
                        arr.metadata['phase-encode-direction'] = pedir

                # field strength
                elif tag == fsio.tags.fieldstrength:
                    arr.metadata['field-strength'] = read_bytes(file, dtype='>f4')

                # skip everything else
                else:
                    file.read(length)

        return arr

    def save(self, arr, filename):
        """
        Write array to a MGH/MGZ file.

        Parameters
        ----------
        arr : FramedArray
            Array to save.
        filename : str
            Target file path.
        """

        # determine whether to write compressed data
        if filename.lower().endswith('gz'):
            fopen = lambda f: gzip.open(f, 'wb', compresslevel=6)
        else:
            fopen = lambda f: open(f, 'wb')

        with fopen(filename) as file:

            # before we map dtypes to MGZ-supported types, smartly convert int64 to int32
            if arr.dtype == np.int64:
                if arr.max() > np.iinfo(np.int32).max or arr.min() < np.iinfo(np.int32).min:
                    raise ValueError('MGH files only support int32 datatypes, but array cannot be ',
                                     'casted since its values exceed the int32 integer limits')
                arr = arr.astype(np.int32)

            # determine supported dtype to save as (order here is very important)
            type_map = {
                np.uint8: 0,
                np.bool8: 0,
                np.int32: 1,
                np.floating: 3,
                np.int16: 4,
                np.uint16: 10,
            }
            dtype_id = next((i for dt, i in type_map.items() if np.issubdtype(arr.dtype, dt)), None)
            if dtype_id is None:
                raise ValueError(f'writing dtype {arr.dtype.name} to MGH format is not supported')

            # sanity check on the array size
            ndim = arr.data.ndim
            if ndim < 1:
                raise ValueError(f'cannot save scalar value to MGH file format')
            if ndim > 4:
                raise ValueError(f'cannot save array with more than 4 dims to MGH format, but got {ndim}D array')

            # shape must always be a length-4 vector, so let's pad with ones
            shape = np.ones(4)
            shape[:ndim] = arr.data.shape

            # begin writing header
            write_bytes(file, 1, '>u4')  # version
            write_bytes(file, shape, '>u4')  # shape
            write_bytes(file, dtype_id, '>u4')  # MGH data type
            write_bytes(file, 1, '>u4')  # DOF

            # write geometry, if valid
            unused_header_space = 254
            is_image = isinstance(arr, FramedImage)
            write_bytes(file, is_image, '>u2')
            if is_image:
                write_bytes(file, arr.geom.voxsize, '>f4')
                write_bytes(file, np.ravel(arr.geom.rotation, order='F'), '>f4')
                write_bytes(file, arr.geom.center, '>f4')
                unused_header_space -= 60

            # fill empty header space
            file.write(bytearray(unused_header_space))

            # write array data
            write_bytes(file, np.ravel(arr.data, order='F'), self.dtype_from_id(dtype_id))

            # write scan parameters
            write_bytes(file, arr.metadata.get('tr', 0.0), '>f4')
            write_bytes(file, arr.metadata.get('fa', 0.0), '>f4')
            write_bytes(file, arr.metadata.get('te', 0.0), '>f4')
            write_bytes(file, arr.metadata.get('ti', 0.0), '>f4')

            # compute FOV
            volsize = pad_vector_length(arr.baseshape, 3, 1)
            fov = max(arr.geom.voxsize * volsize) if is_image else arr.shape[0]
            write_bytes(file, fov, '>f4')

            # write lookup table tag
            if arr.labels is not None:
                fsio.write_tag(file, fsio.tags.old_colortable)
                fsio.write_binary_lookup_table(file, arr.labels)

            # phase encode direction
            pedir = arr.metadata.get('phase-encode-direction', 'UNKNOWN')
            fsio.write_tag(file, fsio.tags.pedir, len(pedir))
            file.write(pedir.encode('utf-8'))

            # field strength
            fsio.write_tag(file, fsio.tags.fieldstrength, 4)
            write_bytes(file, arr.metadata.get('field-strength', 0.0), '>f4')

            # write history tags
            for hist in arr.metadata.get('history', []):
                fsio.write_tag(file, fsio.tags.history, len(hist))
                file.write(hist.encode('utf-8'))


class NiftiArrayIO(protocol.IOProtocol):
    """
    Array IO protocol for nifti files.
    """
    name = 'nifti'
    extensions = ('.nii.gz', '.nii')

    def __init__(self):
        try:
            import nibabel as nib
        except ImportError:
            raise ImportError('the `nibabel` python package must be installed for nifti IO')
        self.nib = nib

    def load(self, filename, atype):
        """
        Read array from a nifiti file.

        Parameters
        ----------
        filename : str
            File path read.
        atype : class
            FramedArray subclass to load.

        Returns
        -------
        FramedArray
            Array object loaded from file.
        """
        nii = self.nib.load(filename)
        data = nii.get_data()
        arr = atype(data)
        if isinstance(arr, FramedImage):
            matrix = nii.get_affine()
            voxsize = nii.header['pixdim'][1:4]
            arr.geom.update(vox2world=matrix, voxsize=voxsize)
        return arr

    def save(self, arr, filename):
        """
        Write array to a nifti file.

        Parameters
        ----------
        arr : FramedArray
            Array to save.
        filename : str
            Target file path.
        """
        isimage = isinstance(arr, FramedImage)
        matrix = arr.geom.vox2world.matrix if isimage else np.eye(4)
        nii = self.nib.Nifti1Image(arr.data, matrix)
        if is_image:
            nii.header['pixdim'][1:4] = arr.voxsize
        self.nib.save(nii, filename)


class ImageSliceIO(protocol.IOProtocol):
    """
    Generic array IO protocol for common image formats.
    """

    def __init__(self):
        try:
            from PIL import Image
        except ImportError:
            raise ImportError(f'the `pillow` python package must be installed for {self.name} IO')
        self.Image = Image

    def save(self, arr, filename):
        self.Image.fromarray(arr.data).save(filename)

    def load(self, filename):
        image = np.asarray(self.Image.open(filename))
        return Slice(image)


class JPEGArrayIO(ImageSliceIO):
    name = 'jpeg'
    extensions = ('.jpeg', '.jpg')


class PNGArrayIO(ImageSliceIO):
    name = 'png'
    extensions = '.png'


class TIFFArrayIO(ImageSliceIO):
    name = 'tiff'
    extensions = ('.tif', '.tiff')


# enabled array IO protocol classes
array_io_protocols = [
    MGHArrayIO,
    NiftiArrayIO,
    JPEGArrayIO,
    PNGArrayIO,
    TIFFArrayIO,
]
