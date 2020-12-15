#!/usr/bin/env python3
# Copyright 2020 Canonical Ltd.
# See LICENSE file for licensing details.
#
# Helper for running bash commands via Python.
#

import logging
import os
import shlex
import subprocess

logger = logging.getLogger('charm')


def _shell(cmd, user='root', save_out=False, raise_error=False):
    """Run a shell command in a subprocess.

    A lot of this charm is just bash commands, and we'll use this to
    make them play nicely, piping STDOUT and STDERR to our logger.

    :param cmd: string representing the bash call.
    :param user: Optionally run the command as this user.
    :param save_out: save and return output. Warning: this can get large.
        Use with caution!

    Raises an error if the command returns a non zero exit
    code. Returns either an empty string, or the output on a succesful
    command.

    """
    env = os.environ.copy()
    output = ""

    if user != 'root':
        cmd = "sudo -H -u {} bash -c '{}'".format(user, cmd)

    logger.info("Running '{}'".format(cmd))

    proc = subprocess.Popen(
        shlex.split(cmd),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=1,
        universal_newlines=True,
        encoding='utf-8',
        env=env
    )

    for line in iter(proc.stdout.readline, ''):
        logger.debug("(python subprocess) {}".format(line))
        if save_out:
            output += line

    proc.wait()
    if proc.returncode and raise_error:
        raise subprocess.CalledProcessError(proc.returncode, cmd)

    return proc.returncode, output


def check(cmd, user='root', raise_error=True):
    """
    Run a bash command as the given user.

    Raises an error on a non zero exit code by default.

    """
    code, _ = _shell(cmd, user=user, raise_error=raise_error)
    return code


def check_output(cmd, user='root'):
    """
    Run a bash command as the given user. Return the output as a
    string.

    Raises an error on a non zero exit code.

    """
    _, out = _shell(cmd, user=user, raise_error=True, save_out=True)
    return out
