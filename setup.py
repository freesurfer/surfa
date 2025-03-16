#!/usr/bin/env python

import re
import pathlib

from setuptools import setup
from setuptools import dist
from setuptools.extension import Extension


requirements = [
    'numpy',
    'scipy',
    'nibabel>=2.1',
    'Pillow',
    'xxhash',
]

packages = [
    'surfa',
    'surfa.core',
    'surfa.transform',
    'surfa.image',
    'surfa.mesh',
    'surfa.io',
    'surfa.vis',
]

# base source directory
base_dir = pathlib.Path(__file__).parent.resolve()

# we don't want to require cython for package install from
# source distributions, like pypi installs, and the best way I
# can think of to detect this is by checking if PKG-INFO exists
cython_build = not base_dir.joinpath('PKG-INFO').is_file()

# configure c extensions
ext = 'pyx' if cython_build else 'c'
ext_opts = dict(extra_compile_args=['-O3', '-std=c99'])
extensions = [
    Extension('surfa.image.interp', [f'surfa/image/interp.{ext}'], **ext_opts),
    Extension('surfa.mesh.intersection', [f'surfa/mesh/intersection.{ext}'], **ext_opts),
]

# if building locally or installing from somewhere that isn't
# an sdist, like directly from github, we'll want to cythonize
# the pyx files, so cython is a hard requirement here
if cython_build:
    from Cython.Build import cythonize
    extensions = cythonize(extensions, compiler_directives={'language_level' : '3'})

# since we interface the c stuff with numpy, it's another hard
# requirement at build-time
import numpy as np
include_dirs = [np.get_include()]

# extract the current version
init_file = base_dir.joinpath('surfa/__init__.py')
init_text = open(init_file, 'rt').read()
pattern = r"^__version__ = ['\"]([^'\"]*)['\"]"
match = re.search(pattern, init_text, re.M)
if not match:
    raise RuntimeError(f'Unable to find __version__ in {init_file}.')
version = match.group(1)

long_description = '''Surfa is a collection of Python utilities for medical image
analysis and mesh-based surface processing. It provides tools that operate on 3D image
arrays and triangular meshes with consideration of their representation in a world (or
scanner) coordinate system. While broad in scope, surfa is developed with particular
emphasis on neuroimaging applications.
'''

# run setup
setup(
    name='surfa',
    version=version,
    description='Utilities for medical image and surface processing.',
    long_description=long_description,
    author='Andrew Hoopes',
    author_email='freesurfer@nmr.mgh.harvard.edu',
    url='https://github.com/freesurfer/surfa',
    python_requires='>=3.6',
    packages=packages,
    ext_modules=extensions,
    include_dirs=include_dirs,
    package_data={'': ['*.pyx'], '': ['*.h']},
    install_requires=requirements,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Natural Language :: English',
        'Topic :: Scientific/Engineering',
    ],
)
