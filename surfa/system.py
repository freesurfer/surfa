import os
import sys
import platform
import subprocess as sp
import warnings

import numpy as np


# reformat default warning message to make it a bit more mininalistic
def formatwarning(message, category, filename, lineno, line=None):
    return f'{category.__name__}: {message}\n'
warnings.formatwarning = formatwarning


def run(command, silent=False, background=False, executable='/bin/bash', log=None):
    """
    Runs a shell command and returns the exit code.

    Parameters
    ----------
    command : str
        Command to run.
    silent : bool
        Send output to devnull.
    background : bool
        Run command as a background process.
    executable : str
        Shell executable. Defaults to bash.
    log : str
        Send output to a log file.

    Returns
    -------
    int
        Command exit code.
    """

    # redirect the standard output appropriately
    if silent:
        std = {'stdout': sp.DEVNULL, 'stderr': sp.DEVNULL}
    elif not background:
        std = {'stdout': sp.PIPE, 'stderr': sp.STDOUT}
    else:
        std = {}  # do not redirect

    # run the command
    process = sp.Popen(command, **std, shell=True, executable=executable)
    if not background:
        # write the standard output stream
        if process.stdout:
            for line in process.stdout:
                decoded = line.decode('utf-8')
                if log is not None:
                    with open(log, 'a') as file:
                        file.write(decoded)
                sys.stdout.write(decoded)
        # wait for process to finish
        process.wait()

    return process.returncode


def collect_output(command, executable='/bin/bash'):
    """
    Collect the output of a shell command.

    Parameters
    ----------
    command : str
        Command to run.
    executable : str
        Shell executable. Defaults to bash.

    Returns
    -------
    tuple of (str, int)
        Tuple containing the command output and the corresponding exit code.
    """
    result = sp.run(command, stdout=sp.PIPE, stderr=sp.STDOUT, shell=True, executable=executable)
    return (result.stdout.decode('utf-8'), result.returncode)


def hostname(short=True):
    """
    Get the system hostname.

    Parameters
    ----------
        short: Provide the short hostname. Defaults to True.
    """
    node = platform.node()
    if short:
        return node.split('.')[0]
    return node


def vmpeak(pid=None):
    """
    Return the peak memory usage of the process in kilobytes.

    Note: This only works on linux machines because it requires `/proc/self/status`.
    """
    # TODO: switch to this (portable across platforms)
    # return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if (pid is None):
        procstatus = '/proc/self/status'
    else:
        procstatus = os.path.join('/proc', str(pid), 'status')
    if os.path.exists(procstatus):
        with open(procstatus, 'r') as file:
            for line in file:
                if 'VmPeak' in line:
                    return int(line.split()[1])
    return None


def fatal(message, retcode=1):
    """
    Print an error message and exit (or raise an exception if in interactive mode).

    Parameters
    ----------
    message : str
        Error message to print
    retcode : int
        Exit code. Defaults to 1.
    """
    import __main__ as main
    if hasattr(main, '__file__'):
        print(f'Error: {message}')
        sys.exit(retcode)
    else:
        raise Exception(message)


def readlines(filename):
    """
    Read the lines of a text file.

    Parameters
    ----------
    filename : str
        Text file to read.

    Returns
    -------
    content : list
        List of stripped lines in text file.
    """
    with open(filename) as file:
        content = file.read().splitlines()
    return content


def kdtree_workers(workers=None):
    """
    Number of workers to use for SciPy KD-tree queries.

    An explicit `workers` value takes precedence. Otherwise the optional
    ``SURFA_NUM_THREADS`` environment variable is read, so that a
    process-level CPU cap (e.g. the cores allocated to a batch job) can be
    respected without changing any code. SciPy interprets ``-1`` as "use all
    CPUs reported by the OS", which oversubscribes shared or cgroup-limited
    nodes.

    Parameters
    ----------
    workers : int, optional
        Explicit number of workers: ``-1`` (all CPUs) or a positive integer.
        If None (default), ``SURFA_NUM_THREADS`` decides.

    Returns
    -------
    int
        ``-1`` (all CPUs; the default when neither is given) or a positive
        number of workers.
    """
    if workers is not None:
        if isinstance(workers, bool) or not isinstance(workers, (int, np.integer)) \
                or workers == 0 or workers < -1:
            raise ValueError(f'workers must be -1 or a positive integer, got {workers!r}')
        return int(workers)
    value = os.environ.get('SURFA_NUM_THREADS', '').strip()
    if not value:
        return -1
    try:
        workers = int(value)
    except ValueError:
        workers = 0
    if workers == 0 or workers < -1:
        raise ValueError(f'SURFA_NUM_THREADS must be -1 or a positive integer, got {value!r}')
    return workers
