import os
import shutil
import tempfile
import numpy as np

from surfa import Mesh
from surfa import load_volume
from surfa import load_mesh
from surfa.system import run
from surfa.system import collect_output
from surfa.image import cast_image
from surfa.mesh import cast_overlay
from surfa.mesh import cast_mesh
from surfa.mesh import is_mesh_castable


class Freeview:

    def __init__(self, title=None, debug=False, use_vglrun=True, return_edits=False):
        """
        A visualization class that wraps the `freeview` command.

        This function assumes FreeView is installed and the `freeview` command is
        accessible in the shell. Images can be configured in the wrapper like so:

            fv = Freeview()
            fv.add_image(img)
            fv.add_image(seg, colormap='lut', opacity=0.5)
            fv.add_mesh(mesh, overlay=overlay)
            fv.show()

        To reload the data visualized inf FreeView after the viewer closes, specify
        'return_edits=True' and assign the return value of fv.show() to be a variable:

            fv = Freeview(return_edits=True)
            fv.add_image(img)
            fv_contents = fv.show()

        This will return a tuple of lists, with the first list containing volumes and
        the second list containing any data added to the viewer via fv.add_mesh(mesh).
        Items will be returned in the order that they are added to FreeView.

        For a quicker but more limited way to wrap freeview, see the `fv()` function.
        """
        self.tempdir = None
        self.debug = debug
        self.title = title
        self.isshown = False
        self.use_vglrun = use_vglrun
        self.arguments = []
        self._return_edits = return_edits
        self._vols = []
        self._meshes = []
        

        # first check if freeview is even accessible
        self.fvpath = shutil.which('freeview')
        if self.fvpath is None:
            raise RuntimeError('cannot find `freeview` command in shell')
        if self.debug:
            print(f'using freeview command from {self.fvpath}')

        self.tempdir = tempfile.mkdtemp()
        if self.debug:
            print(f'creating temporary directory at {self.tempdir}')

    def __del__(self):
        """
        If the session is shutting down and the window was never opened, make sure
        to remove the temporary directory.
        """
        if not self.isshown and self.tempdir is not None and os.path.exists(self.tempdir):
            shutil.rmtree(self.tempdir)

    def add_image(self, img, **kwargs):
        """
        Adds an image to the freeview window. Any key/value tags allowed as a `-v` option
        in the freeview command line can be provided as an additional argument.

        Parameters
        ----------
        img: array_like, FramedImage, or str
            Image or filename to load in the freeview session.
        **kwargs:
            Additional options to append as key/values tags to the freeview volume argument.
        """
        # convert the input to a proper file (if it's not one already)
        if isinstance(img, str):
            if not os.path.isfile(img):
                print(f'freeview error: image file {img} does not exist')
                return
            filename = img
        else:
            img = cast_image(img, allow_none=False)
            filename = _unique_filename('image', '.mgz', self.tempdir)
            img.save(filename)
            if self.debug:
                print(f'wrote image to {filename}')
        
        # add the path to the temp vol to the internal list of volumes
        self._vols.append(filename)

        # configure the corresponding freeview argument
        self.arguments.append('-v ' + filename + _convert_kwargs_to_tags(kwargs))

    def add_mesh(self, mesh, curvature=None, overlay=None, annot=None, name=None, **kwargs):
        """
        Adds an image to the freeview window. Any key/value tags allowed as a `-v` option
        in the freeview command line can be provided as an additional argument.

        Parameters
        ----------
        img: array_like, FramedImage, or str
            Image or filename to load in the freeview session.
        overlay : Overlay or sequence of Overlays
            Load overlay on mesh data.
        annot : Overlay or sequence of Overlays
            Load annotation on mesh data.
        **kwargs:
            Additional options to append as key/values tags to the freeview volume argument.
        """
        # convert the input to a proper file (if it's not one already)
        if isinstance(mesh, str):
            if not os.path.isfile(mesh):
                print(f'freeview error: mesh file {mesh} does not exist')
                return
            mesh_filename = mesh
        else:
            mesh = cast_mesh(mesh, allow_none=False)
            mesh_filename = _unique_filename('mesh', '', self.tempdir)
            mesh.save(mesh_filename)
            if self.debug:
                print(f'wrote mesh to {mesh_filename}')

        # extra tags for the mesh
        tags = ''

        # configure any curvatures
        if curvature is not None:
            curvature = [curvature] if not isinstance(curvature, (list, tuple)) else curvature
            for c in curvature:
                c = FreeviewCurvature(c) if not isinstance(c, FreeviewCurvature) else c
                filename = _unique_filename(c.name, '.mgz', self.tempdir)
                c.arr.save(filename)
                if self.debug:
                    print(f'wrote curvature to {filename}')
                tags += f':curvature={filename}' + c.tags()

        # configure any overlays
        if overlay is not None:
            overlay = [overlay] if not isinstance(overlay, (list, tuple)) else overlay
            for c in overlay:
                c = FreeviewOverlay(c) if not isinstance(c, FreeviewOverlay) else c
                filename = _unique_filename(c.name, '.mgz', self.tempdir)
                c.arr.save(filename)
                if self.debug:
                    print(f'wrote overlay to {filename}')
                tags += f':overlay={filename}' + c.tags()

        # configure any annotations
        if annot is not None:
            annot = [annot] if not isinstance(annot, (list, tuple)) else annot
            for c in annot:
                c = FreeviewAnnot(c) if not isinstance(c, FreeviewAnnot) else c
                filename = _unique_filename(c.name, '.annot', self.tempdir)
                c.arr.save(filename)
                if self.debug:
                    print(f'wrote annotation to {filename}')
                tags += f':annot={filename}'

        if name is not None:
            tags += f':name={name}'
        
        # add the path to the temp vol to the internal list of volumes
        self._meshes.append(filename)

        # configure the corresponding freeview argument
        self.arguments.append('-f ' + mesh_filename + tags + _convert_kwargs_to_tags(kwargs))

    def add_flag(self, flag):
        """
        Add a flag to the freeview command.

        Parameters
        ----------
        flag : str
            Extra command-line option added to the freeview call.
        """
        self.arguments.append(flag)

    def show(self, background=True, threads=None):
        """
        Opens the configured FreeView window.

        Parameters
        ----------
        background : bool
            Run FreeView window as a background process.
        threads : int
            Number of OMP threads available to FreeView.
        """
        # set background based on _return_edits
        background = background if not self._return_edits else False
        
        # compile the command
        command = self.fvpath + ' ' + ' '.join(self.arguments)

        # add window title
        if self.title is not None:
            title = self.title.replace('"', "'")
            command = f'{command} -subtitle "{title}"'

        # be sure to remove the temporary directory (if it exists) after freeview closes
        # need the tempdir if saving edits
        if not self._return_edits:
            command = f'{command} ; rm -rf {self.tempdir}'

        # freeview can be buggy when run remotely, so let's test if VGL is
        # available to wrap the process
        if self.use_vglrun:
            vgl = _find_vgl()
            if vgl is not None:
                command = f'{vgl} {command}'

        # set number of OMP threads if provided
        if threads is not None:
            command = f'OMP_NUM_THREADS={threads} {command}'

        if self.debug:
            print('running FreeView command:')
            print(command)

        # mark the window has been opened to avoid future modification
        self.isshown = True

        # run it
        ret_code = run(command, background=background)

        # reload the vol/mesh data before deleting the tempdir, if necessary
        if self._return_edits:
            print('Reloading temp volumes into surfa')
            vols = [load_volume(x) for x in self._vols]
            meshes = [load_mesh(x) for x in self._meshes]
           
            # clean up the tempdir
            shutil.rmtree(self.tempdir)

            return vols, meshes


class FreeviewCurvature:

    def __init__(self, arr, name='curvature', method='binary'):
        """
        Configuration for freeview curvature.
        """
        self.arr = cast_overlay(arr, allow_none=False)
        self.name = name
        self.method = method

    def tags(self):
        tags = ''
        tags += '' if self.method is None else f':curvature_method={self.method}'
        return tags


class FreeviewOverlay:

    def __init__(self, arr, name='overlay', threshold=None, opacity=None, color=None, custom=None):
        """
        Configuration for freeview overlays.
        """
        self.arr = cast_overlay(arr, allow_none=False)
        self.name = name
        self.threshold = threshold
        self.opacity = opacity
        self.color = color
        self.custom = custom

    def tags(self):
        tags = ''
        tags += '' if self.threshold is None else f':overlay_threshold=' + ','.join(str(x) for x in self.threshold)
        tags += '' if self.opacity is None else f':overlay_opacity={self.opacity}'
        tags += '' if self.color is None else f':overlay_color={self.color}'
        tags += '' if self.custom is None else f':overlay_custom={self.custom}'
        return tags


class FreeviewAnnot:

    def __init__(self, arr, name='annotation'):
        """
        Configuration for freeview annotations.
        """
        self.arr = cast_overlay(arr, allow_none=False)
        self.name = name


def fv(*args, **kwargs):
    """
    Freeview wrapper to quickly load an arbitray number of elements. Inputs
    can be existing filenames, images, meshes, or numpy arrays. Lists
    are also supported. Use the `Freeview` class directly to configure a
    more advanced session.

    Parameters
    ----------
    *args : array_like, FramedImage, Mesh, or str
        Elements to load in FreeView window.
    **kwargs
        Parameters forwarded to the Freeview constructor.
    """
    background = kwargs.pop('background', True)

    # initialize session
    fv = Freeview(**kwargs)

    # expand any nested lists/tuples within args
    def flatten(deep):
        for el in deep:
            if isinstance(el, (list, tuple)):
                yield from flatten(el)
            else:
                yield el

    # cycle through arguments
    for arg in flatten(args):
        if is_mesh_castable(arg):
            fv.add_mesh(arg)
        else:
            fv.add_image(arg)

    # show the window
    fv.show(background=background)


def _find_vgl():
    """
    Locate the VGL wrapper if installed.
    """
    have_key = os.path.isfile('/etc/opt/VirtualGL/vgl_xauth_key')
    vgl_path = shutil.which('vglrun')
    if vgl_path is None:
        vgl_path = shutil.which('vglrun', path='/usr/pubsw/bin')
    if vgl_path is None:
        return None
    islocal = any([os.environ.get('DISPLAY', '').endswith(string) for string in (':0', ':0.0')])
    no_glx = 'NV-GLX' in collect_output('xdpyinfo')[0]
    if not islocal and not no_glx:
        return vgl_path
    return None


def _convert_kwargs_to_tags(kwargs):
    """
    Converts a kwargs dictionary to freeview key/value tags
    """
    tags = kwargs.pop('opts', '')
    for key, value in kwargs.items():
        if isinstance(value, (list, tuple)):
            value = ','.join(str(x) for x in value)
        if value is not None:
            value = value.replace(' ', '-')
            tags += f':{key}={value}'
    return tags


def _unique_filename(filename, extension, directory):
    """
    Identifies a unique filename from a base string in a directory.
    """
    # make sure extension start with a dot
    if extension and not extension.startswith('.'):
        extension = f'.{extension}'

    # check if it's unique
    fullpath = os.path.join(directory, f'{filename}{extension}')
    if not os.path.exists(fullpath):
        return fullpath

    # append numbers until a unique filename is created (stop after 10k tries)
    for n in range(2, 10000):
        fullpath = os.path.join(directory, f'{filename}-{n:02d}{extension}')
        if not os.path.exists(fullpath):
            return fullpath
    raise RuntimeError(f'could not generate a unique filename for {filename} after trying many times')
