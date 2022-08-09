Installation
============

The surfa package supports Python 3.6+ and can be installed with pip:

```
pip install surfa
```

The installation requires that a c/c++ compiler, like gcc or clang, exists on the system in order to build Cython-based utilies. If you run into issues during the install process, see the **compiling** section below.

## Extra Package Dependencies

Surfa requires a handful of packages that are installed automatically as pip dependencies. The only exception is **pyembree**, an optional package necessary for methods using ray-tracing, like mesh self-intersection removal and spherical parameterization. Pyembree can be installed with pip (only for Python 3.8+) or conda.

## Compiling

When surfa is pip-installed, utilities written in Cython must be built from source on the system. In most cases, this process will occur behind the scenes without issue, but on barebones systems, the install might throw an error because a c/c++ compiler was not found. You will need to install these tools with the commands below (these might require sudo).

On **Ubuntu/Debian**: `apt-get install build-essential python3-dev`
<br>
On **CentOS/RHEL**: `yum install libgomp gcc python3 python3-devel`

This shouldn't be an issue on macOS, which will likely have clang pre-installed. If this is not the case, feel free to [open up an issue](https://github.com/freesurfer/surfa/issues). As for Windows, I have idea what to say about that.
