import os
import numpy as np

from surfa.io import protocol
from surfa.io.utils import check_file_readability
from surfa.io.framed import framed_array_from_4d

from surfa import TimeSeries

def load_timeseries(filename, fmt=None):
    """
    Generic loader for `FramedArray` objects.

    Parameters
    ----------
    filename : str or Path
        File path to read.
    fmt : str, optional
        Explicit file format. If None, we extrapolate from the file extension.

    Returns
    -------
    TimeSeries
        A TimeSeries object loaded file.
    """
    check_file_readability(filename)

    if fmt is None:
        iop = find_timeseries_protocol_by_extension(filename)
    else:
        iop = protocol.find_protocol_by_name(timeseries_io_protocols, fmt)
        if iop is None:
            raise ValueError(f'unknown file format {fmt}')

    return iop().load(filename)


def find_timeseries_protocol_by_extension(filename):
    """
    Find timeseries IO protocol from file extension.

    Parameters
    ----------
    filename : str
        File path to read.

    Returns
    -------
    protocol : IOProtocol
        Matched timeseries IO protocol class.
    """

    # find matching protocol
    iop = protocol.find_protocol_by_extension(timeseries_io_protocols, filename)
    if iop is None:
        basename = os.path.basename(filename).lower()
        raise ValueError(f'timeseries file type {basename} is not supported.')
    
    return iop


class GiftiIO(protocol.IOProtocol):
    """
    GIFTI IO protocol for time-series files.
    """
    name = 'time-series'
    extensions = ('.gii')

    def __init__(self):
        try:
            import nibabel as nib
        except ImportError:
            raise ImportError('the `nibabel` python package must be installed for gifti IO')
        self.nib = nib

    def load(self, filename):
        """
        Read time-series from a gifti file.

        Parameters
        ----------
        filename : str or Path
            File path read.

        Returns
        -------
        TimeSeries
            TimeSeries object loaded from file.
        """

        giftiImage = self.nib.load(filename)
        data = np.expand_dims(giftiImage.agg_data(), axis=(1,2))
        
        arr = framed_array_from_4d(TimeSeries, data)

        return arr


    def save(self, arr, filename):
        """
        Write time-series to a gifti file.

        Parameters
        ----------
        arr : array
            Array to save as gifti time-series
        filename : str or Path
            Target file path.
        """

        raise ValueError(f'ERROR: surfa.io.timeseries.GiftiIO.save() not implemented!')

    
# enabled TimeSeries IO protocol classes
timeseries_io_protocols = [
    GiftiIO,                 # '.gii'
]
