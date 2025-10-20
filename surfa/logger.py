import sys
import os
import logging

# default logging level, if no env var set
DEFAULT_LEVEL = 'WARNING'
# env var to check
SF_LOG_VAR = 'SURFA_LOG_LEVEL'

# intitalize the logger global ref
_sf_log = None
# global to hold the log level of the console handler
_log_level = None

def _is_valid_log_level(log_level:str):
    """
    Validate that a string corresponds to a recognized logging level.

    Parameters
    ----------
    log_level : str
        Logging level to check. Expected values are:
        ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

    Returns
    -------
    bool
        True if log_level is valid, False otherwise.
    """
    valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    if not isinstance(log_level, str):
        return False
    return log_level.upper() in valid_levels

def _validate_log_level(log_level:str=None):
    """
    Validate the log_level and ensure it is an upper case str.

    Parameters
    ----------
    log_level : str or None, optional
        Desired logging level. If None or invalid, the function falls back to
        the value of the environment variable SURFA_LOG_LEVEL if set, otherwise
        to the default level 'WARNING'.

    Returns
    -------
    str
        A valid uppercase logging level string.
    """
    if log_level is None:
        return os.environ.get(SF_LOG_VAR, DEFAULT_LEVEL)
    elif not _is_valid_log_level(log_level):
        return os.environ.get(SF_LOG_VAR, DEFAULT_LEVEL)
    else:
        return log_level.upper()

def _configure_logger(log_level:str=None):
    """
    Create and configure the global surfa logger.

    This function initializes a single logger instance with a console handler.
    The handler level is set based on the given or default log level.
    If the logger already exists, a warning is emitted and no changes are made.

    Parameters
    ----------
    log_level : str, optional
        Logging level to set. If None, falls back to environment or default.
    """
    global _sf_log, _log_level

    # validate the log_level passed
    log_level = _validate_log_level(log_level)
    
    # if logger not configured, create one
    if _sf_log is None:
        # create a surfa logger
        _sf_log = logging.getLogger('surfa')
        # set the log level to be the debug (handlers manage own levels)
        _sf_log.setLevel(logging.DEBUG)

        # create a console handler
        console = logging.StreamHandler(sys.stdout)
        # set the logging level to the default
        console.setLevel(getattr(logging, log_level))

        # define the log format
        fmt = logging.Formatter("%(levelname)s | %(asctime)s | %(name)s:%(filename)s:%(lineno)s | %(message)s", datefmt="%Y-%m-%d_%H:%M:%S")
        # set console format
        console.setFormatter(fmt)

        # add console handler to the logger
        _sf_log.addHandler(console)

        # update global ref to _log_level
        _log_level = log_level

    # if already configured, log a warning as this shouldn't happen
    else:
        _sf_log.warning('_configure_logger called, but logger already exists.')

def get_logger(log_level:str=None):
    """
    Retrieve the global surfa logger instance.

    If the logger has not yet been configured, it will be initialized with
    the specified or default logging level. Calling this function without
    arguments preserves the current logging level.

    Parameters
    ----------
    log_level : str or None, optional
        Desired logging level. If None, uses the existing level.

    Returns
    -------
    logging.Logger
        The configured Surfa logger instance.
    """
    global _sf_log, _log_level
    
    # create and return logger, use current state of log level if one not passed
    if _sf_log is None:
        _configure_logger(_validate_log_level(log_level if log_level is not None else _log_level))
        return _sf_log
    
    # if log level is not curerent _sf_log.level, update it, unless None
    if _validate_log_level(log_level) is not logging.getLevelName(_sf_log.level) and log_level is not None:
        set_log_level(log_level)
    return _sf_log

def set_log_level(log_level:str):
    """
    Set the console handler log level for the global Surfa logger.

    Parameters
    ----------
    log_level : str
        Desired log level: ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']. 
        Invalid levels will trigger a warning and have no effect.
    """
    global _sf_log, _log_level
    if _sf_log is not None:
        if _is_valid_log_level(log_level):
            _log_level = log_level.upper()
            for handler in _sf_log.handlers:
                handler.setLevel(_validate_log_level(log_level))
        else:
            _sf_log.warning(f'Invalid log level requested: {log_level}')
    else:
        return _configure_logger(log_level)

def get_log_level():
    """
    Get the current console handler log level.

    Returns
    -------
    str or None
        The current log level (uppercase string) if the logger has been
        initialized, otherwise None.
    """
    global _sf_log
    if _sf_log is None:
        return None
    else:
        return logging.getLevelName(_sf_log.level)
