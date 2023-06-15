Installation
============

The surfa package supports Python 3.6+ and can be installed with pip:

```
pip install surfa
```

The above command should run smoothly and require no further steps, but if your system does not have a c compiler installed it will throw an error.  To resolve this potential issue, review the suggested steps in the troubleshooting section below.

**Troubleshooting Installation Errors**

When surfa is pip-installed, utilities written in c must be built from source on the system. In most cases, this process will occur behind the scenes without issue, but on barebones systems, the install might throw an error because a c compiler was not found. You will need to install these tools with the commands below (these might require sudo).

On Ubuntu/Debian: `apt-get install build-essential python3-dev`
<br>
On CentOS/RHEL: `yum install libgomp gcc python3 python3-devel`

This shouldn't be an issue on macOS, which will likely have clang pre-installed. If this is not the case, feel free to [open up an issue](https://github.com/freesurfer/surfa/issues). As for Windows, I have idea what to say about that.
