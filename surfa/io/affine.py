import numpy as np

from surfa.io import fsio
from surfa.io import protocol
from surfa.io import check_file_readability
from surfa.transform import Affine


def load_affine(filename, fmt=None):
    """
    Load an `Affine` from file.

    Parameters
    ----------
    filename : str
        File path to read.
    fmt : str, optional
        Forced file format. If None (default), file format is extrapolated
        from extension.

    Returns
    -------
    Affine
        Loaded affine. 
    """
    check_file_readability(filename)

    if fmt is None:
        iop = protocol.find_protocol_by_extension(affine_io_protocols, filename)
        if iop is None:
            raise ValueError(f'cannot determine file format from extension for {filename}')
    else:
        iop = protocol.find_protocol_by_name(affine_io_protocols, fmt)
        if iop is None:
            raise ValueError(f'unknown file format {fmt}')

    return iop().load(filename)


def save_affine(aff, filename, fmt=None):
    """
    Save a `Affine` object to file.

    Parameters
    ----------
    aff : Affine
        Object to write.
    filename: str
        Destination file path.
    fmt : str
        Forced file format. If None (default), file format is extrapolated
        from extension.
    """
    if fmt is None:
        iop = protocol.find_protocol_by_extension(affine_io_protocols, filename)
        if iop is None:
            raise ValueError(f'cannot determine file format from extension for {filename}')
    else:
        iop = protocol.find_protocol_by_name(affine_io_protocols, fmt)
        if iop is None:
            raise ValueError(f'unknown file format {fmt}')
        filename = iop.enforce_extension(filename)

    iop().save(aff, filename)


class LinearTransformArrayIO(protocol.IOProtocol):
    """
    Affine IO protocol for LTA files.
    """

    name = 'lta'
    extensions = ('.lta',)

    def load(self, filename):
        """
        Read affine from an LTA file.

        Parameters
        ----------
        filename : str
            File path to read.

        Returns
        -------
        Affine
            Affine object loaded from file.
        """
        with open(filename, 'r') as file:
            lines = [line.rstrip() for line in file]
            lines = [line for line in lines if line and not line.startswith('#')]

        # determine the coordinate space
        space_id = int(lines[0].split()[2])
        space = {0: 'vox',
                 1: 'world',
                 3: 'surf'}.get(space_id, None)
        if space is None:
            raise ValueError(f'unknown affine LTA type ID: {space_id}')

        # read in the actual matrix data
        matrix = np.asarray([line.split() for line in lines[5:9]], dtype=np.float64)

        # read in source and target geometry (if valid)
        source = fsio.image_geometry_from_string('\n'.join(lines[10:18]))
        target = fsio.image_geometry_from_string('\n'.join(lines[19:27]))
        if source is None and target is None:
            space = None

        return Affine(matrix, source=source, target=target, space=space)

    def save(self, aff, filename):
        """
        Write affine to an LTA file.

        Parameters
        ----------
        aff : Affine
            Array to save.
        filename : str
            Target file path.
        """
        with open(filename, 'w') as file:

            # determine LTA coordinate space
            if aff.space is None or aff.space == 'vox':
                file.write('type      = 0 # LINEAR_VOX_TO_VOX\n')
            elif aff.space == 'world':
                file.write('type      = 1 # LINEAR_RAS_TO_RAS\n')
            elif aff.space == 'surf':
                file.write('type      = 3 # LINEAR_SURF_TO_SURF\n')
            else:
                raise NotImplementedError(f'cannot write coordinate space {aff.space} to LTA - this is a '
                                           'bug, not a user error')

            # this is all useless legacy information
            file.write('nxforms   = 1\n')
            file.write('mean      = 0.0000 0.0000 0.0000\n')
            file.write('sigma     = 1.0000\n')
            file.write('1 4 4\n')

            # write the actual matrix data
            file.write('%.15e %.15e %.15e %.15e\n' % tuple(aff.matrix[0]))
            file.write('%.15e %.15e %.15e %.15e\n' % tuple(aff.matrix[1]))
            file.write('%.15e %.15e %.15e %.15e\n' % tuple(aff.matrix[2]))
            file.write('%.15e %.15e %.15e %.15e\n' % tuple(aff.matrix[3]))

            # write source geometry (if any)
            file.write('src volume info\n')
            file.write(fsio.image_geometry_to_string(aff.source))

            # write target geometry (if any)
            file.write('dst volume info\n')
            file.write(fsio.image_geometry_to_string(aff.target))
            
            
class MNITransformIO(protocol.IOProtocol):
    """
    Affine IO protocol for MNI .xfm transform files
    (\"MNI Transform File\" as used by FreeSurfer's ltaMNIwrite/ltaMNIread).
    """

    name = "xfm"
    extensions = (".xfm",)

    def load(self, filename):
        """
        Read affine from an MNI .xfm file.

        This is a RAS-to-RAS (world-to-world) 3D transform.
        Source/target geometries are not stored in the file,
        so the returned Affine has source/target = None and space = 'world'.
        """
        with open(filename, "r") as f:
            lines = [line.strip() for line in f if line.strip()]

        if not lines[0].lower().startswith("mni transform file"):
            raise ValueError(f"{filename} does not look like an MNI .xfm file")

        # Find the "Linear_Transform" block
        lt_idx = None
        for i, line in enumerate(lines):
            if line.lower().startswith("linear_transform"):
                lt_idx = i + 1
                break

        if lt_idx is None:
            raise ValueError(
                f"could not find 'Linear_Transform' block in {filename}")

        rows = []
        for r in range(3):
            line = lines[lt_idx + r]
            # strip trailing ';' if present
            line = line.replace(";", "")
            parts = line.split()
            if len(parts) < 4:
                raise ValueError(
                    f"expected 4 numbers on row {r+1} "
                    f"of Linear_Transform in {filename}, "
                    f"got: {line!r}"
                )
            rows.append([float(x) for x in parts[:4]])

        mat = np.eye(4, dtype=np.float64)
        mat[:3, :4] = np.asarray(rows, dtype=np.float64)

        # By definition this is a world/RAS-to-world/RAS transform
        return Affine(mat, space="world")

    def save(self, aff, filename):
        """
        Write affine to an MNI .xfm file.

        If aff.space is 'world' or 'surf', the matrix is written as-is
        (LINEAR_RAS_TO_RAS case).

        If aff.space is None or 'vox', the matrix is interpreted as
        voxel-to-voxel (LINEAR_VOX_TO_VOX) and converted to a RAS-to-RAS
        transform using the source/target geometries, exactly as in
        ltaMNIwrite() in transform.cpp.
        """
        if aff.ndim != 3:
            raise NotImplementedError("MNI .xfm only supports 3D transforms")

        # Interpret 'space' like the LTA writer does
        space = aff.space or "vox"

        # Decide which matrix to write: either directly m_L (RAS2RAS),
        # or converted from VOX2VOX into RAS2RAS.
        if space in ("world", "surf"):
            ras_to_ras = np.asarray(aff.matrix, dtype=np.float64)
        elif space == "vox":
            if aff.source is None or aff.target is None:
                raise ValueError(
                    "cannot write voxel-space affine to MNI .xfm without "
                    "both source and target geometries"
                )

            # C code:
            #   voxFromRAS  = extract_r_to_i(&lt->src);        // world->vox
            #   tmp         = m_L * voxFromRAS;
            #   rasFromVoxel= extract_i_to_r(&lt->dst);       // vox->world
            #   rasToRAS    = rasFromVoxel * tmp;
            #
            # Here:
            #   src.world2vox.matrix ~ extract_r_to_i(src)
            #   dst.vox2world.matrix ~ extract_i_to_r(dst)
            m_L = np.asarray(aff.matrix, dtype=np.float64)
            vox_from_ras = np.asarray(
                aff.source.world2vox.matrix, dtype=np.float64)
            ras_from_vox = np.asarray(
                aff.target.vox2world.matrix, dtype=np.float64)

            tmp = m_L @ vox_from_ras
            ras_to_ras = ras_from_vox @ tmp
        else:
            raise NotImplementedError(
                f"cannot write affine with space={aff.space!r} to MNI .xfm"
            )

        # The C code only writes the top 3 rows.
        # Use filenames if they exist on geometries; otherwise leave blank.
        src_name = getattr(getattr(aff, "source", None), "filename", "") or ""
        dst_name = getattr(getattr(aff, "target", None), "filename", "") or ""

        with open(filename, "w") as fp:
            fp.write("MNI Transform File\n")
            fp.write(
                f"%Generated by surfa.Affine.save "
                f"src {src_name} dst {dst_name}\n"
            )
            fp.write("\n")
            fp.write("Transform_Type = Linear;\n")
            fp.write("Linear_Transform =\n")

            for row in range(3):
                vals = ras_to_ras[row, :4]
                line = " ".join(f"{v:13.8f}" for v in vals)
                if row == 2:
                    line += " ;"
                fp.write(line + "\n")


# enabled affine IO protocol classes
affine_io_protocols = [
    LinearTransformArrayIO,
    MNITransformIO,
]
