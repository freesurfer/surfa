#!/usr/bin/env python

import os
import re
import pathlib
import platform
import sys

from setuptools import setup
from setuptools import dist
from setuptools.extension import Extension
from wheel.bdist_wheel import bdist_wheel


# https://github.com/joerick/python-abi3-package-sample/blob/main/setup.py
class bdist_wheel_abi3(bdist_wheel):  # noqa: D101
    def get_tag(self):  # noqa: D102
        python, abi, plat = super().get_tag()

        # Only meaningful when we are *actually* building an abi3 wheel.
        # We target cp311 as the minimum CPython that supports the features
        # this project relies on for limited API mode.
        if python.startswith("cp"):
            return "cp311", "abi3", plat

        return python, abi, plat



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

# configure c extensions
ext_opts = dict(
    extra_compile_args=['-O3', '-std=c99'],
    define_macros=[('NPY_NO_DEPRECATED_API', 'NPY_1_7_API_VERSION')],
)
macros = []
setup_opts = {}

ABI3 = (os.environ.get("SURFA_ABI3", "0") == "1")

if ABI3 and sys.version_info >= (3, 11) and platform.python_implementation() == "CPython":
    ext_opts["define_macros"].append(("Py_LIMITED_API", "0x030B0000"))
    ext_opts["py_limited_api"] = True
    setup_opts["cmdclass"] = {"bdist_wheel": bdist_wheel_abi3}
extensions = [
    Extension('surfa.image.interp', [f'surfa/image/interp.pyx'], **ext_opts),
    Extension('surfa.mesh.intersection', [f'surfa/mesh/intersection.pyx'], **ext_opts),
]

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
    license='MIT',
    license_files = ('LICENSE.txt',),
    description='Utilities for medical image and surface processing.',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    author='Andrew Hoopes',
    author_email='freesurfer@nmr.mgh.harvard.edu',
    url='https://github.com/freesurfer/surfa',
    python_requires='>=3.8',
    packages=packages,
    ext_modules=extensions,
    include_dirs=include_dirs,
    package_data={'': ['*.pyx', '*.h']},
    install_requires=requirements,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'Natural Language :: English',
        'Topic :: Scientific/Engineering',
    ],
    **setup_opts,
)
