#!/usr/bin/env python

import re
import numpy
import pathlib
import packaging.version

import setuptools
from setuptools.extension import Extension

from Cython.Build import cythonize


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

# get required dependencies
with open(base_dir.joinpath('requirements.txt')) as file:
    requirements = [line for line in file.read().splitlines() if not line.startswith('#')]

# build cython modules
ext_modules = cythonize([
        Extension('surfa.image.interp', ['surfa/image/interp.pyx']),
    ],
    compiler_directives={'language_level' : '3'})

# extract the current version
init_file = base_dir.joinpath('surfa/__init__.py')
init_text = open(init_file, 'rt').read()
pattern = r"^__version__ = ['\"]([^'\"]*)['\"]"
match = re.search(pattern, init_text, re.M)
if not match:
    raise RuntimeError(f'Unable to find __version__ in {init_file}.')
version = match.group(1)
if isinstance(packaging.version.parse(version), packaging.version.LegacyVersion):
    raise RuntimeError(f'Invalid version string {version}.')

# run setup
setuptools.setup(
    name='surfa',
    version=version,
    description='Utilities for neuroimaging and cortical surface reconstruction.',
    author='Andrew Hoopes',
    author_email='freesurfer@nmr.mgh.harvard.edu',
    url='https://github.com/freesurfer/surfa',
    packages=packages,
    ext_modules=ext_modules,
    include_dirs=[numpy.get_include()],
    install_requires=requirements,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
)
