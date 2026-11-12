import numpy as np
import pytest
import surfa as sf
from scipy.spatial import ConvexHull


def _fibonacci_sphere(n):
    i = np.arange(n) + 0.5
    z = 1 - 2 * i / n
    r = np.sqrt(1 - z * z)
    t = np.pi * (1 + 5 ** 0.5) * i
    return np.stack([r * np.cos(t), r * np.sin(t), z], axis=1)


def _nonuniform_sphere():
    """
    Unit sphere with dense polar caps and a very coarse equatorial belt, mimicking
    the triangle-size distortion left by spherical registration.
    """
    dense = _fibonacci_sphere(20000)
    dense = dense[np.abs(dense[:, 2]) > 0.3]
    coarse = _fibonacci_sphere(120)
    coarse = coarse[np.abs(coarse[:, 2]) <= 0.25]
    # the axis points pin the bounding box so the mesh passes the sphere check
    points = np.concatenate([dense, coarse, np.eye(3), -np.eye(3)])
    return points, ConvexHull(points).simplices


@pytest.mark.parametrize('neighborhood', [3, 10, 30])
def test_barycentric_spherical_map_never_leaves_points_unmapped(neighborhood):
    """
    Regression test for the [0, 0, 0] "bullet hole" artefact: target points whose
    containing triangle is not among the `neighborhood` nearest centroids must fall
    back to the nearest face instead of being left with face -1 and zero weights.
    """
    points, faces = _nonuniform_sphere()
    source = sf.Mesh(points * 100, faces)

    # targets inside the largest triangles, close to the vertex nearest to a dense cap
    area = np.linalg.norm(np.cross(points[faces[:, 1]] - points[faces[:, 0]],
                                   points[faces[:, 2]] - points[faces[:, 0]]), axis=1)
    targets = []
    for face in faces[area > np.percentile(area, 99.5)]:
        weights = np.full(3, 0.05)
        weights[np.argmax(np.abs(points[face, 2]))] = 0.9
        p = (weights[:, None] * points[face]).sum(0)
        targets.append(p / np.linalg.norm(p))
    target = sf.Mesh(np.asarray(targets) * 100)

    face_idx, bary = sf.sphere.barycentric_spherical_map(source, target, neighborhood=neighborhood)
    assert np.all(face_idx >= 0)
    np.testing.assert_allclose(bary.sum(1), 1.0, atol=1e-6)

    sampled = (bary[:, :, None] * source.vertices[source.faces[face_idx]]).sum(1)
    assert np.all(np.linalg.norm(sampled, axis=1) > 1.0)


def test_barycentric_resampling_preserves_radius():
    source_points = _fibonacci_sphere(2000)
    target_points = _fibonacci_sphere(3000)
    source = sf.Mesh(source_points * 100, ConvexHull(source_points).simplices)
    target = sf.Mesh(target_points * 100, ConvexHull(target_points).simplices)
    resampled = sf.sphere.SphericalResamplingBarycentric(source, target).sample(source.vertices)
    radii = np.linalg.norm(resampled, axis=1)
    assert radii.min() > 99.0 and radii.max() <= 100.0 + 1e-6
