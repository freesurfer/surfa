class Space:

    def __init__(self, name):
        """
        Coordinate space representation. Supported spaces are:

            - image: Voxel coordinate space.
            - world: Universal world-space generally represented in RAS orientation.
            - surface: Surface or mesh coordinate space, dependent on base image geometry.

        Parameters
        ----------
        name : str
            Name of coordinate space, case-insensitive.
        """
        name = name.lower()

        # world space, defaulted to RAS space
        if name in ('w', 'world', 'ras'):
            name = 'world'
        # surface space
        elif name in ('s', 'surf', 'surface'):
            name = 'surface'
        # voxel or image space
        elif name in ('i', 'image', 'img', 'vox', 'voxel'):
            name = 'image'
        else:
            raise ValueError(f'Unknown space {name}.')

        self._name = name

    def __eq__(self, other):
        """
        Test whether two spaces are the same.
        """
        try:
            other = cast_space(other, allow_none=False)
        except ValueError:
            return False
        return self.name == other.name

    def __repr__(self):
        return f"sf.Space('{self.name}')"

    @property
    def name(self):
        return self._name


def cast_space(obj, allow_none=True):
    """
    Cast object to coordinate `Space`.

    Parameters
    ----------
    obj : any
        Object to cast.
    allow_none : bool
        Allow for `None` to be successfully passed and returned by cast.

    Returns
    -------
    Space or None
        Casted coordinate space.
    """
    if isinstance(obj, Space):
        return obj

    if obj is None and allow_none:
        return obj

    if isinstance(obj, str):
        return Space(obj)

    raise ValueError('Cannot convert type %s to Space.' % type(obj).__name__)
