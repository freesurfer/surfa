import copy
import warnings
import numpy as np

import surfa as sf
from surfa.image.interp import interpolate


class DeformField:

    class Format:
        """
        Here are the 4 data formats supported:
            abs_crs   - CRS coordinates in image space
            disp_crs  - displacement CRS, delta = image_CRS - atlas_CRS
            abs_ras   - RAS coordinates in image space
            disp_ras  - displacement RAS, delta = image_RAS - atlas_RAS
        """
        
        abs_crs  = 0
        disp_crs = 1
        abs_ras  = 2
        disp_ras = 3



    #
    # constructor
    def __init__(self, data=None, source=None, target=None,
		 spacing=1, exp_k=0.0, format=Format.abs_crs):
        """
        Class constructor. 
        When it is invoked without any parameters, load(mgzwarp) call is needed after the object is created.

        Class variables:
          _data:  deformation field, 4D numpy array (c, r, s, 3)
               The _data (width x height x depth x nframes) is indexed by atlas CRS.
               frame 0 - image voxel ABS coordinate C, image voxel DISP coordinate C, 
                              RAS ABS coordinate X, or RAS DISP coordinate X
               frame 1 - image voxel ABS coordinate R, image voxel DISP coordinate R,
                              RAS ABS coordinate Y, or RAS DISP coordinate Y
               frame 2 - image voxel ABS coordinate S, image voxel DISP coordinate S,
                              RAS ABS coordinate Z, or RAS DISP coordinate Z
          _format:         DeformField.Format
          _source:         ImageGeometry, source image
          _target:         ImageGeometry, target image
          _spacing:        int    (this is from m3z, not sure if it is really needed)
          _exp_k:          double (this is from m3z, not sure if it is really needed)

        Parameters
        ----------
        data : 4D numpy array (c, r, s, 3)
            dense deformation field
        source : ImageGeometry
            source geometry
        target : ImageGeometry
            target geometry
        format : Format
            deformation field format
        spacing : int
        exp_k : double
        """

        if (data is None and source is None and target is None):
            return
        elif (data is not None and source is not None and target is not None):
            self._data = data
            self._format = format
            self._source  = source
            self._target  = target
            self._spacing    = spacing
            self._exp_k      = exp_k
        else:
            raise ValueError('DeformField constructor: input parameters error')


    #
    # Read input mgz warp file
    def load(self, filename):
        """
        Read input mgz warp file, set up deformation field, source/target geometry

        Parameters
        ----------
        filename : string
            input mgz warp file
        """
        
        mgzwarp = sf.load_volume(filename)

        # check if mgzwarp is a volume
        if (not isinstance(mgzwarp, sf.image.framed.Volume)):
            raise ValueError('DeformField::load() - input is not a Volume')
        
        # check if input is a mgzwarp (intent FramedArrayIntents.warpmap)
        if (mgzwarp.metadata['intent'] != sf.core.framed.FramedArrayIntents.warpmap):
            raise ValueError('DeformField::load() - input is not a mgzwarp Volume')

        self._data = mgzwarp.data
        self._format = mgzwarp.metadata['warpfield_dtfmt']

        # create ImageGeometry object self._source from mgzwarp.metadata['gcamorph_volgeom_src']
        self._source = sf.transform.geometry.volgeom_dict2image_geometry(mgzwarp.metadata['gcamorph_volgeom_src'])

        # create ImageGeometry object self._target from mgzwarp.metadata['gcamorph_volgeom_trg']
        self._target = sf.transform.geometry.volgeom_dict2image_geometry(mgzwarp.metadata['gcamorph_volgeom_trg'])

        # not sure if these two are necessary
        self._spacing   = mgzwarp.metadata['gcamorph_spacing']
        self._exp_k     = mgzwarp.metadata['gcamorph_exp_k']


    #
    # output _data as mgz warp
    def save(self, filename):
        """
        Output _data as mgz warp volume

        Parameters
        ----------
        filename : string
            output mgz warp file
        """
         
        # create a volume from _data
        mgzwarp = sf.image.framed.cast_image(self._data, fallback_geom=self._target)
        
        # set metadata
        mgzwarp.metadata['intent'] = sf.core.framed.FramedArrayIntents.warpmap
        mgzwarp.metadata['gcamorph_volgeom_src'] = sf.transform.geometry.image_geometry2volgeom_dict(self._source)
        mgzwarp.metadata['gcamorph_volgeom_trg'] = sf.transform.geometry.image_geometry2volgeom_dict(self._target)
        
        mgzwarp.metadata['warpfield_dtfmt']  = self._format
        mgzwarp.metadata['gcamorph_spacing'] = self._spacing
        mgzwarp.metadata['gcamorph_exp_k']   = self._exp_k

        # output the volume as mgz warp
        mgzwarp.save(filename, None, sf.core.framed.FramedArrayIntents.warpmap)


    #
    # change deformation field data format
    # return new deformation field, self._data is not changed
    def change_space(self, newformat=Format.abs_crs):
        """
        Change deformation field data format

        Parameters
        ----------
        newformat : Format
            output deformation field format

        Returns
        -------
        data : 4D numpy array (c, r, s, 3)
            converted deformation field with newformat
        """

        if (self._format == newformat):
            return self._data

        # cast vox2world.matrix and world2vox.matrix to float32
        src_vox2ras = self._source.vox2world.matrix.astype('float32')
        src_ras2vox = self._source.world2vox.matrix.astype('float32')
        trg_vox2ras = self._target.vox2world.matrix.astype('float32')

        # reshape self._data to (3, n) array, n = c * s * r
        transform = self._data.astype('float32')
        transform = transform.reshape(-1, 3)     # (n, 3)
        transform = transform.transpose()        # (3, n)

        # target crs grid corresponding to the reshaped (3, n) array
        trg_crs = (np.arange(x, dtype=np.float32) for x in self._data.shape[:3])
        trg_crs = np.meshgrid(*trg_crs, indexing='ij')
        trg_crs = np.stack(trg_crs)
        trg_crs = trg_crs.reshape(3, -1)

        # target ras
        trg_ras = trg_vox2ras[:3, :3] @ trg_crs + trg_vox2ras[:3, 3:]
        
        if (self._format == self.Format.abs_crs):
        #
            if (newformat == self.Format.disp_crs):
                # abs_crs => disp_crs
                deformationfield = transform - trg_crs
            else:
                # abs_crs => abs_ras
                src_ras = src_vox2ras[:3, :3] @ transform + src_vox2ras[:3, 3:]
                if (newformat == self.Format.abs_ras):
                    deformationfield = src_ras
                elif (newformat == self.Format.disp_ras):
                    # abs_ras => disp_ras
                    deformationfield = src_ras - trg_ras
        #
        elif (self._format == self.Format.disp_crs):
        #
            # disp_crs => abs_crs            
            src_crs = transform + trg_crs
            if (newformat == self.Format.abs_crs):
                deformationfield = src_crs
            else:
                # abs_crs => abs_ras
                src_ras = src_vox2ras[:3, :3] @ src_crs + src_vox2ras[:3, 3:]
                if (newformat == self.Format.abs_ras):
                    deformationfield = src_ras
                elif (newformat == self.Format.disp_ras):
                    # abs_ras => disp_ras
                    deformationfield = src_ras - trg_ras
        #
        elif (self._format == self.Format.abs_ras):
        #
            if (newformat == self.Format.disp_ras):
                # abs_ras => disp_ras
                deformationfield = transform - trg_ras
            else:
                # abs_ras => abs_crs            
                src_crs = src_ras2vox[:3, :3] @ transform + src_ras2vox[:3, 3:]
                if (newformat == self.Format.abs_crs):
                    deformationfield = src_crs
                elif (newformat == self.Format.disp_crs):
                    # abs_crs => disp_crs
                    deformationfield = src_crs - trg_crs
        #
        elif (self._format == self.Format.disp_ras):
        #
            # disp_ras => abs_ras
            src_ras = transform + trg_ras
            if (newformat == self.Format.abs_ras):
                deformationfield = src_ras
            else:
                # abs_ras => abs_crs
                src_crs = src_ras2vox[:3, :3] @ src_ras + src_ras2vox[:3, 3:]                
                if (newformat == self.Format.abs_crs):
                    deformationfield = src_crs
                elif (newformat == self.Format.disp_crs):
                    # abs_crs => disp_crs
                    deformationfield = src_crs - trg_crs
        #

        # reshape deformationfield to [c, r, s] x 3
        deformationfield = deformationfield.transpose()
        deformationfield = deformationfield.reshape(*self._data.shape[:3], 3)
        
        return deformationfield


    #
    # apply _data on given image using Cython interpolation in image/interp.pyx
    # return transformed image
    def apply(self, image, method='linear', fill=0):
        """
        Apply dense deformation field to input image volume

        Parameters
        ----------
        image : Volume
            input image Volume

        Returns
        -------
        deformed : Volume
            deformed image
        """

        # check if image is a Volume
        if (not isinstance(image, sf.image.framed.Volume)):
            raise ValueError('DeformField::apply() - input is not a Volume')

        # get the image in the space of the deformation
        #source_data = image.resample_like(self._target).framed_data
        source_data = image.framed_data

        # convert deformation field to disp_crs
        deformationfield = self.change_space(self.Format.disp_crs)

        # do the interpolation, the function assumes disp_crs deformation field
        interpolated = interpolate(source=source_data,
                                   target_shape=self._target.shape,
                                   method=method,
                                   disp=deformationfield,
                                   fill=fill)
        
        deformed = image.new(interpolated, self._target)
        
        return deformed
        

    #
    # _data getter and setter
    @property
    def data(self):
        return self._data
    @data.setter
    def data(self, deformfield):
        self._data = deformfield


    #
    # _format getter and setter
    @property
    def deformationformat(self):
        return self._format
    @deformationformat.setter
    def deformationformat(self, format):
        self._format = format


    #
    # _source getter and setter
    @property
    def source(self):
        return self._source
    @source.setter
    def source(self, geom):
        self._source = geom


    #
    # _target getter and setter
    @property
    def target(self):
        return self._target
    @target.setter
    def target(self, geom):
        self._target = geom


