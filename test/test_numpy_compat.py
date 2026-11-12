import sys

import numpy as np
import pytest


sf = pytest.importorskip('surfa')


def _non_native_float32(data):
    byteorder = '>' if sys.byteorder == 'little' else '<'
    return np.asarray(data, dtype=np.float32).astype(np.dtype(np.float32).newbyteorder(byteorder), copy=True)


def _assert_machine_precision_equal(a, b):
    assert a.shape == b.shape
    assert a.dtype == b.dtype
    assert np.issubdtype(a.dtype, np.floating)

    scale = max(
        float(np.max(np.abs(a))),
        float(np.max(np.abs(b))),
        1.0,
    )
    atol = np.finfo(a.dtype).eps * scale
    assert np.allclose(a, b, rtol=0.0, atol=atol), f'max abs diff={np.max(np.abs(a - b))}, atol={atol}'


@pytest.mark.parametrize('method', ['linear', 'nearest'])
def test_resize_non_native_endian_matches_native(method):
    rng = np.random.default_rng(123456)
    data_native = rng.normal(loc=0.1, scale=1.7, size=(9, 7, 5, 2)).astype(np.float32)
    data_non_native = _non_native_float32(data_native)

    vol_native = sf.Volume(data_native)
    vol_non_native = sf.Volume(data_non_native)

    assert vol_non_native.framed_data.dtype.byteorder not in ('=', '|')

    voxsize = np.array([1.3, 0.9, 1.7], dtype=np.float32)
    resized_native = vol_native.resize(voxsize, method=method)
    resized_non_native = vol_non_native.resize(voxsize, method=method)

    assert resized_native.framed_data.shape == resized_non_native.framed_data.shape
    assert resized_native.framed_data.dtype == resized_non_native.framed_data.dtype
    _assert_machine_precision_equal(resized_native.framed_data, resized_non_native.framed_data)


def test_array_protocol_accepts_dtype_and_copy():
    # NumPy 2 passes `copy` to __array__ and warns (DeprecationWarning) when
    # the implementation does not accept it.
    import warnings
    data = np.arange(6, dtype=np.float64)
    overlay = sf.Overlay(data)
    affine = sf.Affine(np.eye(4))
    with warnings.catch_warnings():
        warnings.simplefilter('error', DeprecationWarning)
        copied = np.array(overlay, copy=True)
        assert copied is not overlay.data and np.array_equal(copied, data)
        assert np.asarray(overlay) is overlay.data
        assert np.asarray(overlay, dtype=np.float32).dtype == np.float32
        assert np.array(affine, copy=True) is not affine.matrix
        assert np.asarray(affine) is affine.matrix
        if np.lib.NumpyVersion(np.__version__) >= '2.0.0':
            # NumPy 2 semantics: copy=False must never copy
            with pytest.raises(ValueError):
                np.array(overlay, dtype=np.float32, copy=False)


def test_onehot_no_shape_assignment():
    seg = sf.Volume(np.array([0, 1, 2, 1, 0, 2, 2, 1], dtype=np.int32).reshape(2, 2, 2))
    onehot = seg.onehot([0, 1, 2])
    assert onehot.shape == (2, 2, 2, 3)
    assert np.array_equal(np.argmax(onehot.data, axis=-1), seg.data)


def test_affine_to_warp():
    geom = sf.ImageGeometry(shape=(4, 5, 6))
    affine = sf.Affine(np.eye(4), source=geom, target=geom, space='world')
    warp = affine.to_warp()
    assert warp.shape == (4, 5, 6, 3)
    assert np.allclose(warp.data, 0)


def test_annotation_roundtrip(tmp_path):
    # np.in1d was removed in NumPy 2.4
    lut = sf.LabelLookup()
    lut[0] = ('unknown', [25, 5, 25])
    lut[1] = ('a', [255, 0, 0])
    lut[2] = ('b', [0, 255, 0])
    overlay = sf.Overlay(np.array([0, 1, 2, 1, 0, 2], dtype=np.int32), labels=lut)
    filename = str(tmp_path / 'test.annot')
    overlay.save(filename)
    loaded = sf.load_overlay(filename)
    assert np.array_equal(loaded.data, overlay.data)
