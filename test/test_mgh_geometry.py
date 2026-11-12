import os
import re
import struct
import subprocess

import pytest
import numpy as np
import surfa as sf


FREESURFER_HOME = os.environ.get('FREESURFER_HOME', '')
MRI_INFO = os.path.join(FREESURFER_HOME, 'bin', 'mri_info')

# geometry given by FreeSurfer's mghRead rule for the files written below
# (checked against mri_info 8.2)
FS_VOXSIZE = {
    -1: (1.0, 1.0, 1.0),
    0: (1.0, 1.0, 1.0),
    1: (0.5, 0.5, 2.0),
}
FS_ORIENTATION = {-1: 'LIA', 0: 'LIA', 1: 'LSP'}
FS_VOX2RAS = {
    -1: [[-1, 0, 0, 2], [0, 0, 1, -3], [0, -1, 0, 2.5], [0, 0, 0, 1]],
    0: [[-1, 0, 0, 2], [0, 0, 1, -3], [0, -1, 0, 2.5], [0, 0, 0, 1]],
    1: [[-0.5, 0, 0, 1], [0, 0, -2, 6], [0, 0.5, 0, -1.25], [0, 0, 0, 1]],
}


def write_mgh(filename, ras_good_flag, shape=(4, 5, 6)):
    """
    Write a uchar MGH file whose header stores 0.5 x 0.5 x 2 mm voxels and an
    LSP rotation, with the given goodRASflag.
    """
    header = struct.pack('>i', 1)
    header += struct.pack('>4i', *shape, 1)
    header += struct.pack('>2i', 0, 1)
    header += struct.pack('>h', ras_good_flag)
    header += struct.pack('>3f', 0.5, 0.5, 2.0)
    header += struct.pack('>9f', -1, 0, 0, 0, 0, 1, 0, -1, 0)
    header += struct.pack('>3f', 0, 0, 0)
    header += bytes(284 - len(header))
    data = np.arange(np.prod(shape), dtype='>u1').tobytes()
    with open(filename, 'wb') as file:
        file.write(header + data + struct.pack('>5f', 0, 0, 0, 0, 0))


@pytest.mark.parametrize('flag', [-1, 0, 1])
def test_mgh_ras_good_flag(tmp_path, flag):
    """
    Test that the stored geometry is used only when goodRASflag > 0, otherwise
    the FreeSurfer default of 1 mm coronal (LIA) voxels, as in mghRead.
    """
    filename = str(tmp_path / f'flag{flag}.mgh')
    write_mgh(filename, flag)
    vol = sf.load_volume(filename)
    assert np.allclose(vol.geom.voxsize, FS_VOXSIZE[flag])
    assert vol.geom.orientation == FS_ORIENTATION[flag]
    assert np.allclose(vol.geom.vox2world.matrix, FS_VOX2RAS[flag])

    # a save then load round trip must keep the geometry
    resaved = str(tmp_path / f'resaved{flag}.mgz')
    vol.save(resaved)
    again = sf.load_volume(resaved)
    assert np.allclose(again.geom.voxsize, FS_VOXSIZE[flag])
    assert np.allclose(again.geom.vox2world.matrix, FS_VOX2RAS[flag])
    assert np.array_equal(again.data, vol.data)


@pytest.mark.skipif(not FREESURFER_HOME or not os.path.isfile(MRI_INFO),
                    reason='FREESURFER_HOME/bin/mri_info not found')
@pytest.mark.parametrize('flag', [-1, 0, 1])
def test_mgh_ras_good_flag_mri_info(tmp_path, flag):
    """
    Test that surfa reads the same geometry as FreeSurfer's mri_info.
    """
    filename = str(tmp_path / f'flag{flag}.mgh')
    write_mgh(filename, flag)
    vol = sf.load_volume(filename)

    def mri_info(option):
        out = subprocess.run([MRI_INFO, option, filename], check=True,
                             capture_output=True, text=True).stdout
        return np.array([float(x) for x in re.findall(r'-?\d+\.\d+', out)])

    assert np.allclose(vol.geom.voxsize, mri_info('--res')[:3])
    assert np.allclose(vol.geom.vox2world.matrix, mri_info('--vox2ras').reshape(4, 4))
