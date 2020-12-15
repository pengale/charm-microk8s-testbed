#!/usr/bin/env python3
# Copyright 2020 Canonical Ltd.
# See LICENSE file for licensing details.

import logging
import shlex
import subprocess
import os

from ops.charm import CharmBase
from ops.main import main
from ops.model import ActiveStatus, MaintenanceStatus
from ops.framework import StoredState

logger = logging.getLogger(__name__)


def shell(cmd, user='root', save_out=False):
    """Run a shell command, piping STDOUT and STDERR to our logger.

    :param cmd: string to be composed into the bash call.
    :param user: run the command as this user. Defaults to root.
    :param save_out: save and return output. Warning: this can get large.
        Use with caution!

    Logs STDOUT and STDERR to Juju debug log. Raises an error if the
    command returns a non zero exit code.

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
    if proc.returncode:
        raise subprocess.CalledProcessError(proc.returncode, cmd)

    return output  # Returns empty string if save_out not set.


def is_installed(snap_name):
    """
    Check to see if a given snap is installed.

    :param name: Name of the snap.

    """
    return snap_name in shell('snap list', save_out=True)


class Microk8STestCharm(CharmBase):
    _stored = StoredState()

    def __init__(self, *args):
        super().__init__(*args)
        self._stored.cloud_user = self.config['cloud_user']
        self.framework.observe(self.on.start, self._on_start)
        self.framework.observe(self.on.status_action, self._on_status_action)

    def _ensure_microk8s(self):
        """
        Ensure that microk8s is installed.

        TODO: make this more robust and able to recover from a
        mid-process crash.

        """
        user = self._stored.cloud_user

        if is_installed('microk8s'):
            return

        # Install and shell microk8s
        self.unit.status = MaintenanceStatus('Installing microk8s.')
        shell('snap install microk8s --classic')
        shell('usermod -a -G microk8s {}'.format(user))
        shell('microk8s status --wait-ready', user=user)
        shell('microk8s.kubectl get all --all-namespaces', user=user)

        # Enable components
        self.unit.status = MaintenanceStatus('Enabling microk8s components.')
        shell('microk8s.enable dns storage', user=self.config['cloud_user'])

    def _ensure_juju(self):
        """
        Ensure that juju is installed.

        TODO: make this more robust and able to recover from a
        mid-process crash.

        """
        user = self._stored.cloud_user

        if is_installed('juju'):
            return

        # Bootstrap and add a model.
        self.unit.status = MaintenanceStatus('Bootstrapping Juju.')
        shell('snap install juju --classic')
        shell('juju bootstrap microk8s micro', user=user)
        shell('juju add-model testing', user=user)

    def _on_start(self, event):
        """
        Make sure that we have snaps installed, and that we can talk to
        our Juju model.

        """
        user = self._stored.cloud_user

        self._ensure_microk8s()
        self._ensure_juju()

        # Final output
        shell('juju models', user=user)
        self.unit.status = ActiveStatus('Ready.')

    def _on_status_action(self, event):
        """
        Add a juju status action.

        """
        user = self._stored.cloud_user
        out = shell('juju status', user=user, save_out=True)
        event.set_results({"juju_status": out})


if __name__ == "__main__":
    main(Microk8STestCharm)
