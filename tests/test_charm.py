# Copyright 2020 Pete Vander Giessen
# See LICENSE file for licensing details.

import unittest

from unittest.mock import patch, Mock

from ops.testing import Harness
from charm import Microk8STestCharm


EXAMPLE_STATUS = """
Model    Controller   Cloud/Region   Version  SLA          Timestamp
testbed  aws-testbed  aws/us-east-1  2.8.6    unsupported  19:21:47-05:00

App            Version  Status  Scale  Charm          Store  Rev  OS      Message
microk8s-test           active      1  microk8s-test  local    0  ubuntu  Ready.

Unit              Workload  Agent  Machine  Public address  Ports  Message
microk8s-test/0*  active    idle   0        184.73.80.35           Ready.

Machine  State    DNS           Inst id              Series  AZ          Message
0        started  184.73.80.35  i-0cb1ea098314d2805  focal   us-east-1a  running
"""


class TestCharm(unittest.TestCase):
    def test_config(self):
        harness = Harness(Microk8STestCharm)
        self.addCleanup(harness.cleanup)
        harness.begin()
        self.assertEqual(harness.charm._stored.cloud_user, "ubuntu")

    @patch('charm.shell')
    def test_install(self, mock_shell):
        harness = Harness(Microk8STestCharm)
        self.addCleanup(harness.cleanup)
        harness.begin_with_initial_hooks()
        mock_shell.assert_called_with('juju models', user='ubuntu')

    @patch('charm.shell')
    def test_action(self, mock_shell):
        harness = Harness(Microk8STestCharm)
        harness.begin()
        action_event = Mock(params={})
        mock_shell.return_value = EXAMPLE_STATUS

        harness.charm._on_status_action(action_event)

        self.assertTrue(action_event.set_results.called)
        action_event.set_results.assert_called_with({'juju_status': EXAMPLE_STATUS})


if __name__ == '__main__':
    unittest.main()
