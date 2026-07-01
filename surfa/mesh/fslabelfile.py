import sys
import numpy as np

from surfa.transform import Space


# this class implements the following methods:
# 1. read(): read list of coords in Freesurfer .label format
# 2. write(): write list of coords in Freesurfer .label format
# 3. transform(): transform coordinates between 'world', 'voxel', and 'surface' spaces
#                 if inverse deformation field is provide, apply the defomration field
#                 the deformation field is expected to be in abs-crs data representation
class FSLabelFile():
    
    def __init__(self, geom=None, coords=None, surface_vertices=None, coordspace=Space.FS_COORDS_UNKNOWN):
        # [N, 3] array containing the coordinates
        self._coords = coords
        # [N] 1-D array containing the surface vertex number
        self._surface_vertices = surface_vertices
        # coordinates space
        self._coordspace = coordspace
        # number of coords
        self._num_points = 0
        # volume geometry
        self._geom = geom

        if (self._surface_vertices is None and self._coords is not None):
            self._surface_vertices = np.zeros(self._coords.shape[0], dtype=int)


    # read list of coords in Freesurfer .label format
    # For Freesurfer .label format,
    # see https://surfer.nmr.mgh.harvard.edu/fswiki/LabelsClutsAnnotationFiles#Label_file
    def read(self, infile):
        fp = open(infile, "r")

        # read the comment line, locate coordinate space
        line = fp.readline().strip()
        index = line.find("vox2ras=")  # find the index where 'vox2ras=' starts
        if (index != -1):
            loc = index + len("vox2ras=")
            space = line[loc:]   # skip pass 'vox2ras='
            if (space == 'voxel'):
                self._coordspace = Space.FS_COORDS_VOXEL
            elif (space == 'scanner'):
                self._coordspace = Space.FS_COORDS_SCANNER_RAS
            elif (space == 'TkReg'):
                self._coordspace = Space.FS_COORDS_TKREG_RAS
            else:
                raise ValueError(f"Invalid `vox2ras`: {space}. It can either 'voxel', 'scanner', or 'TkReg'")

        # read in the count of coords
        line = fp.readline().strip()
        self._num_points = int(line)

        # read all the coords
        coords, surface_vertices = [], []
        line = fp.readline().strip()
        while (line):
            # .split() with no arguments automatically handles any consecutive whitespace (multiple spaces, tabs, or newlines)
            # as a single delimiter. It also automatically ignores empty elements caused by leading or trailing spaces.
            v, x, y, z, stat = line.split()
            coords.append((float(x), float(y), float(z)))
            surface_vertices.append(int(v))

            # next line
            line = fp.readline().strip()
        
        self._coords = np.array(coords)                      # [N, 3]
        self._surface_vertices = np.array(surface_vertices)  # [N]

        fp.close()


    # write list of coords in Freesurfer .label format
    def write(self, outfile=None):
        fp = sys.stdout
        if (outfile is not None):
            fp = open(outfile, "w")

        # write the comment line
        if (self._coordspace == Space.FS_COORDS_TKREG_RAS):
            space = "TkReg"
        elif (self._coordspace == Space.FS_COORDS_SCANNER_RAS):
            space = "scanner"
        elif (self._coordspace == Space.FS_COORDS_VOXEL):
            space = "voxel"
        fp.write(f"#!ascii label,  vox2ras={space}\n")

        # write number of coodinates
        num_points = self._coords.shape[0]
        fp.write(f"{num_points}\n")

        # write the coordinates
        for v in range(num_points):
            fp.write(f"{self._surface_vertices[v]} {self._coords[v, 0]:.3f} {self._coords[v, 1]:.3f} {self._coords[v, 2]:.3f} 0.0000000000\n")

        # can't close stdout
        if (outfile is not None):
            fp.close()


    # transform the coordinates into a different space specified as 'coordspace'
    # apply the warp field first if 'warp' is specified
    def transform(self, warp=None, coordspace=Space.FS_COORDS_TKREG_RAS, geom=None):
        if (warp is not None):
            self.apply_warp(warp)
        self.change_space(coordspace=coordspace, geom=geom)
        

    # apply warp field to the coordinates
    # 'warp' is the inverse (backward) warp field mapping from target (fixed) to source (moving)
    def apply_warp(self, warp):
        # the coordinates needs to be FS_COORDS_VOXEL space assuming the warp in abs-crs
        if (self._coordspace != Space.FS_COORDS_VOXEL):
            self.change_space(coordspace=Space.FS_COORDS_VOXEL)

        from surfa.transform import Warp
        self._coords = Warp.warp_pointsets(warp, self._coords)


    # change coordinates space
    def change_space(self, coordspace=Space.FS_COORDS_TKREG_RAS, geom=None):
        if (self._coordspace == coordspace):
            return
        
        transform_geom = geom if (geom is not None) else self._geom
        space_from = Space.CODE_TO_LETTER[self._coordspace]
        space_to = Space.CODE_TO_LETTER[coordspace]
        affine = transform_geom.affine(space_from, space_to)
        self._coords = affine[:3, :3] @ self._coords.T + affine[:3, 3:]
        self._coords = self._coords.T   # [ N, 3]
        self._coordspace = coordspace


    @property
    def coordspace(self):
        return self._coordspace
    
    @property
    def geom(self):
        return self._geom   

    @property
    def coords(self):
        return self._coords

    @property
    def surface_vertices(self):
        return self._surface_vertices

