#!/usr/bin/env python

import os
import re
import pathlib
import setuptools
import packaging.version


# the freesurfer python packages
packages = [
    'surfa',
]

# todoc
base_dir = pathlib.Path(__file__).parent.resolve()

# get required dependencies
with open(base_dir.joinpath('requirements.txt')) as file:
    requirements = [line for line in file.read().splitlines() if not line.startswith('#')]

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

setuptools.setup(
    name='surfa',
    version=version,
    description='Utilities for neuroimaging and cortical surface reconstruction.',
    author='Andrew Hoopes',
    author_email='freesurfer@nmr.mgh.harvard.edu',
    url='https://github.com/freesurfer/surfa',
    packages=setuptools.find_packages(include=packages),
    install_requires=requirements,
)
