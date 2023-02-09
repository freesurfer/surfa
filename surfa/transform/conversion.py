from surfa.transform.affine import cast_affine


def cast_transform(obj, allow_none=True, copy=False):
    """
    Cast object to either an `Affine` or `FramedImage` representing a deformation field.

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
    Affine, FramedImage, or None
        Casted transform.
    """
    try:
        # first try to convert it to an affine matrix. if that fails
        # we assume it has to be a deformation field
        return cast_affine(obj, allow_none=allow_none, copy=copy)
    except ValueError:
        pass

    try:
        # TODO: importing here to avoid circular import but there's
        # probably a better way to do this
        from surfa.image import cast_image
        deformation = cast_image(obj, allow_none=allow_none, copy=copy)

        # now check to make sure the number of dimensions are reasonable
        if deformation.nframes == deformation.basedim:
            return deformation
    except ValueError:
        pass

    # at this point we know it's a framed image, just not a valid one
    typename = type(obj).__name__
    if getattr(obj, 'shape') is not None:
        typename = f'{typename} of shape {obj.shape}'
    raise ValueError(f'cannot convert type {typename} to affine transform or deformation')
