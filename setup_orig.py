#!/usr/bin/env python

import re
import pathlib

from setuptools import setup
from setuptools import dist
from setuptools.extension import Extension

dist.Distribution().fetch_build_eggs(['packaging', 'cython', 'numpy'])

import packaging.version
import numpy as np
from Cython.Build import cythonize


requirements = [
    'cython',
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

long_description = '''Surfa is a collection of Python (3.5+) utilities for medical image
analysis and mesh-based surface processing. It provides tools that operate on 3D image
arrays and triangular meshes with consideration of their representation in a world (or
scanner) coordinate system. While broad in scope, surfa is developed with particular
emphasis on neuroimaging applications, as it is an extension of the FreeSurfer brain
analysis software suite.
'''

# run setup
setup(
    name='surfa',
    version=version,
    description='Utilities for medical image processing and surface reconstruction.',
    long_description=long_description,
    author='Andrew Hoopes',
    author_email='freesurfer@nmr.mgh.harvard.edu',
    url='https://github.com/freesurfer/surfa',
    python_requires='>=3.5',
    packages=packages,
    ext_modules=ext_modules,
    include_dirs=[np.get_include()],
    package_data={'': ['*.pyx']},
    install_requires=requirements,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Natural Language :: English',
        'Topic :: Scientific/Engineering',
    ],
)
