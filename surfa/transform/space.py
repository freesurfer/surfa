class Space:

    """
    Here are the 3 spaces supported (see https://github.com/freesurfer/freesurfer/blob/dev/include/mri.h)
        FS_COORDS_UNKNOWN
        FS_COORDS_TKREG_RAS   - Freesurfer surface RAS space
        FS_COORDS_SCANNER_RAS - scanner RAS space
        FS_COORDS_VOXEL       - voxel space
    """
    # see defines in https://github.com/freesurfer/freesurfer/blob/dev/include/mri.h
    FS_COORDS_UNKNOWN = 0
    FS_COORDS_TKREG_RAS = 1
    FS_COORDS_SCANNER_RAS = 2
    FS_COORDS_VOXEL = 3

    # to be consistent with sf.transform.Space
    # 'voxel'   = voxel space
    # 'world'   = scanner RAS space
    # 'surface' = Freesurfer surface RAS space (tkreg space)
    LETTER_TO_CODE = {
        'voxel'   : FS_COORDS_VOXEL,
        'world'   : FS_COORDS_SCANNER_RAS,
        'surface' : FS_COORDS_TKREG_RAS,
        }
    
    # consistent with sf.transform.Space
    CODE_TO_LETTER = {
        FS_COORDS_VOXEL       : 'voxel',
        FS_COORDS_SCANNER_RAS : 'world',
        FS_COORDS_TKREG_RAS   : 'surface',
        }    

    def __init__(self, name):
        """
        Coordinate space representation. Supported spaces are:

            - voxel: Voxel (or image) coordinate space.
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
        # surface or mesh space
        elif name in ('s', 'surf', 'surface', 'm', 'mesh'):
            name = 'surface'
        # voxel or image space
        elif name in ('i', 'image', 'img', 'v', 'vox', 'voxel'):
            name = 'voxel'
        else:
            raise ValueError(f'unknown space: {name}')

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

    def __str__(self):
        return self.name

    def copy(self):
        """
        Create a copy of the space.
        """
        return Space(self.name)

    @property
    def name(self):
        """
        Primary coordinate system name.
        """
        return self._name


def cast_space(obj, allow_none=True, copy=False):
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
    if obj is None and allow_none:
        return obj

    if isinstance(obj, str):
        return Space(obj)

    if isinstance(obj, Space):
        return obj.copy() if copy else obj

    raise ValueError('cannot convert type %s to Space object' % type(obj).__name__)
