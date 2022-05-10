import os
import numpy as np


def check_file_readability(filename):
    """
    Raise an exception if a file cannot be read.

    Parameters
    ----------
    filename : str
        Path to file.
    """
    if os.path.isdir(filename):
        raise ValueError(f'{filename} is a directory, not a file')
    if not os.path.isfile(filename):
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
