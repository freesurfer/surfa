import numpy as np

from surfa.core.array import normalize


class IntersectionQuery:

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


def remove_self_intersections(mesh, smoothing_iters=20, max_attempts=100):
    """
    Find and remove mesh self-intersections by smoothing the vertex neighorhood
    around intersecting faces.

    Parameters
    ----------
    mesh : Mesh
        Mesh to be fixed.
    smoothing_iters : int
        Number of laplacian smoothing iterations on offending vertices
        during each global fix attempt.
    max_attempts : int
        Maximum number of global attempts to find and remove intersections.
        When this limit is reached, an exception is thrown if `throw=True`,
        otherwise the partially fixed mesh is returned.
    throw : True
        Throw an exception if number of global attempts surpasses `max_attempts`.

    Returns
    -------
    fixed : Mesh
        Mesh with self-intersections removed.
    """

    # this algorithm involves two steps during each global attempt:
    #   1) mark the vertices of edges that intersect a face triangle
    #   2) perform a laplacian mesh smoothing on these marked vertices
    # this process is repeated until all self-intersections are smoothed away or until
    # the max number of attempts is reached

    # finding self-intersecting faces is the most difficult component here.
    # a nice solution is to use the pyembree ray-tracing utils to quickly determine
    # whether each unique edge (representing a ray with finite length) intersects
    # with any face in the mesh. the major issue here is that there's no easy way to
    # set a threshold on the intersection angle (tangent), so the intersection tests
    # often just returns a hit associated with the edge's adjacent face. from what I
    # can tell, there is no clear way to efficiently ignore adjacent faces during the
    # test. so, the somewhat hacky, but effective, solution is to nudge each edge ray
    # by a small distance in a perpendicular direction. this prevents embree from
    # computing edge intersections with the two adjacent faces, while still being
    # able to detect intersections with other faces.
    edges = mesh.unique_edges
    first_faces = mesh.adjacent_faces[:, 0]

    # do work on a copy of the input
    mesh = mesh.copy()

    for attempt in range(max_attempts):

        # compute the edge vector (ray)
        v = mesh.vertices[edges]
        r = v[:, 1] - v[:, 0]

        # now displace the ray origin a bit so it's not
        # going to intersect with itself (it's own faces)
        c = mesh.face_normals[first_faces]
        o = v[:, 0] + c * 0.0001
        o += normalize(r) * 0.01

        # compute the actual intersection tests
        f, d, _ = mesh.ray_intersection(o, r)

        # compute mask of ray intersections that intersect with a
        # valid face and have an intersection distance less than the
        # length of the original edge (minus a small value to be safe)
        edge_length = np.sqrt(np.sum(r * r, -1)) - 0.05
        ie = (f != -1) & (d < edge_length)

        # there is still a chance that we didn't nudge the edge ray far enough
        # from its original location. we can detect and ignore cases where embree
        # computes intersections that are invalid by checking whether the intersected
        # face contains vertex indices defining the edge.
        y = mesh.faces[f[ie]]
        e1 = edges[ie, 0, np.newaxis]
        e2 = edges[ie, 1, np.newaxis]
        ie[ie] = np.all(e1 != y, -1) & np.any(e2 != y, -1)

        # return early if all removed
        if np.count_nonzero(ie) == 0:
            return mesh

        # mark all vertices associated with bad edges
        marked = np.zeros(mesh.nvertices, dtype=np.uint8)
        np.add.at(marked, edges[:, 0], ie)
        np.add.at(marked, edges[:, 1], ie)
        pinned = marked == 0

        # smooth the marked vertex positions and update
        mesh.vertices = mesh.smooth_overlay(mesh.vertices, iters=smoothing_iters,
                                            step=0.5, weighted=False, pinned=pinned).data

    return mesh
