import os
import numpy as np

from surfa.core.framed import FramedArray
from surfa.core.array import pad_vector_length
from surfa.transform.geometry import ImageGeometry
from surfa.transform.geometry import cast_image_geometry
from surfa.transform import orientation as otn
from surfa.transform.affine import cast_affine
from surfa.image.slicing import sane_slicing
from surfa.image.slicing import slicing_parameters
from surfa.image.interp import interpolate


class FramedImage(FramedArray):
    """
    Abstract class defining an ND image array with data frames and associated geometry (i.e. data
    elements have a mapable relationship to a world-space coordinate system). This base class includes
    generic support for 3D and 2D FramedArray classes, which are later defined by Volume and Slice classes.
    """

    def __init__(self, basedim, data, geometry=None, **kwargs):
        super().__init__(basedim, data, **kwargs)
        self.geom = geometry

    @property
    def geom(self):
        """
        ImageGeometry object that positions image coordinates in 3D world space.
        """
        return self._geometry

    @geom.setter
    def geom(self, geometry):
        if geometry is None:
            geometry = ImageGeometry(shape=self.baseshape)
        else:
            geometry = cast_image_geometry(geometry).reshape(self.baseshape, copy=True)
        setattr(self, '_geometry', geometry)

    def __geometry__(self):
        return self.geom

    def _shape_changed(self):
        """
        Reshape geometry when the underlying shape changes.
        """
        self._geometry = self._geometry.reshape(self.baseshape)

    def __getitem__(self, index_expression):
        return self._crop(index_expression)

    def _crop(self, index_expression):

        # extract the starting coordinate of the cropping
        sane_expression = sane_slicing(self.shape, index_expression)[:self.basedim]
        start, step = slicing_parameters(sane_expression)
        start = pad_vector_length(start, 3, 0)
        step = pad_vector_length(step, 3, 1)

        if np.any(step < 1):
            raise NotImplementedError

        # use the original index_expression to crop the raw array
        cropped_data = self.data[index_expression]

        # 
        rotation = self.geom.rotation
        voxsize = self.geom.voxsize * step

        # 
        cut_axes = [isinstance(x, int) for x in sane_expression]
        num_axis_cuts = np.count_nonzero(cut_axes)
        if (self.basedim == 2 and num_axis_cuts > 0):
            # 
            return cropped_data
        elif num_axis_cuts == 1:
            # 
            cropped_basedim = 2
            cut_index = cut_axes.index(True)
            inter_baseshape = np.insert(cropped_data.shape, cut_index, 1)[:self.basedim]
            if cut_index < 2:
                axis_swap = [1, 2, 0] if cut_index == 0 else [0, 2, 1]
                rotation = rotation[:, axis_swap]
                voxsize = voxsize[axis_swap]
        else:
            # 
            cropped_basedim = self.basedim
            inter_baseshape = np.asarray(cropped_data.shape[:self.basedim])

        # compute the new geometry
        inter_baseshape = pad_vector_length(inter_baseshape, 3, 1)
        matrix = self.geom.vox2world.matrix.copy()
        matrix[:3, 3] = self.geom.vox2world.transform(start)
        image_center = np.append(inter_baseshape * step / 2, 1)
        world_center = np.matmul(matrix, image_center)[:3]
        geometry = ImageGeometry(
            shape=cropped_data.shape[:cropped_basedim],
            center=world_center,
            rotation=rotation,
            voxsize=voxsize,
        )

        # construct cropped volume
        itype = Slice if cropped_basedim == 2 else Volume
        cropped = itype(cropped_data, geometry=geometry, metadata=self.metadata)
        return cropped

    def resize(self, voxsize, method='linear', copy=False):
        """
        Reslice image to voxelsize.
        """
        if self.basedim == 2:
            raise NotImplementedError
        if self.nframes > 1:
            raise NotImplementedError

        if np.isscalar(voxsize):
            # deal with a scalar voxel size input
            voxsize = np.repeat(voxsize, 3).astype('float')
        else:
            # pad to ensure array has length of 3
            voxsize = np.asarray(voxsize, dtype='float')
            check_array(voxsize, ndim=1, shape=(2, 3), name='voxsize')
            voxsize = pad_vector_length(voxsize, 3, 1, copy=False)

        # check if anything needs to be done
        if np.allclose(self.geom.voxsize, voxsize, atol=1e-5, rtol=0):
            return self.copy() if copy else self

        baseshape3D = pad_vector_length(self.baseshape, 3, 1, copy=False)
        target_shape = np.asarray(self.geom.voxsize, dtype='float') * baseshape3D / voxsize
        target_shape = tuple(np.ceil(target_shape).astype(int))

        target_geom = ImageGeometry(
            shape=target_shape,
            voxsize=voxsize,
            rotation=self.geom.rotation,
            center=self.geom.center)
        affine = self.geom.world2vox @ target_geom.vox2world
        interped = interpolate(self.framed_data, target_shape, method, affine.matrix)
        return self.__class__(data=interped, geometry=target_geom, metadata=self.metadata)

    def resample_like(self, target, method='linear'):
        """
        Resample with a particular image geometry.
        """
        if self.basedim == 2:
            raise NotImplementedError
        target_geom = cast_image_geometry(target)
        affine = self.geom.world2vox @ target_geom.vox2world
        interped = interpolate(self.framed_data, target_geom.shape, method, affine.matrix)
        return self.__class__(data=interped, geometry=target_geom, metadata=self.metadata)

    def transform(self, affine=None, disp=None, method='linear', rotation='corner', resample=True):
        """
        Apply a transform.
        """
        if self.basedim == 2:
            raise NotImplementedError
        if self.nframes > 1:
            raise NotImplementedError
        if resample is False and affine is not None:
            raise NotImplementedError

        if affine is not None:
            affine = cast_affine(affine).inverse().matrix
            target_shape = self.baseshape
            target_geom = self.geom

        interped = interpolate(self.framed_data, target_shape, method, affine=affine, disp=disp, rotation=rotation)
        return self.__class__(data=interped, geometry=target_geom, metadata=self.metadata)

    def reorient(self, orientation, copy=True):
        """
        Realigns image data and world matrix to conform to a specific slice orientation.
        """
        if self.basedim == 2:
            raise NotImplementedError
        if self.nframes > 1:
            raise NotImplementedError

        trg_orientation = orientation.upper()
        src_orientation = otn.rotation_matrix_to_orientation(self.geom.vox2world.matrix)
        if trg_orientation == src_orientation.upper():
            return self.copy() if copy else self

        # extract world axes
        get_world_axes = lambda aff: np.argmax(np.absolute(np.linalg.inv(aff)), axis=0)
        trg_matrix = otn.orientation_to_rotation_matrix(trg_orientation)
        src_matrix = otn.orientation_to_rotation_matrix(src_orientation)
        world_axes_trg = get_world_axes(trg_matrix[:self.basedim, :self.basedim])
        world_axes_src = get_world_axes(src_matrix[:self.basedim, :self.basedim])

        voxsize = np.asarray(self.geom.voxsize)
        voxsize = voxsize[world_axes_src][world_axes_trg]

        # initialize new
        data = self.data.copy()
        affine = self.geom.vox2world.matrix.copy()

        # align axes
        affine[:, world_axes_trg] = affine[:, world_axes_src]
        for i in range(self.basedim):
            if world_axes_src[i] != world_axes_trg[i]:
                data = np.swapaxes(data, world_axes_src[i], world_axes_trg[i])
                swapped_axis_idx = np.where(world_axes_src == world_axes_trg[i])
                world_axes_src[swapped_axis_idx], world_axes_src[i] = world_axes_src[i], world_axes_src[swapped_axis_idx]

        # align directions
        dot_products = np.sum(affine[:3, :3] * trg_matrix[:3, :3], axis=0)
        for i in range(self.basedim):
            if dot_products[i] < 0:
                data = np.flip(data, axis=i)
                affine[:, i] = - affine[:, i]
                affine[:3, 3] = affine[:3, 3] - affine[:3, i] * (data.shape[i] - 1)

        # update geometry
        target_geom = ImageGeometry(
            shape=data.shape[:3],
            vox2world=affine,
            voxsize=voxsize)
        return self.__class__(data, geometry=target_geom, metadata=self.metadata)

    def reshape(self, shape):
        """
        Returns a volume fit to a given shape. Image will be centered in the conformed volume.
        """
        if self.basedim == 2:
            raise NotImplementedError
        if self.nframes > 1:
            raise NotImplementedError

        delta = (np.array(shape) - np.array(self.baseshape)) / 2
        low = np.floor(delta).astype(int)
        high = np.ceil(delta).astype(int)

        c_low = np.clip(low, 0, None)
        c_high = np.clip(high, 0, None)
        conformed_data = np.pad(self.data.squeeze(), list(zip(c_low, c_high)), mode='constant')

        # note: low and high are intentionally swapped here
        c_low = np.clip(-high, 0, None)
        c_high = conformed_data.shape[:3] - np.clip(-low, 0, None)
        cropping = tuple([slice(a, b) for a, b in zip(c_low, c_high)])
        conformed_data = conformed_data[cropping]

        # compute new affine if one exists
        matrix = np.eye(4)
        matrix[:3, :3] = self.geom.vox2world.matrix[:3, :3]
        p0crs = np.clip(-high, 0, None) - np.clip(low, 0, None)
        p0 = self.geom.vox2world(p0crs)
        matrix[:3, 3] = p0
        pcrs = np.append(np.array(conformed_data.shape[:3]) / 2, 1)
        cras = np.matmul(matrix, pcrs)[:3]
        matrix[:3, 3] = 0
        matrix[:3, 3] = cras - np.matmul(matrix, pcrs)[:3]

        # update geometry
        target_geom = ImageGeometry(
            shape=conformed_data.shape[:3],
            vox2world=matrix,
            voxsize=self.geom.voxsize)
        return self.__class__(conformed_data, geometry=target_geom, metadata=self.metadata)

    def conform(self, shape=None, voxsize=1.0, orientation='LIA', method='linear', dtype=None, copy=True):
        """
        Conforms image to a specific shape, type, resolution, and orientation.
        """
        if self.basedim == 2:
            raise NotImplementedError
        if self.nframes > 1:
            raise NotImplementedError

        conformed = self.reorient(orientation, copy=False)
        conformed = conformed.resize(voxsize, method=method, copy=False)
        if shape is not None:
            conformed = conformed.reshape(shape, copy=False)
        if dtype is not None:
            conformed = conformed.astype(dtype, copy=False)
        if copy and conformed is self:
            return self.copy()
        return conformed


class Slice(FramedImage):

    def __init__(self, data, **kwargs):
        super().__init__(basedim=2, data=data, **kwargs)


class Volume(FramedImage):

    def __init__(self, data, **kwargs):
        super().__init__(basedim=3, data=data, **kwargs)
