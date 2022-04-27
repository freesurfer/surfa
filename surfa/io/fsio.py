from . import utils as iou


# FreeSurfer tag ID lookup
class tags:
    old_colortable = 1
    old_real_ras = 2
    history = 3
    real_ras = 4
    colortable = 5
    gcamorph_geom = 10
    gcamorph_type = 11
    gcamorph_labels = 12
    old_surf_geom = 20
    surf_geom = 21
    old_xform = 30
    xform = 31
    group_avg_area = 32
    auto_align = 33
    scalar_double = 40
    pedir = 41
    mri_frame = 42
    fieldstrength = 43


# these are FreeSurfer tags that have a
# buffer with hardcoded length
lengthless_tags = [
    tags.old_surf_geom,
    tags.old_real_ras,
    tags.old_colortable,
]


def read_tag(file):
    """
    Reads the next FreeSurfer tag ID and associated byte-length (if any)
    from a file buffer.

    Parameters
    ----------
    file : BufferedReader
        Opened file buffer to read tags from.

    Returns
    -------
    tag : int
        Tag ID read from file. Tag is None if end-of-file is reached.
    length : int
        Byte-length of tagged data.
    """
    tag = iou.read_int(file)
    if tag == 0:
        return (None, None)
    if tag == tags.old_xform:
        # backwards compatibility for transform, which writes 32-bit length
        length = iou.read_int(file)
    elif tag in lengthless_tags:
        # these tags have static lengths
        length = 0
    else:
        length = iou.read_int(file, size=8)
    return (tag, length)


def write_tag(file, tag, length=None):
    """
    Writes a FreeSurfer tag ID and associated byte-length (if any) to a file buffer.

    Parameters
    ----------
    file : BufferedWriter
        Opened file buffer to write tags to.
    tag : int
        Tag ID to write.
    length : int
        Byte-length of tagged data. Optional depending on tag type.
    """
    iou.write_int(file, tag)
    if tag == tags.old_xform:
        # backwards compatibility for transform, which writes 32-bit length
        iou.write_int(file, length)
    elif tag in lengthless_tags:
        # these tags have static lengths
        pass
    elif length is not None:
        iou.write_int(file, length, size=8)


def read_binary_lookup_table(file):
    """
    TODOC
    """
    version = iou.read_bytes(file, '>i4')
    max_id = iou.read_bytes(file, '>i4')
    file_name_size = iou.read_bytes(file, '>i4')
    file.read(file_name_size).decode('utf-8')
    
    total = iou.read_bytes(file, '>i4')
    if total < 1:
        return None
    
    lut = LabelMap()
    for n in range(total):
        index = iou.read_bytes(file, '>i4')
        name_size = iou.read_bytes(file, '>i4')
        name = file.read(name_size).decode('utf-8')
        color = iou.read_bytes(file, '(4,)>i4')
        lut.add(index, name, color)
    return lut


def write_binary_lookup_table(file, lut):
    """
    TODOC
    """
    iou.write_bytes(file, -2, '>i4')
    iou.write_bytes(file, max(lut) + 1, '>i4')
    iou.write_bytes(file, 0, '>i4')
    iou.write_bytes(file, len(lut), '>i4')
    for index, element in lut.items():
        iou.write_bytes(file, index, '>i4')
        iou.write_bytes(file, len(element.name), '>i4')
        file.write(element.name.encode('utf-8'))
        iou.write_bytes(file, element.color, '>i4')
