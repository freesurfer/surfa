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
