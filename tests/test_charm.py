# Copyright 2020 Pete Vander Giessen
# See LICENSE file for licensing details.

import unittest

from unittest.mock import patch

from ops.testing import Harness
from charm import Microk8STestCharm


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


if __name__ == '__main__':
    unittest.main()
