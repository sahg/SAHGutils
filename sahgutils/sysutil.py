# System utility functions
from subprocess import Popen, PIPE

def exec_command(cmd_args):
    """Execute a shell command in a subprocess

    Convenience wrapper around subprocess to execute a shell command
    and pass back stdout, stderr, and the return code. This function
    waits for the subprocess to complete, before returning.

    Usage example:
    >>> stdout, stderr, retcode = exec_command(['ls', '-lhot'])

    Parameters
    ----------
    cmd_args : list of strings
        The args to pass to subprocess. The first arg is the program
        name.

    Returns
    -------
    stdout : string
        The contents of stdout produced by the shell command
    stderr : string
        The contents of stderr produced by the shell command
    retcode : int
        The return code produced by the shell command

    """
    proc = Popen(cmd_args, stdout=PIPE, stderr=PIPE)
    stdout, stderr = proc.communicate()
    proc.wait()

    return stdout, stderr, proc.returncode
