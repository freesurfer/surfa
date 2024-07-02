import os
import gzip
import warnings
import numpy as np

from surfa.io import fsio
from surfa.io import utils as iou
from surfa.transform.geometry import ImageGeometry
from surfa.core.labels import LabelLookup
from surfa.core.framed import FramedArrayIntents


class FSNifti1Extension:
    """
    This class handles Freesurfer Nifti1 header extension IO.

    Class variables:
      _content:      FSNifti1Extension.Content
    """

    def __init__(self):
        """
        FSNifti1Extension Constructor
        """

        # initialization
        self._content = FSNifti1Extension.Content()


    def read(self, fileobj, esize, offset=0):
        """
        Read Freesurfer Nifti1 header extension data from the file-like object.

        Parameters
        ----------
        fileobj : file-like object
            opened file-like object
        esize   : int
            nifti1 header extension size including sizes of esize and ecode
        offset  : int
            offset to Freesurfer Nifti1 Header Extension

        Returns
        -------
        content : FSNifti1Extension.Content
        """

        if (offset > 0):
            fileobj.seek(offset)  # seek to Freesurfer Header Extension

        # freesurfer nifti header extension data is in big endian
        # the first 4 bytes are as following:
        #   endian ">" (1 byte), intent (unsigned short, 2 bytes), version (1 byte)
        fsexthdr = fileobj.read(4)
        self.content.endian = fsexthdr[0]
        self.content.intent = int.from_bytes(fsexthdr[1:3], byteorder='big')
        self.content.version = fsexthdr[3]

        print(f'[DEBUG] FSNifti1Extension.read(): esize = {esize:6d}')
        print(f'[DEBUG] FSNifti1Extension.read(): endian = \'{self.content.endian:c}\', intent = {self.content.intent:d}, version = {self.content.version:d}')

        # process Freesurfer Nifti1 extension tag data
        tagdatalen = esize - 12  # exclude esize, ecode, fsexthdr
        len_tagheader = 12       # tagid (4 bytes), data-length (8 bytes)
        while True:
            # read tagid (4 bytes), data-length (8 bytes)
            (tag, length) = FSNifti1Extension.read_tag(fileobj)

            print(f'[DEBUG] FSNifti1Extension.read(): remaining taglen = {tagdatalen:6d} (tag = {tag:2d}, length = {length:5d})')

            if (tag == 0):
                break

            # embedded lookup table (TAG_OLD_COLORTABLE = 1)
            elif (tag == FSNifti1Extension.Tags.old_colortable):
                self.content.labels = fsio.read_binary_lookup_table(fileobj)

            # command history (TAG_CMDLINE = 3)
            elif (tag == FSNifti1Extension.Tags.history):
                history = fileobj.read(length).decode('utf-8').rstrip('\x00')
                if (self.content.history):
                    self.content.history.append(history)
                else:
                    self.content.history = [history]

            # dof (TAG_DOF = 7)
            elif (tag == FSNifti1Extension.Tags.dof):
                dof = iou.read_int(fileobj, length)
                self.content.dof = dof

            # ras_xform (TAG_RAS_XFORM = 8)
            elif (tag == FSNifti1Extension.Tags.ras_xform):
                self.content.ras_xform = dict(
                    rotation = iou.read_bytes(fileobj, '>f4', 9).reshape((3, 3), order='F'),
                    center   = iou.read_bytes(fileobj, '>f4', 3)
                )

            # gcamorph src & trg geoms (warp) (TAG_GCAMORPH_GEOM = 10)
            elif (tag == FSNifti1Extension.Tags.gcamorph_geom):
                if (not self.content.warpmeta):
                    self.content.warpmeta = {}

                (self.content.warpmeta['source-geom'], self.content.warpmeta['source-valid'], self.content.warpmeta['source-fname']) = iou.read_geom(fileobj, niftiheaderext=True)
                (self.content.warpmeta['target-geom'], self.content.warpmeta['target-valid'], self.content.warpmeta['target-fname']) = iou.read_geom(fileobj, niftiheaderext=True)
            # gcamorph meta (warp: int int float) (TAG_GCAMORPH_META = 13)
            elif (tag == FSNifti1Extension.Tags.gcamorph_meta):
                if (not self.content.warpmeta):
                    self.content.warpmeta = {}

                self.content.warpmeta['format']  = iou.read_bytes(fileobj, dtype='>i4')
                self.content.warpmeta['spacing'] = iou.read_bytes(fileobj, dtype='>i4')
                self.content.warpmeta['exp_k']   = iou.read_bytes(fileobj, dtype='>f4')

            # scan_parameters (TAG_SCAN_PARAMETERS = 45)
            elif (tag == FSNifti1Extension.Tags.scan_parameters):
                self.content.scan_parameters = {}
                self.content.scan_parameters['te'] = iou.read_bytes(fileobj, dtype='>f4')
                self.content.scan_parameters['ti'] = iou.read_bytes(fileobj, dtype='>f4')
                self.content.scan_parameters['flip_angle'] = iou.read_bytes(fileobj, dtype='>f8') # ??? double 8 bytes
                self.content.scan_parameters['field_strength'] = iou.read_bytes(fileobj, dtype='>f4')

                len_pedir = length - 20
                self.content.scan_parameters['pedir'] = fileobj.read(len_pedir).decode('utf-8').rstrip('\x00')

            # skip everything else
            else:
                fileobj.read(length)

            # check if we reach the end
            tagdatalen -= (len_tagheader + length)
            if (tagdatalen < len_tagheader):
                print(f'[DEBUG] FSNifti1Extension.read(): remaining taglen = {tagdatalen:6d}')
                break;

        return self.content


    def write(self, fileobj, content, countbytesonly=False):
        """
        Write Freesurfer Nifti1 header extension data saved to the file-like object.

        Parameters
        ----------
        fileobj : file-like object
            opened file-like object
        content : FSNifti1Extension.Content
            Data to output or count bytes
        countbytesonly : boolean
            if True, count total bytes to output w/o writing to fileobj

        Returns
        -------
        num_bytes : long
            total bytes output or counted
        """

        # freesurfer nifti header extension data is in big endian
        # the first 4 bytes are as following:
        #   endian ">" (1 byte), intent (unsigned short, 2 bytes), version (1 byte)
        if (not countbytesonly):
            fileobj.write(content.endian.encode('utf-8'))
            iou.write_int(fileobj, content.intent,  size=2, byteorder='big')
            iou.write_int(fileobj, content.version, size=1, byteorder='big')

        num_bytes = 4
        print(f'[DEBUG] FSNifti1Extension.write():              dlen = {num_bytes:6d}')

        # tag data
        addtaglength = 12
        if (content.intent == FramedArrayIntents.warpmap):
            # gcamorph src & trg geoms (warp) (TAG_GCAMORPH_GEOM = 10)
            source_fname = content.warpmeta.get('source-fname', '')
            target_fname = content.warpmeta.get('target-fname', '')

            tag = FSNifti1Extension.Tags.gcamorph_geom
            length = FSNifti1Extension.getlen_gcamorph_geom(source_fname, target_fname)
            num_bytes += length + addtaglength
            print(f'[DEBUG] FSNifti1Extension.write(): +{length:5d}, +{addtaglength:d}, dlen = {num_bytes:6d}, TAG = {tag:2d}')
            if (not countbytesonly):
                FSNifti1Extension.write_tag(fileobj, tag, length)
                iou.write_geom(fileobj,
                           geom=content.warpmeta['source-geom'],
                           valid=content.warpmeta.get('source-valid', True),
                           fname=source_fname,
                           niftiheaderext=True)
                iou.write_geom(fileobj,
                           geom=content.warpmeta['target-geom'],
                           valid=content.warpmeta.get('target-valid', True),
                           fname=target_fname,
                           niftiheaderext=True)

            # gcamorph meta (warp: int int float) (TAG_GCAMORPH_META = 13)
            tag = FSNifti1Extension.Tags.gcamorph_meta
            length = 12
            num_bytes += length + addtaglength
            print(f'[DEBUG] FSNifti1Extension.write(): +{length:5d}, +{addtaglength:d}, dlen = {num_bytes:6d}, TAG = {tag:2d}')
            if (not countbytesonly):
                FSNifti1Extension.write_tag(fileobj, tag, length)
                iou.write_bytes(fileobj, content.warpmeta['format'], dtype='>i4')
                iou.write_bytes(fileobj, content.warpmeta.get('spacing', 1), dtype='>i4')
                iou.write_bytes(fileobj, content.warpmeta.get('exp_k', 0.0), dtype='>f4')

            # write TAG_END_NIIHDREXTENSION at the end of extension data to avoid the data to be truncated:
            #   TAG_END_NIIHDREXTENSION (-1)  data-length (1) '*'
            # this needs to be the last tag.
            tag = FSNifti1Extension.Tags.end_data
            length = 1  # extra char '*'
            num_bytes += length + addtaglength
            print(f'[DEBUG] FSNifti1Extension.write(): +{length:5d}, +{addtaglength:d}, dlen = {num_bytes:6d}, TAG = {tag:2d}')
            if (not countbytesonly):
                FSNifti1Extension.write_tag(fileobj, tag, length)
                extrachar = '*'
                fileobj.write(extrachar.encode('utf-8'))

            return num_bytes


        # lookup table (TAG_OLD_COLORTABLE = 1)
        if (content.labels):
            tag = FSNifti1Extension.Tags.old_colortable
            length = FSNifti1Extension.getlen_labels(content.labels)
            num_bytes += length + addtaglength
            print(f'[DEBUG] FSNifti1Extension.write(): +{length:5d}, +{addtaglength:d}, dlen = {num_bytes:6d}, TAG = {tag:2d}')
            if (not countbytesonly):
                FSNifti1Extension.write_tag(fileobj, tag, length)
                fsio.write_binary_lookup_table(fileobj, content.labels)

        # history (TAG_CMDLINE = 3)
        if (content.history):
            for hist in content.history:
                tag = FSNifti1Extension.Tags.history
                length = len(hist)
                num_bytes += length + addtaglength
                print(f'[DEBUG] FSNifti1Extension.write(): +{length:5d}, +{addtaglength:d}, dlen = {num_bytes:6d}, TAG = {tag:2d}')
                if (not countbytesonly):
                    FSNifti1Extension.write_tag(fileobj, tag, length)
                    fileobj.write(hist.encode('utf-8'))

        # dof (TAG_DOF = 7)
        tag = FSNifti1Extension.Tags.dof
        length = 4
        num_bytes += length + addtaglength
        print(f'[DEBUG] FSNifti1Extension.write(): +{length:5d}, +{addtaglength:d}, dlen = {num_bytes:6d}, TAG = {tag:2d}')
        if (not countbytesonly):
            FSNifti1Extension.write_tag(fileobj, tag, length)
            iou.write_int(fileobj, content.dof, size=4)

        # ras_xform (TAG_RAS_XFORM = 8)
        if (content.ras_xform):
            tag = FSNifti1Extension.Tags.ras_xform
            length = 48
            num_bytes += length + addtaglength
            print(f'[DEBUG] FSNifti1Extension.write(): +{length:5d}, +{addtaglength:d}, dlen = {num_bytes:6d}, TAG = {tag:2d}')
            if (not countbytesonly):
                FSNifti1Extension.write_tag(fileobj, tag, length)
                iou.write_bytes(fileobj, np.ravel(content.ras_xform['rotation'], order='F'), '>f4')
                iou.write_bytes(fileobj, content.ras_xform['center'], '>f4')

        # scan_parameters (TAG_SCAN_PARAMETERS = 45)
        if (content.scan_parameters):
            tag = FSNifti1Extension.Tags.scan_parameters
            length = 20 + len(content.scan_parameters['pedir'])
            num_bytes += length + addtaglength
            print(f'[DEBUG] FSNifti1Extension.write(): +{length:5d}, +{addtaglength:d}, dlen = {num_bytes:6d}, TAG = {tag:2d}')
            if (not countbytesonly):
                FSNifti1Extension.write_tag(fileobj, tag, length)
                iou.write_bytes(fileobj, content.scan_parameters['te'], '>f4')
                iou.write_bytes(fileobj, content.scan_parameters['ti'], '>f4')
                iou.write_bytes(fileobj, content.scan_parameters['flip_angle'], '>f8') # ??? double 8 bytes
                iou.write_bytes(fileobj, content.scan_parameters['field_strength'], '>f4')
                fileobj.write(content.scan_parameters['pedir'].encode('utf-8'))

        # end_data (TAG_END_NIIHDREXTENSION = -1)
        """
        write TAG_END_NIIHDREXTENSION at the end of extension data to avoid the data to be truncated:
          TAG_END_NIIHDREXTENSION (-1)  data-length (1) '*'
        this needs to be the last tag.

        If the extension data has trailing null characters or zeros at the end,
        nibabel.nifti1.Nifti1Extension.get_content() will truncate the data.
        See https://github.com/nipy/nibabel/blob/master/nibabel/nifti1.py#L629C1-L630C1,
        line 629:  'evalue = evalue.rstrip(b'\x00')'
        """
        tag = FSNifti1Extension.Tags.end_data
        length = 1  # extra char '*'
        num_bytes += length + addtaglength
        print(f'[DEBUG] FSNifti1Extension.write(): +{length:5d}, +{addtaglength:d}, dlen = {num_bytes:6d}, TAG = {tag:2d}')
        if (not countbytesonly):
            FSNifti1Extension.write_tag(fileobj, tag, length)
            extrachar = '*'
            fileobj.write(extrachar.encode('utf-8'))

        return num_bytes


    @staticmethod
    def read_tag(fileobj):
        """
        Reads the next FreeSurfer tag ID and associated data length.

        Parameters
        ----------
        fileobj : file-like object
            opened file-like object

        Returns
        -------
        tag : FSNifti1Extension.Tags
            Tag ID
        length : long
            data length of tagged data
        """

        tag = iou.read_int(fileobj)
        length = iou.read_int(fileobj, size=8)

        return (tag, length)


    @staticmethod
    def write_tag(fileobj, tag, length):
        """
        Write tag ID and associated data-length

        Parameters
        ----------
        fileobj : file-like object
            opened file-like object
        tag     : FSNifti1Extension.Tags
            Tag ID
        length  : long
            data length
        """

        iou.write_int(fileobj, tag)
        iou.write_int(fileobj, length, size=8)


    @staticmethod
    def getlen_labels(labels):
        """
        Calculate total bytes that will be written for the labels

        Parameters
        ----------
        labels : LabelLookup
            Labels used for calculation

        Returns
        -------
        num_bytes : int
            total bytes that will be written for the input labels
        """

        num_bytes = 12      # version, nentries, len(fname)
        # io.fsio.write_binary_lookup_table() doesn't write fname, len(fname)=0
        num_bytes += 4      # num_entries
        for index, element in labels.items():
            num_bytes += 8  # structure id, len(structure-name)+1
            num_bytes += len(element.name) + 1  # structure name
            num_bytes += 16  # ri, gi, bi, t-ai

        return num_bytes


    @staticmethod
    def getlen_gcamorph_geom(fname_source, fname_target):
        """
        Calculate total bytes that will be written for the labels.

        Parameters
        ----------
        fname_source : string
            File name associated with the source geometry
        fname_target : string
            File name associated with the target geometry

        Returns
        -------
        num_bytes : int
            total bytes that will be written for the source and target geometry
        """

        # See freesurfer/utils/fstagsio.cpp::getlen_gcamorph_geom().
        num_bytes = 2 * 80
        num_bytes += len(fname_source)
        num_bytes += len(fname_target)

        return num_bytes


    @property
    def content(self):
        return self._content
    @content.setter
    def content(self, content):
        self._content = content


    class Tags:
        """
        Freesurfer Nifti1 header extension data is in big endian and has the following format:
          endian ">" (1 byte), intent (2 bytes), version (1 byte)
          tagid-1 data-length-1 tag-data-1
          tagid-2 data-length-2 tag-data-2
          ...

        This class defines the tags recognized in surfa.
        It is a subset of tag IDs defined in freesurfer/include/tags.h
        """

        old_colortable  = 1    # TAG_OLD_COLORTABLE
        history         = 3    # TAG_CMDLINE
        dof             = 7    # TAG_DOF
        ras_xform       = 8    # TAG_RAS_XFORM
        gcamorph_geom   = 10   # TAG_GCAMORPH_GEOM
        gcamorph_meta   = 13   # TAG_GCAMORPH_META
        scan_parameters = 45   # TAG_SCAN_PARAMETERS
        end_data        = -1   # TAG_END_NIIHDREXTENSION


    class Content:
        """
        Data class represents Freesurfer Nifti1 header extension data.

        Class variables:
          _endian:          big endian = '>', or little endian = '<'
          _intent:          FramedArrayIntents
          _version:         int

          _dof:             int
          _scan_parameters: dict {
                                   'te'             : float,
                                   'ti'             : float,
                                   'flip_angle'     : double,
                                   'field_strength' : float,
                                   'pedir'          : string
                                 }
          _ras_xform:       dict {
                                   'rotation' : array(3, 3, float)
                                   'center'   : array(1, 3, float)
                                 }
          _warpmeta:        dict {
                                   'format'       : Warp.Format
                                   'spacing'      : int
                                   'exp_k'        : float
                                   'source-valid' : int
                                   'source-fname' : string
                                   'source-geom'  : ImageGeometry
                                   'target-valid' : int
                                   'target-fname' : string
                                   'target-geom'  : ImageGeometry
                                 }
          _history:         list[string]
          _labels:          LabelLookup
        """

        def __init__(self, framedimage=None):
            """
            FSNifti1Extension.Content Constructor
            """

            self._endian = '>'
            self._intent = FramedArrayIntents.mri
            self._version = 1

            self._dof = 1
            self._scan_parameters = None
            self._ras_xform = None
            self._warpmeta = None
            self._history = None
            self._labels = None

            if (framedimage):
                self._from_framedimage(framedimage)


        def update_framedimage(self, framedimage):
            """
            Update input FramedImage metadata

            Parameters
            ----------
            framedimage : FramedImage
                input FramedImage to update
            """

            # update input framedimage metadata
            framedimage.metadata['intent'] = self.intent

            if (self.intent == FramedArrayIntents.warpmap):
                # gcamorph src & trg geoms (mgz warp)
                framedimage.source = self.warpmeta['source-geom']
                framedimage.metadata['source-valid'] = self.warpmeta['source-valid']
                framedimage.metadata['source-fname'] = self.warpmeta['source-fname']

                framedimage.target = self.warpmeta['target-geom']
                framedimage.metadata['target-valid'] = self.warpmeta['target-valid']
                framedimage.metadata['target-fname'] = self.warpmeta['target-fname']

                # gcamorph meta (mgz warp: int int float)
                framedimage.format = self.warpmeta['format']
                framedimage.metadata['spacing'] = self.warpmeta['spacing']
                framedimage.metadata['exp_k'] = self.warpmeta['exp_k']

                return

            # update image-specific information
            if (self.ras_xform):
                framedimage.geom.update(
                    rotation=self.ras_xform['rotation'],
                    center=self.ras_xform['center']
                                       )

            if (self.scan_parameters):
                framedimage.metadata['phase-encode-direction'] = self.scan_parameters['pedir']
                framedimage.metadata['field-strength'] = self.scan_parameters['field_strength']

                scan_params = {}
                scan_params['fa'] = self.scan_parameters['flip_angle']
                scan_params['te'] = self.scan_parameters['te']
                scan_params['ti'] = self.scan_parameters['ti']
                framedimage.metadata.update(scan_params)

            if (self.history):
                framedimage.metadata['history'] = self.history

            if (self.labels):
                framedimage.labels = self.labels


        def _from_framedimage(self, image):
            """
            Create FSNifti1Extension.Content object from FramedImage instance.

            Parameters
            ----------
            image : FramedImage
                Input Image.

            """
            self.endian = '>'
            self.version = 1
            self.intent = image.metadata.get('intent', FramedArrayIntents.mri)
            self.dof = 1
            if isinstance(self.intent, np.int_):
                self.intent = self.intent.item()  # convert numpy int to python int

            if self.intent == FramedArrayIntents.warpmap:
                if not self.warpmeta:
                    self.warpmeta = {}

                # gcamorph src & trg geoms (mgz warp)
                self.warpmeta['source-geom'] = image.source
                self.warpmeta['source-valid'] = image.metadata.get('source-valid', True)
                self.warpmeta['source-fname'] = image.metadata.get('source-fname', '')

                self.warpmeta['target-geom'] = image.target
                self.warpmeta['target-valid'] = image.metadata.get('target-valid', True)
                self.warpmeta['target-fname'] = image.metadata.get('target-fname', '')

                # gcamorph meta (mgz warp: int int float)
                self.warpmeta['format'] = image.format
                self.warpmeta['spacing'] = image.metadata.get('spacing', 1)
                self.warpmeta['exp_k'] = image.metadata.get('exp_k', 0.0)

                return

            # update ras_xform
            self.ras_xform = dict(
                rotation = image.geom.rotation,
                center = image.geom.center,
            )

            # update scan_parameters
            self.scan_parameters = dict(
                pedir = image.metadata.get('phase-encode-direction', 'UNKNOWN'),
                field_strength = image.metadata.get('field-strength'),
                flip_angle = image.metadata.get('fa', 0),
                te = image.metadata.get('te', 0),
                ti = image.metadata.get('ti', 0),
            )

            if image.metadata.get('history'):
                self.history = image.metadata['history']

            if image.labels:
                 self.labels = image.labels


        @property
        def endian(self):
            return self._endian

        @endian.setter
        def endian(self, endian):
            self._endian = endian

        @property
        def intent(self):
            return self._intent

        @intent.setter
        def intent(self, intent):
            self._intent = intent

        @property
        def version(self):
            return self._version

        @version.setter
        def version(self, version):
            self._version = version

        @property
        def dof(self):
            return self._dof

        @dof.setter
        def dof(self, dof):
            self._dof = dof

        @property
        def scan_parameters(self):
            return self._scan_parameters

        @scan_parameters.setter
        def scan_parameters(self, scan_parameters):
            self._scan_parameters = scan_parameters

        @property
        def ras_xform(self):
            return self._ras_xform

        @ras_xform.setter
        def ras_xform(self, ras_xform):
            self._ras_xform = ras_xform

        @property
        def warpmeta(self):
            return self._warpmeta

        @warpmeta.setter
        def warpmeta(self, warpmeta):
            self._warpmeta = warpmeta

        @property
        def history(self):
            return self._history

        @history.setter
        def history(self, history):
            self._history = history

        @property
        def labels(self):
            return self._labels

        @labels.setter
        def labels(self, labels):
            self._labels = labels
