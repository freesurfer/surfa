import os

from surfa.system import fatal
from surfa.core.labels import LabelRecoder
from surfa.core.labels import LabelLookup
from surfa.io.labels import load_label_lookup


def home(require=True):
    """
    The freesurfer installation directory as defined by the FREESURFER_HOME environment variable.

    Parameters
    ----------
    require : bool
        If enabled, throws an error when freesurfer home is not set.

    Returns
    -------
    fshome : str
    """
    fshome = os.environ.get('FREESURFER_HOME')
    if require and fshome is None:
        fatal('FREESURFER_HOME has not been set in the environment')
    return fshome


def subjsdir(path=None):
    """
    The freesurfer subjects directory as defined by the SUBJECTS_DIR environment variable.

    Parameters
    ----------
    path : str
        If provided, sets the new SUBJECTS_DIR.

    Returns
    -------
    dir : str
    """
    if path is not None:
        os.environ['SUBJECTS_DIR'] = path
    sdir = os.environ.get('SUBJECTS_DIR')
    if sdir is None:
        fatal('FREESURFER_HOME has not been set in the environment')
    return sdir


def getfile(subpath):
    """
    Retrieve the complete path of a subfile in the freesurfer home directory.

    Parameters
    ----------
    subpath : str
        File path to append to the extracted freesurfer home.

    Returns
    -------
    path : str
    """
    return os.path.join(home(), subpath)


def labels():
    """
    Standard label lookup for all brain regions.

    Returns
    -------
    labels : LabelLookup
    """
    return load_label_lookup(getfile('FreeSurferColorLUT.txt'))


def destrieux():
    """
    Label lookup for Destrieux cortical atlas parcellations.

    Returns
    -------
    labels : LabelLookup
    """
    labels = LabelLookup()
    labels[0]  = ('Unknown',                   [  0,   0,   0])
    labels[1]  = ('G_and_S_frontomargin',      [ 23, 220,  60])
    labels[2]  = ('G_and_S_occipital_inf',     [ 23,  60, 180])
    labels[3]  = ('G_and_S_paracentral',       [ 63, 100,  60])
    labels[4]  = ('G_and_S_subcentral',        [ 63,  20, 220])
    labels[5]  = ('G_and_S_transv_frontopol',  [ 13,   0, 250])
    labels[6]  = ('G_and_S_cingul-Ant',        [ 26,  60,   0])
    labels[7]  = ('G_and_S_cingul-Mid-Ant',    [ 26,  60,  75])
    labels[8]  = ('G_and_S_cingul-Mid-Post',   [ 26,  60, 150])
    labels[9]  = ('G_cingul-Post-dorsal',      [ 25,  60, 250])
    labels[10] = ('G_cingul-Post-ventral',     [ 60,  25,  25])
    labels[11] = ('G_cuneus',                  [180,  20,  20])
    labels[12] = ('G_front_inf-Opercular',     [220,  20, 100])
    labels[13] = ('G_front_inf-Orbital',       [140,  60,  60])
    labels[14] = ('G_front_inf-Triangul',      [180, 220, 140])
    labels[15] = ('G_front_middle',            [140, 100, 180])
    labels[16] = ('G_front_sup',               [180,  20, 140])
    labels[17] = ('G_Ins_lg_and_S_cent_ins',   [ 23,  10,  10])
    labels[18] = ('G_insular_short',           [225, 140, 140])
    labels[19] = ('G_occipital_middle',        [180,  60, 180])
    labels[20] = ('G_occipital_sup',           [ 20, 220,  60])
    labels[21] = ('G_oc-temp_lat-fusifor',     [ 60,  20, 140])
    labels[22] = ('G_oc-temp_med-Lingual',     [220, 180, 140])
    labels[23] = ('G_oc-temp_med-Parahip',     [ 65, 100,  20])
    labels[24] = ('G_orbital',                 [220,  60,  20])
    labels[25] = ('G_pariet_inf-Angular',      [ 20,  60, 220])
    labels[26] = ('G_pariet_inf-Supramar',     [100, 100,  60])
    labels[27] = ('G_parietal_sup',            [220, 180, 220])
    labels[28] = ('G_postcentral',             [ 20, 180, 140])
    labels[29] = ('G_precentral',              [ 60, 140, 180])
    labels[30] = ('G_precuneus',               [ 25,  20, 140])
    labels[31] = ('G_rectus',                  [ 20,  60, 100])
    labels[32] = ('G_subcallosal',             [ 60, 220,  20])
    labels[33] = ('G_temp_sup-G_T_transv',     [ 60,  60, 220])
    labels[34] = ('G_temp_sup-Lateral',        [220,  60, 220])
    labels[35] = ('G_temp_sup-Plan_polar',     [ 65, 220,  60])
    labels[36] = ('G_temp_sup-Plan_tempo',     [ 25, 140,  20])
    labels[37] = ('G_temporal_inf',            [220, 220, 100])
    labels[38] = ('G_temporal_middle',         [180,  60,  60])
    labels[39] = ('Lat_Fis-ant-Horizont',      [ 61,  20, 220])
    labels[40] = ('Lat_Fis-ant-Vertical',      [ 61,  20,  60])
    labels[41] = ('Lat_Fis-post',              [ 61,  60, 100])
    labels[42] = ('Medial_wall',               [ 25,  25,  25])
    labels[43] = ('Pole_occipital',            [140,  20,  60])
    labels[44] = ('Pole_temporal',             [220, 180,  20])
    labels[45] = ('S_calcarine',               [ 63, 180, 180])
    labels[46] = ('S_central',                 [221,  20,  10])
    labels[47] = ('S_cingul-Marginalis',       [221,  20, 100])
    labels[48] = ('S_circular_insula_ant',     [221,  60, 140])
    labels[49] = ('S_circular_insula_inf',     [221,  20, 220])
    labels[50] = ('S_circular_insula_sup',     [ 61, 220, 220])
    labels[51] = ('S_collat_transv_ant',       [100, 200, 200])
    labels[52] = ('S_collat_transv_post',      [ 10, 200, 200])
    labels[53] = ('S_front_inf',               [221, 220,  20])
    labels[54] = ('S_front_middle',            [141,  20, 100])
    labels[55] = ('S_front_sup',               [ 61, 220, 100])
    labels[56] = ('S_interm_prim-Jensen',      [141,  60,  20])
    labels[57] = ('S_intrapariet_and_P_trans', [143,  20, 220])
    labels[58] = ('S_oc_middle_and_Lunatus',   [101,  60, 220])
    labels[59] = ('S_oc_sup_and_transversal',  [ 21,  20, 140])
    labels[60] = ('S_occipital_ant',           [ 61,  20, 180])
    labels[61] = ('S_oc-temp_lat',             [221, 140,  20])
    labels[62] = ('S_oc-temp_med_and_Lingual', [141, 100, 220])
    labels[63] = ('S_orbital_lateral',         [221, 100,  20])
    labels[64] = ('S_orbital_med-olfact',      [181, 200,  20])
    labels[65] = ('S_orbital-H_Shaped',        [101,  20,  20])
    labels[66] = ('S_parieto_occipital',       [101, 100, 180])
    labels[67] = ('S_pericallosal',            [181, 220,  20])
    labels[68] = ('S_postcentral',             [ 21, 140, 200])
    labels[69] = ('S_precentral-inf-part',     [ 21,  20, 240])
    labels[70] = ('S_precentral-sup-part',     [ 21,  20, 200])
    labels[71] = ('S_suborbital',              [ 21,  20,  60])
    labels[72] = ('S_subparietal',             [101,  60,  60])
    labels[73] = ('S_temporal_inf',            [ 21, 180, 180])
    labels[74] = ('S_temporal_sup',            [223, 220,  60])
    labels[75] = ('S_temporal_transverse',     [221,  60,  60])
    return labels


def dkt():
    """
    Label lookup for DKT cortical atlas parcellations.

    Returns
    -------
    labels : LabelLookup
    """
    labels = LabelLookup()
    labels[0]  = ('unknown',                  [ 25,   5,  25])
    labels[1]  = ('bankssts',                 [ 25, 100,  40])
    labels[2]  = ('caudalanteriorcingulate',  [125, 100, 160])
    labels[3]  = ('caudalmiddlefrontal',      [100,  25,   0])
    labels[4]  = ('corpuscallosum',           [120,  70,  50])
    labels[5]  = ('cuneus',                   [220,  20, 100])
    labels[6]  = ('entorhinal',               [220,  20,  10])
    labels[7]  = ('fusiform',                 [180, 220, 140])
    labels[8]  = ('inferiorparietal',         [220,  60, 220])
    labels[9]  = ('inferiortemporal',         [180,  40, 120])
    labels[10] = ('isthmuscingulate',         [140,  20, 140])
    labels[11] = ('lateraloccipital',         [ 20,  30, 140])
    labels[12] = ('lateralorbitofrontal',     [ 35,  75,  50])
    labels[13] = ('lingual',                  [225, 140, 140])
    labels[14] = ('medialorbitofrontal',      [200,  35,  75])
    labels[15] = ('middletemporal',           [160, 100,  50])
    labels[16] = ('parahippocampal',          [ 20, 220,  60])
    labels[17] = ('paracentral',              [ 60, 220,  60])
    labels[18] = ('parsopercularis',          [220, 180, 140])
    labels[19] = ('parsorbitalis',            [ 20, 100,  50])
    labels[20] = ('parstriangularis',         [220,  60,  20])
    labels[21] = ('pericalcarine',            [120, 100,  60])
    labels[22] = ('postcentral',              [220,  20,  20])
    labels[23] = ('posteriorcingulate',       [220, 180, 220])
    labels[24] = ('precentral',               [ 60,  20, 220])
    labels[25] = ('precuneus',                [160, 140, 180])
    labels[26] = ('rostralanteriorcingulate', [ 80,  20, 140])
    labels[27] = ('rostralmiddlefrontal',     [ 75,  50, 125])
    labels[28] = ('superiorfrontal',          [ 20, 220, 160])
    labels[29] = ('superiorparietal',         [ 20, 180, 140])
    labels[30] = ('superiortemporal',         [140, 220, 220])
    labels[31] = ('supramarginal',            [ 80, 160,  20])
    labels[32] = ('frontalpole',              [100,   0, 100])
    labels[33] = ('temporalpole',             [ 70,  20, 170])
    labels[34] = ('transversetemporal',       [150, 150, 200])
    labels[35] = ('insula',                   [255, 192,  32])
    return labels


def tissue_types():
    """
    Label lookup for generic brain tissue types (including skull and head labels).

    Returns
    -------
    labels : LabelLookup
    """
    labels = LabelLookup()
    labels[0] = ('Unknown',                  [0,   0,   0])
    labels[1] = ('Cortex',                   [205, 62,  78])
    labels[2] = ('Subcortical-Gray-Matter',  [230, 148, 34])
    labels[3] = ('White-Matter',             [245, 245, 245])
    labels[4] = ('CSF',                      [120, 18,  134])
    labels[5] = ('Head',                     [150, 150, 200])
    labels[6] = ('Lesion',                   [255, 165,  0])
    return labels


def nonlateral_aseg_recoder(include_lesions=False):
    """
    Returns a recoding table that converts default brain labels to the
    corresponding tissue-type.

    Returns:
        RecodingLookupTable: .
    """
    include_list = [
        "Unknown",
        "Left-Cerebral-White-Matter",
        "Left-Cerebral-Cortex",
        "Left-Cerebellum-White-Matter",           
        "Left-Cerebellum-Cortex",
        "Left-Thalamus",
        "Left-Caudate",
        "Left-Putamen",
        "Left-Pallidum",
        "3rd-Ventricle",                           
        "4th-Ventricle",
        "Brain-Stem",                            
        "Left-Hippocampus",
        "Left-Amygdala",                        
        "CSF",
        "Left-Lesion",
        "Left-Accumbens-area",
        "Left-VentralDC",
        "Left-Choroid-Plexus"
    ]        
    aseg = labels()
    source_lut = labels()
    target_lut = LabelLookup()
    mapping = {}
    for key in source_lut.keys():
        if (key >= 1000 and key < 3000) or \
           (key > 11000 and key < 13000):   # destrieux labels
            name = 'Left-Cerebral-Cortex'
        elif (key >= 3000 and key < 5000) or (key >= 13000 and key < 15000) or (key >= 250 and key <= 255):
            name = 'Left-Cerebral-White-Matter'
        elif (key >= 7000 and key <= 7020):
            name = 'Left-Amygdala'
        elif (key >= 8000 and key < 9000):
            name = 'Left-Thalamus'
        elif key < 100:
            name = source_lut[key].name
            if name.startswith('Right-'):
                name = name.replace('Right-', 'Left-')
            if (name.find('Vent') >= 0 and name.find('entral') < 0):
                name = 'CSF'
            if name.find('ypoint') >= 0 or name.find('esion') >= 0 or \
               name.find('wmsa') >= 0:
                name = 'Left-Lesion'
        else:
            continue

        if name not in include_list:
            continue

        source_key = key
        target_list = target_lut.search(name)

        if len(target_list) == 0:  # not already
            target_key = len(target_lut)
            target_lut[target_key] = (name, source_lut[key].color)
        else:
            target_key = target_list[0]

        mapping[source_key] = target_key

    return LabelRecoder(mapping, target=target_lut)

def lateral_aseg_recoder(include_lesions=False):
    """
    Returns a recoding table that converts default brain labels to the
    corresponding tissue-type.

    Returns:
        RecodingLookupTable: .
    """
    include_list = [
        "Unknown",
        "Left-Cerebral-White-Matter",
        "Right-Cerebral-White-Matter",
        "Left-Cerebral-Cortex",
        "Right-Cerebral-Cortex",
        "Left-Cerebellum-White-Matter",
        "Right-Cerebellum-White-Matter",           
        "Left-Cerebellum-Cortex",
        "Right-Cerebellum-Cortex",
        "Left-Thalamus",
        "Right-Thalamus",
        "Left-Caudate",
        "Right-Caudate",
        "Left-Putamen",
        "Right-Putamen",
        "Left-Pallidum",
        "Right-Pallidum",
        "3rd-Ventricle",                           
        "4th-Ventricle",
        "Brain-Stem",                            
        "Left-Hippocampus",
        "Right-Hippocampus",
        "Left-Amygdala",
        "Right-Amygdala",                        
        "CSF",
        "Left-Lesion",
        "Right-Lesion",
        "Left-Accumbens-area",
        "Right-Accumbens-area",
        "Left-VentralDC",
        "Right-VentralDC",
        "Left-Choroid-Plexus"
        "Right-Choroid-Plexus"
    ] 
    aseg = labels()
    source_lut = labels()
    target_lut = LabelLookup()
    mapping = {}
    for key in source_lut.keys():
        l_name = source_lut[key].name
        if (key >= 1000 and key < 3000) or \
           (key > 11000 and key < 13000):   # destrieux labels
            if is_r_label(l_name):
                name = 'Right-Cerebral-Cortex'
            else:
                name = 'Left-Cerebral-Cortex'
        elif (key >= 3000 and key < 5000) or (key >= 13000 and key < 15000) or (key >= 250 and key <= 255):
            if is_r_label(l_name):
                name = 'Right-Cerebral-White-Matter'
            else:
                name = 'Left-Cerebral-White-Matter'
        elif (key >= 7000 and key <= 7020):
            if is_r_label(l_name):
                name = 'Right-Amygdala'
            else:
                name = 'Left-Amygdala'
        elif (key >= 8000 and key < 9000):
            if is_r_label(l_name):
                name = 'Right-Thalamus'
            else:
                name = 'Left-Thalamus'
        elif key < 100:
            name = l_name
            if (name.find('Vent') >= 0 and name.find('entral') < 0):
                name = 'CSF'
            if name.find('ypoint') >= 0 or name.find('esion') >= 0 or \
               name.find('wmsa') >= 0:
                if is_r_label(name):
                    name = 'Right-Lesion'
                else:
                    name = 'Left-Lesion'
        else:
            continue

        if name not in include_list:
            continue

        source_key = key
        target_list = target_lut.search(name)

        if len(target_list) == 0:  # not already
            target_key = len(target_lut)
            target_lut[target_key] = (name, source_lut[key].color)
        else:
            target_key = target_list[0]

        mapping[source_key] = target_key

    return LabelRecoder(mapping, target=target_lut)

def tissue_type_recoder(extra=False, lesions=False):
    """
    Return a recoding lookup that converts default brain labels to the
    corresponding tissue-type (includes skull and head labels).

    Parameters
    ----------
    extra : bool
        Include extra-cerebral labels, like skull and eye fluid.
    lesions : bool
        Include lesions as a seperate label.

    Returns
    -------
    recoder : LabelRecoder
    """
    mapping = {
        0:    0,  # Unknown
        2:    3,  # Left-Cerebral-White-Matter
        3:    1,  # Left-Cerebral-Cortex
        4:    4,  # Left-Lateral-Ventricle
        5:    4,  # Left-Inf-Lat-Vent
        7:    3,  # Left-Cerebellum-White-Matter
        8:    2,  # Left-Cerebellum-Cortex
        10:   2,  # Left-Thalamus
        11:   2,  # Left-Caudate
        12:   2,  # Left-Putamen
        13:   2,  # Left-Pallidum
        14:   4,  # 3rd-Ventricle
        15:   4,  # 4th-Ventricle
        16:   3,  # Brain-Stem
        17:   2,  # Left-Hippocampus
        18:   2,  # Left-Amygdala
        24:   4,  # CSF
        25:   6 if lesions else 2,  # Left-Lesion
        26:   2,  # Left-Accumbens-Area
        28:   3,  # Left-VentralDC
        30:   4,  # Left-Vessel
        31:   4,  # Left-Choroid-Plexus
        41:   3,  # Right-Cerebral-White-Matter
        42:   1,  # Right-Cerebral-Cortex
        43:   4,  # Right-Lateral-Ventricle
        44:   4,  # Right-Inf-Lat-Vent
        46:   3,  # Right-Cerebellum-White-Matter
        47:   2,  # Right-Cerebellum-Cortex
        49:   2,  # Right-Thalamus
        50:   2,  # Right-Caudate
        51:   2,  # Right-Putamen
        52:   2,  # Right-Pallidum
        53:   2,  # Right-Hippocampus
        54:   2,  # Right-Amygdala
        75:   6 if lesions else 2,  # Right-Lesion
        58:   2,  # Right-Accumbens-Area
        60:   3,  # Right-VentralDC
        62:   4,  # Right-Vessel
        63:   4,  # Right-Choroid-Plexus
        72:   4,  # 5th-Ventricle
        77:   6 if lesions else 3,  # WM-Hypointensities
        78:   3,  # Left-WM-Hypointensities
        79:   3,  # Right-WM-Hypointensities
        80:   2,  # Non-WM-Hypointensities
        81:   2,  # Left-Non-WM-Hypointensities
        82:   2,  # Right-Non-WM-Hypointensities
        85:   3,  # Optic-Chiasm
        99:   6 if lesions else 2,  # Lesion
        130:  5 if extra else 0,  # Air
        165:  5 if extra else 0,  # Skull
        172:  2,  # Vermis
        174:  3,  # Pons
        251:  3,  # CC_Posterior
        252:  3,  # CC_Mid_Posterior
        253:  3,  # CC_Central
        254:  3,  # CC_Mid_Anterior
        255:  3,  # CC_Anterior
        257:  4,  # CSF-ExtraCerebral
        258:  5 if extra else 0,  # Head-ExtraCerebral
        1001: 1,  # ctx-lh-bankssts
        1002: 1,  # ctx-lh-caudalanteriorcingulate
        1003: 1,  # ctx-lh-caudalmiddlefrontal
        1005: 1,  # ctx-lh-cuneus
        1006: 1,  # ctx-lh-entorhinal
        1007: 1,  # ctx-lh-fusiform
        1008: 1,  # ctx-lh-inferiorparietal
        1009: 1,  # ctx-lh-inferiortemporal
        1010: 1,  # ctx-lh-isthmuscingulate
        1011: 1,  # ctx-lh-lateraloccipital
        1012: 1,  # ctx-lh-lateralorbitofrontal
        1013: 1,  # ctx-lh-lingual
        1014: 1,  # ctx-lh-medialorbitofrontal
        1015: 1,  # ctx-lh-middletemporal
        1016: 1,  # ctx-lh-parahippocampal
        1017: 1,  # ctx-lh-paracentral
        1018: 1,  # ctx-lh-parsopercularis
        1019: 1,  # ctx-lh-parsorbitalis
        1020: 1,  # ctx-lh-parstriangularis
        1021: 1,  # ctx-lh-pericalcarine
        1022: 1,  # ctx-lh-postcentral
        1023: 1,  # ctx-lh-posteriorcingulate
        1024: 1,  # ctx-lh-precentral
        1025: 1,  # ctx-lh-precuneus
        1026: 1,  # ctx-lh-rostralanteriorcingulate
        1027: 1,  # ctx-lh-rostralmiddlefrontal
        1028: 1,  # ctx-lh-superiorfrontal
        1029: 1,  # ctx-lh-superiorparietal
        1030: 1,  # ctx-lh-superiortemporal
        1031: 1,  # ctx-lh-supramarginal
        1032: 1,  # ctx-lh-frontalpole
        1033: 1,  # ctx-lh-temporalpole
        1034: 1,  # ctx-lh-transversetemporal
        1035: 1,  # ctx-lh-insula
        2001: 1,  # ctx-rh-bankssts
        2002: 1,  # ctx-rh-caudalanteriorcingulate
        2003: 1,  # ctx-rh-caudalmiddlefrontal
        2005: 1,  # ctx-rh-cuneus
        2006: 1,  # ctx-rh-entorhinal
        2007: 1,  # ctx-rh-fusiform
        2008: 1,  # ctx-rh-inferiorparietal
        2009: 1,  # ctx-rh-inferiortemporal
        2010: 1,  # ctx-rh-isthmuscingulate
        2011: 1,  # ctx-rh-lateraloccipital
        2012: 1,  # ctx-rh-lateralorbitofrontal
        2013: 1,  # ctx-rh-lingual
        2014: 1,  # ctx-rh-medialorbitofrontal
        2015: 1,  # ctx-rh-middletemporal
        2016: 1,  # ctx-rh-parahippocampal
        2017: 1,  # ctx-rh-paracentral
        2018: 1,  # ctx-rh-parsopercularis
        2019: 1,  # ctx-rh-parsorbitalis
        2020: 1,  # ctx-rh-parstriangularis
        2021: 1,  # ctx-rh-pericalcarine
        2022: 1,  # ctx-rh-postcentral
        2023: 1,  # ctx-rh-posteriorcingulate
        2024: 1,  # ctx-rh-precentral
        2025: 1,  # ctx-rh-precuneus
        2026: 1,  # ctx-rh-rostralanteriorcingulate
        2027: 1,  # ctx-rh-rostralmiddlefrontal
        2028: 1,  # ctx-rh-superiorfrontal
        2029: 1,  # ctx-rh-superiorparietal
        2030: 1,  # ctx-rh-superiortemporal
        2031: 1,  # ctx-rh-supramarginal
        2032: 1,  # ctx-rh-frontalpole
        2033: 1,  # ctx-rh-temporalpole
        2034: 1,  # ctx-rh-transversetemporal
        2035: 1,  # ctx-rh-insula
    }
    return LabelRecoder(mapping, target=tissue_types())

def reduced35_aseg_recoder():
    """
    Return a recoding lookup that converts default brain labels to the
    corresponding labels in the ReducedLabels35.txt.

    Returns
    -------
    recoder : LabelRecoder
    """
    mapping = {
        0: 0,
		2: 1,
		3: 2,
		4: 3,
		5: 4,
		7: 5,
		8: 6,
		10: 7,
		11: 8,
		12: 9,
		13: 10,
		14: 11,
		15: 12,
		16: 13,
		17: 14,
		18: 15,
		24: 0,
		25: 77,
		26: 16,
		28: 17,
		30: 18,
		31: 19,
		41: 20,
		42: 21,
		43: 22,
		44: 23,
		46: 24,
		47: 25,
		49: 26,
		50: 27,
		51: 28,
		52: 29,
		53: 30,
		54: 31,
		58: 32,
		60: 33,
		62: 34,
		63: 35,
		72: 0,
		75: 13,
		77: 1,
		78: 1,
		79: 20,
		80: 2,
		81: 2,
		82: 21,
		85: 1,
		99: 77,
		130: 0,
		165: 0,
		172: 6,
		174: 13,
		251: 1,
		252: 1,
		253: 1,
		254: 1,
		255: 1,
		257: 0,
		258: 0,
		1001: 2,
		1002: 2,
		1003: 2,
		1005: 2,
		1006: 2,
		1007: 2,
		1008: 2,
		1009: 2,
		1010: 2,
		1011: 2,
		1012: 2,
		1013: 2,
		1014: 2,
		1015: 2,
		1016: 2,
		1017: 2,
		1018: 2,
		1019: 2,
		1020: 2,
		1021: 2,
		1022: 2,
		1023: 2,
		1024: 2,
		1025: 2,
		1026: 2,
		1027: 2,
		1028: 2,
		1029: 2,
		1030: 2,
		1031: 2,
		1032: 2,
		1033: 2,
		1034: 2,
		1035: 2,
		2001: 21,
		2002: 21,
		2003: 21,
		2005: 21,
		2006: 21,
		2007: 21,
		2008: 21,
		2009: 21,
		2010: 21,
		2011: 21,
		2012: 21,
		2013: 21,
		2014: 21,
		2015: 21,
		2016: 21,
		2017: 21,
		2018: 21,
		2019: 21,
		2020: 21,
		2021: 21,
		2022: 21,
		2023: 21,
		2024: 21,
		2025: 21,
		2026: 21,
		2027: 21,
		2028: 21,
		2029: 21,
		2030: 21,
		2031: 21,
		2032: 21,
		2033: 21,
		2034: 21,
		2035: 21
    }
    target_lut_path = os.path.join(os.environ.get('FREESURFER_HOME'),'luts/ReducedLabels35.txt')
    target = load_label_lookup(target_lut_path)
    return LabelRecoder(mapping, target=target)

def reduced24_aseg_recoder():
    """
    Return a recoding lookup that converts default brain labels to the
    corresponding labels in the ReducedLabels24.txt.

    Returns
    -------
    recoder : LabelRecoder
    """
    mapping = {
        0: 0,
		2: 1,
		3: 2,
		4: 3,
		5: 4,
		7: 0,
		8: 0,
		10: 5,
		11: 6,
		12: 7,
		13: 8,
		14: 9,
		15: 0,
		16: 10,
		17: 11,
		18: 0,
		24: 0,
		25: 0,
		26: 0,
		28: 12,
		30: 0,
		31: 13,
		41: 14,
		42: 15,
		43: 16,
		44: 17,
		46: 0,
		47: 0,
		49: 18,
		50: 19,
		51: 20,
		52: 21,
		53: 22,
		54: 0,
		58: 0,
		60: 23,
		62: 0,
		63: 24,
		72: 0,
		75: 10,
		77: 1,
		78: 1,
		79: 14,
		80: 2,
		81: 2,
		82: 15,
		85: 1,
		99: 0,
		130: 0,
		165: 0,
		172: 0,
		174: 10,
		251: 1,
		252: 1,
		253: 1,
		254: 1,
		255: 1,
		257: 0,
		258: 0,
		1001: 2,
		1002: 2,
		1003: 2,
		1005: 2,
		1006: 2,
		1007: 2,
		1008: 2,
		1009: 2,
		1010: 2,
		1011: 2,
		1012: 2,
		1013: 2,
		1014: 2,
		1015: 2,
		1016: 2,
		1017: 2,
		1018: 2,
		1019: 2,
		1020: 2,
		1021: 2,
		1022: 2,
		1023: 2,
		1024: 2,
		1025: 2,
		1026: 2,
		1027: 2,
		1028: 2,
		1029: 2,
		1030: 2,
		1031: 2,
		1032: 2,
		1033: 2,
		1034: 2,
		1035: 2,
		2001: 15,
		2002: 15,
		2003: 15,
		2005: 15,
		2006: 15,
		2007: 15,
		2008: 15,
		2009: 15,
		2010: 15,
		2011: 15,
		2012: 15,
		2013: 15,
		2014: 15,
		2015: 15,
		2016: 15,
		2017: 15,
		2018: 15,
		2019: 15,
		2020: 15,
		2021: 15,
		2022: 15,
		2023: 15,
		2024: 15,
		2025: 15,
		2026: 15,
		2027: 15,
		2028: 15,
		2029: 15,
		2030: 15,
		2031: 15,
		2032: 15,
		2033: 15,
		2034: 15,
		2035: 15
    }

    target_lut_path = os.path.join(os.environ.get('FREESURFER_HOME'),'luts/ReducedLabels24.txt')
    target = load_label_lookup(target_lut_path)

    return LabelRecoder(mapping, target=target)

def reduced24_reduced35_recoder():
    """
    Return a recoding lookup that converts the ReducedLabels35 labels to the
    corresponding labels in the ReducedLabels24.txt.

    Returns
    -------
    recoder : LabelRecoder
    """
    mapping = {
        0: 0,
		1: 1,
		2: 2,
		3: 3,
		4: 4,
		5: 0,
		6: 0,
		7: 5,
		8: 6,
		9: 7,
		10: 8,
		11: 9,
		12: 0,
		13: 10,
		14: 11,
		15: 0,
		16: 0,
		17: 12,
		18: 0,
		19: 13,
		20: 14,
		21: 15,
		22: 16,
		23: 17,
		24: 0,
		25: 0,
		26: 18,
		27: 19,
		28: 20,
		29: 21,
		30: 22,
		31: 0,
		32: 0,
		33: 23,
		34: 0,
		35: 24,
		77: 0
    }
    target_lut_path = os.path.join(os.environ.get('FREESURFER_HOME'), 'luts/ReducedLabels24.txt')
    target = load_label_lookup(target_lut_path)

    return LabelRecoder(mapping, target=target)

def tissue_type_reduced35_recoder():
    """
    Return a recoding lookup that converts the ReducedLabels35 labels to the
    corresponding tissue types.

    Returns
    -------
    recoder : LabelRecoder
    """
    mapping = {
		0: 0,
		1: 3,
		2: 1,
		3: 4,
		4: 4,
		5: 3,
		6: 1,
		7: 2,
		8: 2,
		9: 2,
		10: 2,
		11: 4,
		12: 4,
		13: 2,
		14: 2,
		15: 2,
		16: 2,
		17: 2,
		18: 0,
		19: 4,
		20: 3,
		21: 1,
		22: 4,
		23: 4,
		24: 3,
		25: 1,
		26: 2,
		27: 2,
		28: 2,
		29: 2,
		30: 2,
		31: 2,
		32: 2,
		33: 2,
		34: 0,
		35: 4,
		77: 0        
    }
    
    return LabelRecoder(mapping, target=tissue_types())

def tissue_type_reduced24_recoder():
    """
    Return a recoding lookup that converts the ReducedLabels24 labels to the
    corresponding tissue types.

    Returns
    -------
    recoder : LabelRecoder
    """
    mapping = {
		0: 0,
		1: 3,
		2: 1,
		3: 4,
		4: 4,
		5: 2,
		6: 2,
		7: 2,
		8: 2,
		9: 4,
		10: 2,
		11: 2,
		12: 2,
		13: 4,
		14: 3,
		15: 1,
		16: 4,
		17: 4,
		18: 2,
		19: 2,
		20: 2,
		21: 2,
		22: 2,
		23: 2,
		24: 4        
    }

    return LabelRecoder(mapping, target=tissue_types())

def is_r_label(label_name):
    """
    Returns an int corresponding to the 'sidedness' of a label name
    
    Returns
    -------
    int : 1 if name corresponds to right hemi; 0 if the name corresponds to
          the left hemi; -1 if there is no left/right associated with the label
    """
    if '-rh-' in label_name or '_rh_' in label_name or 'Right-' in label_name:
        return 1
    elif '-lh-' in label_name or '_lh_' in label_name or 'Left-' in label_name:
        return 0
    else:
        return -1