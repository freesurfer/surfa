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


# read VOL_GEOM
# also see VOL_GEOM.read() in mri.h 
def read_volgeom(file):
    volgeom = dict(
        valid  = read_bytes(file, '>i4', 1),
                        
        width  = read_bytes(file, '>i4', 1),
        height = read_bytes(file, '>i4', 1),
        depth  = read_bytes(file, '>i4', 1),
                       
        xsize  = read_bytes(file, '>f4', 1),
        ysize  = read_bytes(file, '>f4', 1),
        zsize  = read_bytes(file, '>f4', 1),
                        
        x_r    = read_bytes(file, '>f4', 1),
        x_a    = read_bytes(file, '>f4', 1),
        x_s    = read_bytes(file, '>f4', 1),
        y_r    = read_bytes(file, '>f4', 1),
        y_a    = read_bytes(file, '>f4', 1),
        y_s    = read_bytes(file, '>f4', 1),
        z_r    = read_bytes(file, '>f4', 1),
        z_a    = read_bytes(file, '>f4', 1),
        z_s    = read_bytes(file, '>f4', 1),
                        
        c_r    = read_bytes(file, '>f4', 1),
        c_a    = read_bytes(file, '>f4', 1),
        c_s    = read_bytes(file, '>f4', 1),

        fname  = file.read(512).decode('utf-8').rstrip('\x00')
        )
    return volgeom


# output VOL_GEOM
# also see VOL_GEOM.write() in mri.h
def write_volgeom(file, volgeom):
    write_bytes(file, volgeom['valid'], '>i4')
                        
    write_bytes(file, volgeom['width'], '>i4')
    write_bytes(file, volgeom['height'], '>i4')
    write_bytes(file, volgeom['depth'], '>i4')
                       
    write_bytes(file, volgeom['xsize'], '>f4')
    write_bytes(file, volgeom['ysize'], '>f4')
    write_bytes(file, volgeom['zsize'], '>f4')
                        
    write_bytes(file, volgeom['x_r'], '>f4')
    write_bytes(file, volgeom['x_a'], '>f4')
    write_bytes(file, volgeom['x_s'], '>f4')
    write_bytes(file, volgeom['y_r'], '>f4')
    write_bytes(file, volgeom['y_a'], '>f4')
    write_bytes(file, volgeom['y_s'], '>f4')
    write_bytes(file, volgeom['z_r'], '>f4')
    write_bytes(file, volgeom['z_a'], '>f4')
    write_bytes(file, volgeom['z_s'], '>f4')

    write_bytes(file, volgeom['c_r'], '>f4')
    write_bytes(file, volgeom['c_a'], '>f4')
    write_bytes(file, volgeom['c_s'], '>f4')

    # output 512 bytes padded with '/x00'
    file.write(volgeom['fname'].ljust(512, '\x00').encode('utf-8'))

