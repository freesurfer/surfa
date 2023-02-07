import numpy as np

from surfa.core.array import normalize


class RayIntersectionQuery:

    def __init__(self, mesh):
        """
        Query cache for computing ray intersections on a mesh.

        Parameters
        ----------
        mesh : Mesh
            Mesh to compute ray intersections with.
        """
        try:
            from pyembree.rtcore_scene import EmbreeScene
            from pyembree.mesh_construction import TriangleMesh
        except ImportError:
            raise ImportError('ray intersection tests require that the optional `pyembree` package is installed')

        self._scene = EmbreeScene()
        self._mesh = TriangleMesh(self._scene, mesh.vertices.astype(np.float32), mesh.faces.astype(np.int32))

    def __deepcopy__(self, memo):
        # embree scenes cannot be deep-copied, so lets just return none
        return None

    def ray_intersection(self, origins, dirs):
        """
        Compute mesh intersections for a group of rays.

        Parameters
        ----------
        origins : (n, 3) float
            Ray vector origin points.
        origins : (n, 3) float
            Ray vector directions (can be unnormalized).

        Returns
        -------
        faces : (n,) int
            Indices of intersected faces. Index will be -1 if intersection was not found.
        dists : (n,) float
            Distance to intersection point from ray origin.
        bary : (n, 3) float
            Barycentric weights representing the intersection point on the triangle face.
        """
        res = self._scene.run(origins.astype(np.float32), normalize(dirs.astype(np.float32)), output=True)
        faces = res['primID']
        bary = np.stack((1 - res['u'] - res['v'], res['u'], res['v']), axis=-1)
        dists = res['tfar']
        return (faces, dists, bary)
