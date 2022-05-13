import os
from copy import deepcopy
import numpy as np

from surfa.core.array import check_array
from surfa.transform import ImageGeometry
from surfa.transform import image_geometry_equal
from surfa.transform import cast_image_geometry
from surfa.transform import cast_space


class Mesh:

    def __init__(self, vertices, faces=None, space='surf', geometry=None, metadata=None):
        """
        Triangular mesh topology represented by arrays of vertices and faces.

        Parameters
        ----------
        vertices : (V, 3) float
            TODO
        faces : (F, 3) int
            TODO
        space : Space
            Coordinate space of the point data. Defaults to the 'surface' coordinate system.
        geometry : ImageGeometry
            Geometry mapping the point data to world and image coordinates.
        metadata : dict
            Dictionary containing arbitrary array metadata.
        """
        self.vertices = vertices
        self.faces = faces
        self.space = space
        self.geom = geometry

        # initialize and set the private metadata dictionary
        self._metadata = {}
        self.metadata = metadata

    def copy(self):
        """
        Return a deep copy of the object.
        """
        return deepcopy(self)

    def save(self, filename, fmt=None):
        """
        Write mesh to file.

        Parameters
        ----------
        filename : str
            Target filename to write array to.
        fmt : str
            Optional file format to force.
        """
        from surfa.io.mesh import save_mesh
        save_mesh(self, filename, fmt=fmt)

    @property
    def vertices(self):
        """
        Mesh 3D point positions defined by a (V, 3) array, where V corresponds to
        the number of vertices.
        """
        return self._vertices

    @vertices.setter
    def vertices(self, vertices):
        vertices = np.asarray(vertices, dtype=np.float64)
        check_array(vertices, ndim=2, name='vertices')
        if vertices.shape[-1] != 3:
            raise ValueError(f'expected shape (V, 3) for vertices array, but got {vertices.shape}')
        self._vertices = vertices

    @property
    def nvertices(self):
        """
        Total number of vertices in the mesh.
        """
        return len(self.vertices)

    @property
    def faces(self):
        """
        Mesh triangle faces defined by a (F, 3) array, where F corresponds to the
        total number of mesh faces.
        """
        return self._faces

    @faces.setter
    def faces(self, faces):
        faces = np.asarray(faces, dtype=np.int64)
        check_array(faces, ndim=2, name='faces')
        if faces.shape[-1] != 3:
            raise ValueError(f'expected shape (F, 3) for faces array, but got {faces.shape}')
        self._faces = faces

    @property
    def nfaces(self):
        """
        Total number of faces in the mesh.
        """
        return len(self.faces)

    @property
    def space(self):
        """
        Coordinate space of the points.
        """
        return self._space
    
    @space.setter
    def space(self, value):
        self._space = cast_space(value, allow_none=False, copy=True)

    @property
    def geom(self):
        """
        Geometry that maps mesh coordinates to image and world spaces.
        """
        return self._geometry

    @geom.setter
    def geom(self, geometry):
        if geometry is None:
            geometry = ImageGeometry(shape=(256, 256, 256))
        else:
            geometry = cast_image_geometry(geometry, copy=True)
        setattr(self, '_geometry', geometry)

    @property
    def metadata(self):
        """
        Metadata dictionary.
        """
        return self._metadata

    @metadata.setter
    def metadata(self, value):
        """
        Replace the metadata dictionary. Will always make a deep copy of the new dictionary.
        """
        self._metadata = deepcopy(value) if value is not None else {}

    def convert(self, space=None, geometry=None, copy=True):
        """
        Converts mesh vertex positions into a new coordinate space, given a particular
        image geometry.

        Parameters
        ----------
        space : Space
            Target coordinate space.
        geometry : Geometry
            Target image geometry.
        copy : bool
            Return a copy of the mesh when target space and geometry conditions
            are already satisfied.s

        Returns
        -------
        Mesh
            Mesh with converted vertex positions.
        """
        space = self.space if space is None else cast_space(space)
        geometry = self.geom if geometry is None else cast_image_geometry(geometry)

        same_geom = image_geometry_equal(geometry, self.geom)
        same_space = space == self.space

        # return self if no changes are necessary
        if same_geom and same_space:
            return self.copy() if copy else self

        # make copy of the mesh
        converted = self.copy()

        if same_geom:
            # only need to transform the points once if the geometry doesn't change
            converted.vertices = self.geom.affine(self.space, space).transform(self.vertices)
            converted.space = space
        else:
            # if we're updating the geometry, we'll need to pass through world space first
            aff = geometry.affine('world', space) @ self.geom.affine(self.space, 'world')
            converted.vertices = aff(self.vertices)
            converted.space = space
            converted.geom = geometry

        return converted
