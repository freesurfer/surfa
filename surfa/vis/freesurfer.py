import os
import shutil
import tempfile
import numpy as np

from surfa.system import run
from surfa.system import collect_output
from surfa.image import cast_image


class Freeview:

    def __init__(self, title=None, debug=False):
        """
        A visualization class that wraps the `freeview` command.

        This function assumes FreeView is installed and the `freeview` command is
        accessible in the shell. Images can be configured in the wrapper like so:

            fv = Freeview()
            fv.images(img)
            fv.images(seg, colormap='lut', opacity=0.5)
            fv.show()

        For a quicker but more limited way to wrap freeview, see the `fv()` function.
        """
        self.debug = debug
        self.title = title
        self.isshown = False
        self.arguments = []

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

        # configure the corresponding freeview argument
        self.arguments.append('-v ' + filename + _convert_kwargs_to_tags(kwargs))

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

        # compile the command
        command = self.fvpath + ' ' + ' '.join(self.arguments)

        # add window title
        if self.title is not None:
            title = self.title.replace('"', "'")
            command = f'{command} -subtitle "{title}"'

        # be sure to remove the temporary directory (if it exists) after freeview closes
        command = f'{command} ; rm -rf {self.tempdir}'

        # freeview can be buggy when run remotely, so let's test if VGL is
        # available to wrap the process
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
        run(command, background=background)


def fv(*args, **kwargs):
    """
    Freeview wrapper to quickly load an arbitray number of elements. Inputs
    can be existing filenames, volumes, or numpy arrays. Lists are also supported.
    Use the `Freeview` class directly to configure a more advanced session.

    Parameters
    ----------
    *args : array_like, FramedImage, or str
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
    if not islocal and not nvglx:
        return vgl_path
    return None


def _convert_kwargs_to_tags(kwargs):
    """
    Converts a kwargs dictionary to freeview key/value tags
    """
    tags = ''
    for key, value in kwargs.items():
        if isinstance(value, (list, tuple)):
            value = ','.join(str(x) for x in value)
        if value is not None:
            vale = value.replace(' ', '-')
            tags += f':{key}={value}'
    return tags


def _unique_filename(filename, extension, directory):
    """
    Identifies a unique filename from a base string in a directory.
    """
    # make sure extension start with a dot
    if not extension.startswith('.'):
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
