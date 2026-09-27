import numpy as np
import pytest
import surfa as sf


def _octahedron():
    vertices = np.array([
        [1, 0, 0], [-1, 0, 0], [0, 1, 0], [0, -1, 0], [0, 0, 1], [0, 0, -1],
    ], dtype=float)
    faces = np.array([
        [0, 2, 4], [2, 1, 4], [1, 3, 4], [3, 0, 4],
        [2, 0, 5], [1, 2, 5], [3, 1, 5], [0, 3, 5],
    ])
    return sf.Mesh(vertices, faces)


def _reference(mesh, values, method):
    """Per-vertex reduction over incident faces, computed with a plain loop."""
    reduce = {'mean': np.mean, 'sum': np.sum, 'max': np.max, 'min': np.min}[method]
    out = []
    for v in range(mesh.nvertices):
        incident = np.any(mesh.faces == v, axis=1)
        out.append(reduce(values[incident], axis=0))
    return np.asarray(out)


@pytest.mark.parametrize('method', ['mean', 'sum', 'max', 'min'])
def test_face_to_vertex_overlay_single_frame(method):
    mesh = _octahedron()
    values = np.arange(mesh.nfaces, dtype=float)
    result = mesh.face_to_vertex_overlay(sf.Overlay(values), method=method)
    assert result.nframes == 1
    assert result.shape[0] == mesh.nvertices
    np.testing.assert_allclose(np.asarray(result).ravel(), _reference(mesh, values, method))


@pytest.mark.parametrize('method', ['mean', 'sum', 'max', 'min'])
def test_face_to_vertex_overlay_multi_frame(method):
    mesh = _octahedron()
    values = np.stack([np.arange(mesh.nfaces), 2.0 * np.arange(mesh.nfaces)], axis=1)
    result = mesh.face_to_vertex_overlay(sf.Overlay(values), method=method)
    assert result.shape == (mesh.nvertices, 2)
    np.testing.assert_allclose(np.asarray(result), _reference(mesh, values, method))
