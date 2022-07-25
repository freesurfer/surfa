import numpy as np
import surfa as sf

from scipy.interpolate import RegularGridInterpolator

from surfa.core.array import normalize
from surfa.mesh.overlay import cast_overlay
from surfa.image.framed import cast_slice


def mesh_is_sphere(mesh):
    """
    Test whether mesh repesents a sphere. The mesh must (1) have a center that does
    not deviate from zero by more than 0.1% of its average radius and (2) have a
    standard deviation in radii not greater than 1% of it's average.

    Parameters
    ----------
    mesh : Mesh
        Spherical mesh to test.

    Returns
    -------
    result : bool
    """
    minc = mesh.vertices.min(0)
    maxc = mesh.vertices.max(0)
    radius = np.mean(maxc - minc) / 2
    center = np.mean((minc, maxc), axis=0)

    if np.any(np.abs(center) > (radius * 1e-3)):
        return False

    radii = np.sqrt(np.sum(mesh.vertices ** 2, 1))
    if np.std(radii) > (radius * 1e-2):
        return False

    return True


def require_sphere(mesh):
    """
    Return an exception if the mesh does not qualify as a valid sphere.

    Parameters
    ----------
    mesh : Mesh
        Spherical mesh to test.
    """
    if not mesh.is_sphere:
        message = ('mesh is not spherical, meaning its center is not close to zero '
                   'or there is substantial variability across radii')
        raise ValueError(message)


def cartesian_to_spherical(points):
    """
    Convert a set of cartesian points to spherical coordinates (phi, theta) around the origin.

    Parameters
    ----------
    points : (n, 3) float
        Array of (x, y, z) spherical points to convert.

    Returns
    -------
    spherical : (n, 2) float
    """
    p = points
    theta = np.arctan2(p[:, 1], p[:, 0])
    phi = np.arctan2(np.sqrt(p[:, 0] ** 2 + p[:, 1] ** 2), p[:, 2])
    mask = theta < 0
    theta[mask] = 2 * np.pi + theta[mask]
    return np.stack([phi, theta], axis=-1)


def spherical_to_cartesian(points):
    """
    Convert a set of spherical coordinates (phi, theta) to cartesian coordinates around
    the origin.

    Parameters
    ----------
    points : (n, 2) float
        Array of (phi, theta) points to convert.

    Returns
    -------
    cartesian : (n, 3) float
    """
    x = np.sin(points[:, 0]) * np.cos(points[:, 1])
    y = np.sin(points[:, 0]) * np.sin(points[:, 1])
    z = np.cos(points[:, 0])
    return np.stack([x, y, z], axis=1)


class SphericalResamplingNearest:

    def __init__(self, source, target):
        """
        Nearest-neighbor map to transfer vertex information between two aligned spheres.
        The computed map will interpolate scalars from the source surface mesh to the
        target surface mesh.

        Parameters
        ----------
        source, target : Mesh
        """
        require_sphere(source)
        require_sphere(target)

        min_radius = np.sqrt(np.sum(source.vertices ** 2, 1)).min() * 0.99
        points = normalize(target.vertices) * min_radius
        nn, _ = sphere.nearest_vertex(points)
        self._vertices = nn
        self._nv = source.nvertices

    def sample(self, overlay):
        """
        Sample overlay values.

        Parameters
        ----------
        overlay : Overlay
            Scalar point values to resample to the target sphere graph
            from the source sphere mesh.

        Returns
        -------
        resampled : Overlay
        """
        overlay = cast_overlay(overlay)
        if overlay.shape[0] != self._nv:
            raise ValueError(f'overlay must correspond to {self._nv} points, but '
                             f'got {overlay.baseshape[0]} points')
        return overlay.new(overlay[self._vertices])


class SphericalResamplingBarycentric:

    def __init__(self, source, target):
        """
        Barycentric map to transfer vertex information between two aligned spheres.
        The computed map will interpolate scalars from the source surface mesh to the
        target surface mesh.

        Parameters
        ----------
        source, target : Mesh
        """
        require_sphere(source)
        require_sphere(target)

        dirs = normalize(target.vertices)
        min_radius = np.sqrt(np.sum(source.vertices ** 2, 1)).min() * 0.99
        origins = dirs * min_radius
        faces, dists, bary = source.ray_intersection(origins, dirs)

        self._nv = source.nvertices
        self._vertices = source.faces[faces]
        self._weights = bary[:, :, np.newaxis]

    def sample(self, overlay):
        """
        Sample overlay values.

        Parameters
        ----------
        overlay : Overlay
            Scalar point values to resample to the target sphere graph
            from the source sphere mesh.

        Returns
        -------
        resampled : Overlay
        """
        overlay = cast_overlay(overlay)
        if overlay.shape[0] != self._nv:
            raise ValueError(f'overlay must correspond to {self._nv} points, but '
                             f'got {overlay.baseshape[0]} points')
        sampled = overlay.framed_data[self._vertices]
        weighted = np.sum(sampled * self._weights, axis=-2)
        return overlay.new(weighted)


class SphericalMapNearest:

    def __init__(self, sphere, shape=(256, 512)):
        """
        A nearest-neighbor to map spherical surface overlays into a 2D
        image grid with (phi, theta) units.

        Parameters
        ----------
        sphere : Mesh
            Spherical mesh to build parameterization map on.
        shape :  tuple of int
            2D shape of the output parameterization map.
        """
        require_sphere(sphere)
        self._shape = shape
        self._nv = sphere.nvertices

        points = np.zeros((*shape, 2))
        points[:, :, 0] = np.linspace(0, np.pi, shape[0] + 1)[:-1, np.newaxis]
        points[:, :, 1] = np.linspace(0, 2 * np.pi, shape[1])[np.newaxis]
        points = points.reshape((-1, 2), order='C')

        points = spherical_to_cartesian(points) * np.sqrt(np.sum(sphere.vertices ** 2, 1)).min()
        nn, _ = sphere.nearest_vertex(points)
        self._map_forward = nn.reshape(shape, order='C')

        nn, _ = sf.Mesh(points).nearest_vertex(sphere.vertices)
        self._map_backward = nn

    def parameterize(self, overlay):
        """
        Parameterize a spherical surface overlay into a 2D (phi, theta) map.

        Parameters
        ----------
        overlay : Overlay
            Overlay to parameterize.

        Returns
        -------
        map : Slice
            Sampled image parameterization.
        """
        overlay = cast_overlay(overlay)
        if overlay.shape[0] != self._nv:
            raise ValueError(f'overlay must correspond to {self._nv} points, but '
                             f'got {overlay.baseshape[0]} points')
        return sf.Slice(overlay[self._map_forward], labels=overlay.labels)

    def sample(self, image):
        """
        Sample a parameterized 2D (phi, theta) map back into a surface overlay.
        
        Parameters
        ----------
        map : Slice
            2D image parameterization.

        Returns
        -------
        sampled : Overlay
            Overlay sampled from the parameterization.
        """
        image = cast_slice(image)
        if not np.array_equal(image.baseshape, self._shape):
            raise ValueError(f'parameterization map must be of shape {self._shape}, '
                             f'but got shape {image.baseshape}')
        sampled = image.data.reshape(-1, image.nframes)[self._map_backward]
        return sf.Overlay(sampled, labels=image.labels)


class SphericalMapBarycentric:

    def __init__(self, sphere, shape=(256, 512)):
        """
        A barycentric interpolator to map spherical surface overlays into a 2D
        image grid with (phi, theta) units.

        Parameters
        ----------
        sphere : Mesh
            Spherical mesh to build parameterization map on.
        shape :  tuple of int
            2D shape of the output parameterization map.
        """
        require_sphere(sphere)
        self._shape = shape
        self._sphere_coords = cartesian_to_spherical(sphere.vertices)
        self._nv = sphere.nvertices

        points = np.zeros((*shape, 2))
        points[:, :, 0] = np.linspace(0, np.pi, shape[0])[:, np.newaxis]
        points[:, :, 1] = np.linspace(0, 2 * np.pi, shape[1] + 1)[np.newaxis, :-1]
        points = points.reshape((-1, 2), order='C')
        
        dirs = spherical_to_cartesian(points)
        origins = dirs * np.sqrt(np.sum(sphere.vertices ** 2, 1)).min() * 0.99
        faces, dists, bary = sphere.ray_intersection(origins, dirs)

        self._forward_vertices = sphere.faces[faces]
        self._forward_weights = bary[:, :, np.newaxis]

        x = np.linspace(0, np.pi, shape[0])
        y = np.linspace(0, 2 * np.pi, shape[1] + 1)
        self._meshgrid = (x, y)

    def parameterize(self, overlay):
        """
        Parameterize a spherical surface overlay into a 2D (phi, theta) map.

        Parameters
        ----------
        overlay : Overlay
            Overlay to parameterize.

        Returns
        -------
        map : Slice
            Sampled image parameterization.
        """
        overlay = cast_overlay(overlay)
        if overlay.shape[0] != self._nv:
            raise ValueError(f'overlay must correspond to {self._nv} points, but '
                             f'got {overlay.baseshape[0]} points')
        sampled = overlay.framed_data[self._forward_vertices]
        weighted = np.sum(sampled * self._forward_weights, axis=-2)
        reshaped = weighted.reshape((*self._shape, -1), order='C')
        return sf.Slice(reshaped, labels=overlay.labels)

    def sample(self, image):
        """
        Sample a parameterized 2D (phi, theta) map back into a surface overlay.
        
        Parameters
        ----------
        map : Slice
            2D image parameterization.

        Returns
        -------
        sampled : Overlay
            Overlay sampled from the parameterization.
        """
        image = cast_slice(image)
        if not np.array_equal(image.baseshape, self._shape):
            raise ValueError(f'parameterization map must be of shape {self._shape}, '
                             f'but got shape {image.baseshape}')
        data = np.concatenate([image.data, image.data[:, :1]], axis=1)
        interped = RegularGridInterpolator(self._meshgrid, data)(self._sphere_coords)
        return sf.Overlay(interped, labels=image.labels)
