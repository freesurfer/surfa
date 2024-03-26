import os
import pathlib
import numpy as np

from surfa import ImageGeometry


def check_file_readability(filename):
    """
    Raise an exception if a file cannot be read.

    Parameters
    ----------
    filename : str
        Path to file.
    """
    if not isinstance(filename, pathlib.Path):
        filename = pathlib.Path(filename)

    if filename.is_dir():
        raise ValueError(f'{filename} is a directory, not a file')

    if not filename.is_file():
        raise FileNotFoundError(f'{filename} is not a file')

    if not os.access(filename, os.R_OK):
        raise PermissionError(f'{filename} is not a readable file')


def read_int(file, size=4, signed=True, byteorder='big'):
    """
    Read integer from a file buffer.

    Parameters
    ----------
    file : BufferedReader
        Opened file buffer.
    size : int
        Byte size.
    signed : bool
        Whether integer is signed.
    byteorder : str
        Memory byte order.

    Returns
    -------
    integer : int
    """
    return int.from_bytes(file.read(size), byteorder=byteorder, signed=signed)


def write_int(file, value, size=4, signed=True, byteorder='big'):
    """
    Write integer to a file buffer.

    Parameters
    ----------
    file : BufferedWriter
        Opened file buffer.
    size : int
        Byte size.
    signed : bool
        Whether integer is signed.
    byteorder : str
        Memory byte order.
    """
    file.write(value.to_bytes(size, byteorder=byteorder, signed=signed))


def read_bytes(file, dtype, count=1):
    """
    Read from a binary file buffer.

    Parameters
    ----------
    file : BufferedReader
        Opened file buffer.
    dtype : np.dtype
        Read into numpy datatype.
    count : int
        Number of elements to read.

    Returns
    -------
    np.ndarray:
        The read dtype array.
    """
    dtype = np.dtype(dtype)
    value = np.fromstring(file.read(dtype.itemsize * count), dtype=dtype)
    if count == 1:
        return value[0]
    return value


def write_bytes(file, value, dtype):
    """
    Write a binary file buffer.

    Parameters
    ----------
    file : BufferedWriter
        Opened file buffer.
    value : array_like
        Data to write.
    dtype : np.dtype
        Datatype to save as.
    """
    file.write(np.asarray(value).astype(dtype, copy=False).tobytes())


def read_geom(file, niftiheaderext=False):
    """
    Read an image geometry from a binary file buffer. See VOL_GEOM.read() in mri.h.

    Parameters
    ----------
    file : BufferedReader
        Opened file buffer.

    Returns
    -------
    ImageGeometry
        Image geometry.
    bool
        True if the geometry is valid.
    str
        File name associated with the geometry.
    niftiheaderext : bool
        If True, write for nifti header extension.
    """
    valid = bool(read_bytes(file, '>i4', 1))
    geom = ImageGeometry(
        shape=read_bytes(file, '>i4', 3).astype(int),
        voxsize=read_bytes(file, '>f4', 3),
        rotation=read_bytes(file, '>f4', 9).reshape((3, 3), order='F'),
        center=read_bytes(file, '>f4', 3),
    )

    len_fname_max = 512
    if (not niftiheaderext):
        fname = file.read(len_fname_max).decode('utf-8').rstrip('\x00')
    else:
        # variable length fname, if length = 0, no fname output follows
        # read the first len_max bytes, skip the rest
        len_fname = read_bytes(file, '>i4', 1)
        to_read = len_fname
        if (len_fname > len_fname_max):
            to_read = len_fname_max

        fname = file.read(to_read).decode('utf-8').rstrip('\x00')
        remaining = len_fname - to_read
        if (remaining > 0):
            file.read(remaining)
    return geom, valid, fname


def write_geom(file, geom, valid=True, fname='', niftiheaderext=False):
    """
    Write an image geometry to a binary file buffer. See VOL_GEOM.write() in mri.h.

    Parameters
    ----------
    file : BufferedWriter
        Opened file buffer.
    geom : ImageGeometry
        Image geometry.
    valid : bool
        True if the geometry is valid.
    fname : str
        File name associated with the geometry.
    niftiheaderext : bool
        If True, write for nifti header extension.
    """
    write_bytes(file, valid, '>i4')

    voxsize, rotation, center = geom.shearless_components()
    write_bytes(file, geom.shape, '>i4')
    write_bytes(file, voxsize, '>f4')
    write_bytes(file, np.ravel(rotation, order='F'), '>f4')
    write_bytes(file, center, '>f4')

    len_fname_max = 512
    if (not niftiheaderext):
        # right-pad with '/x00' to 512 bytes
        file.write(fname[:len_fname_max].ljust(len_fname_max, '\x00').encode('utf-8'))
    else:
        # variable length fname, if length = 0, no fname output follows
        len_fname = len(fname)
        if (len_fname > len_fname_max):
            len_fname = len_fname_max
        write_bytes(file, len_fname, '>i4')
        if (len_fname > 0):
            file.write(fname.encode('utf-8'))
