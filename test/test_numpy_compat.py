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
