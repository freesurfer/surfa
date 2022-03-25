import numpy as np


def conform_ndim(arr, ndim):
    """
    TODOC
    """
    arr = np.asarray(arr)
    if arr.ndim > ndim:
        raise ValueError(f'Cannot conform array of shape {arr.shape} to {ndmi}D.')
    for _ in range(ndim - arr.ndim):
        arr = np.expand_dims(arr, axis=-1)
    return arr
