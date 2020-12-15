#!/usr/bin/env python3
# Copyright 2020 Canonical Ltd.
# See LICENSE file for licensing details.

import logging

from ops.charm import CharmBase
from ops.main import main
from ops.model import ActiveStatus, MaintenanceStatus
from ops.framework import StoredState

from shell import check, check_output

logger = logging.getLogger('charm')


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

        if 'microk8s' in check_output('snap list'):
            return

        # Install and check microk8s
        self.unit.status = MaintenanceStatus('Installing microk8s.')
        check('snap install microk8s --classic')
        check('usermod -a -G microk8s {}'.format(user))
        check('microk8s status --wait-ready', user=user)
        check('microk8s.kubectl get all --all-namespaces', user=user)

        # Enable components
        self.unit.status = MaintenanceStatus('Enabling microk8s components.')
        check('microk8s.enable dns storage', user=self.config['cloud_user'])

    def _ensure_juju(self):
        """
        Ensure that juju is installed.

        TODO: make this more robust and able to recover from a
        mid-process crash.

        """
        user = self._stored.cloud_user

        if 'juju' in check_output('snap list'):
            return

        # Bootstrap and add a model.
        self.unit.status = MaintenanceStatus('Bootstrapping Juju.')
        check('snap install juju --classic')
        check('juju bootstrap microk8s micro', user=user)
        check('juju add-model testing', user=user)

    def _on_start(self, event):
        """
        Make sure that we have snaps installed, and that we can talk to
        our Juju model.

        """
        user = self._stored.cloud_user

        logger.debug('Running "on start" action.')

        self._ensure_microk8s()
        self._ensure_juju()

        # Final output
        check('juju models', user=user)
        self.unit.status = ActiveStatus('Ready.')

    def _on_status_action(self, event):
        """
        Add a juju status action.

        """
        logger.debug('Running juju status.')

        user = self._stored.cloud_user
        out = check_output('juju status', user=user)
        event.set_results({"juju_status": out})


if __name__ == "__main__":
    main(Microk8STestCharm)
