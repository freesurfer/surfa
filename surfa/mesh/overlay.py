import os
import numpy as np

from surfa.core.framed import FramedArray


class Overlay(FramedArray):

    def __init__(self, data, **kwargs):
        super().__init__(basedim=1, data=data, **kwargs)


def cast_overlay(obj, allow_none=True, copy=False):
    """
    Cast object to `Overlay` type.

    Parameters
    ----------
    obj : any
        Object to cast.
    allow_none : bool
        Allow for `None` to be successfully passed and returned by cast.
    copy : bool
        Return copy if object is already the correct type.

    Returns
    -------
    Overlay or None
        Casted overlay.
    """
    if obj is None and allow_none:
        return obj

    if isinstance(obj, Overlay):
        return obj.copy() if copy else obj

    if getattr(obj, '__array__', None) is not None:
        return Volume(np.array(obj))

    raise ValueError('cannot convert type %s to overlay' % type(obj).__name__)
