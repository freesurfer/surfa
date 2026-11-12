import numpy as np
import pytest
import surfa as sf
from surfa.system import kdtree_workers


def test_default_uses_all_cpus(monkeypatch):
    monkeypatch.delenv('SURFA_NUM_THREADS', raising=False)
    assert kdtree_workers() == -1


@pytest.mark.parametrize('value, expected', [('1', 1), ('4', 4), ('-1', -1), (' 2 ', 2), ('', -1)])
def test_env_override(monkeypatch, value, expected):
    monkeypatch.setenv('SURFA_NUM_THREADS', value)
    assert kdtree_workers() == expected


@pytest.mark.parametrize('value', ['0', '-2', 'many'])
def test_invalid_values_raise(monkeypatch, value):
    monkeypatch.setenv('SURFA_NUM_THREADS', value)
    with pytest.raises(ValueError):
        kdtree_workers()


def test_capped_queries_match_default(monkeypatch):
    rng = np.random.default_rng(0)
    vertices = rng.normal(size=(200, 3))
    vertices /= np.linalg.norm(vertices, axis=1, keepdims=True)
    from scipy.spatial import ConvexHull
    mesh = sf.Mesh(vertices, ConvexHull(vertices).simplices)
    points = rng.normal(size=(50, 3))

    monkeypatch.delenv('SURFA_NUM_THREADS', raising=False)
    nn_default, d_default = mesh.nearest_vertex(points)
    dist_default = sf.mesh.surface_distance(points, mesh)

    monkeypatch.setenv('SURFA_NUM_THREADS', '1')
    nn_capped, d_capped = mesh.nearest_vertex(points)
    dist_capped = sf.mesh.surface_distance(points, mesh)

    np.testing.assert_array_equal(nn_default, nn_capped)
    np.testing.assert_array_equal(d_default, d_capped)
    np.testing.assert_array_equal(dist_default, dist_capped)


@pytest.mark.parametrize('value', [1, 3, -1, np.int64(2)])
def test_explicit_workers(monkeypatch, value):
    monkeypatch.delenv('SURFA_NUM_THREADS', raising=False)
    assert kdtree_workers(value) == int(value)


def test_explicit_workers_override_env(monkeypatch):
    monkeypatch.setenv('SURFA_NUM_THREADS', '4')
    assert kdtree_workers() == 4
    assert kdtree_workers(1) == 1
    assert kdtree_workers(-1) == -1
    # an invalid variable is not read when an explicit value is given
    monkeypatch.setenv('SURFA_NUM_THREADS', 'many')
    assert kdtree_workers(2) == 2


@pytest.mark.parametrize('value', [0, -2, 1.5, '2', True])
def test_invalid_explicit_workers_raise(monkeypatch, value):
    monkeypatch.delenv('SURFA_NUM_THREADS', raising=False)
    with pytest.raises(ValueError):
        kdtree_workers(value)


def test_workers_keyword_at_every_query_site(monkeypatch):
    rng = np.random.default_rng(1)
    from scipy.spatial import ConvexHull
    vertices = rng.normal(size=(300, 3))
    vertices /= np.linalg.norm(vertices, axis=1, keepdims=True)
    sphere = sf.Mesh(vertices * 100, ConvexHull(vertices).simplices)
    other = rng.normal(size=(200, 3))
    other /= np.linalg.norm(other, axis=1, keepdims=True)
    target = sf.Mesh(other * 100, ConvexHull(other).simplices)
    points = rng.normal(size=(40, 3)) * 100

    # an invalid variable proves that the keyword, not the variable, is used
    monkeypatch.setenv('SURFA_NUM_THREADS', 'many')
    nn, d = sphere.nearest_vertex(points, workers=1)
    dist = sf.mesh.surface_distance(points, sphere, workers=1)
    faces, bary = sf.sphere.barycentric_spherical_map(sphere, target, workers=1)
    sphere.find_self_intersecting_faces(workers=1)
    sphere.remove_self_intersections(workers=1)
    near = sf.sphere.SphericalResamplingNearest(sphere, target, workers=1)
    bari = sf.sphere.SphericalResamplingBarycentric(sphere, target, workers=1)
    sf.sphere.SphericalMapNearest(sphere, shape=(16, 32), workers=1)
    sf.sphere.SphericalMapBarycentric(sphere, shape=(16, 32), workers=1)
    with pytest.raises(ValueError):
        sphere.nearest_vertex(points)

    monkeypatch.delenv('SURFA_NUM_THREADS')
    nn_all, d_all = sphere.nearest_vertex(points)
    np.testing.assert_array_equal(nn, nn_all)
    np.testing.assert_array_equal(d, d_all)
    np.testing.assert_array_equal(dist, sf.mesh.surface_distance(points, sphere))
    faces_all, bary_all = sf.sphere.barycentric_spherical_map(sphere, target)
    np.testing.assert_array_equal(faces, faces_all)
    np.testing.assert_allclose(bary, bary_all)
