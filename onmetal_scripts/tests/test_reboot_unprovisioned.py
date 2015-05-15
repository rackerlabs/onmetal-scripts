# Copyright 2015 Rackspace, Inc
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from onmetal_scripts.lib import states
from onmetal_scripts import reboot_unprovisioned
from onmetal_scripts.tests import base

import mock


class TestRebootUnprovisioned(base.BaseTest):
    def setUp(self):
        self.script = reboot_unprovisioned.RebootUnprovisioned()
        self.script.get_argument = mock.Mock()
        self.script.get_argument.return_value = 0

    @mock.patch('onmetal_scripts.reboot_unprovisioned.RebootUnprovisioned.'
                'ironic_client')
    def test_run(self, ironic_mock):
        active_node = self._get_test_node(
            provision_state=states.ACTIVE,
            instance_uuid='118ad976-084a-443f-9ec5-77d477f2bfcc')
        inactive_node = self._get_test_node(
            provision_state=states.AVAILABLE,
            instance_uuid=None,
            maintenance=False)

        ironic_mock.list_nodes.return_value = [active_node, inactive_node]

        self.script.run()

        ironic_mock.set_target_power_state.assert_called_once_with(
            inactive_node, states.REBOOT)

    @mock.patch('onmetal_scripts.reboot_unprovisioned.RebootUnprovisioned.'
                'ironic_client')
    def test_run_fail(self, ironic_mock):
        inactive_node = self._get_test_node(
            provision_state=states.AVAILABLE,
            instance_uuid=None,
            maintenance=False)

        ironic_mock.list_nodes.return_value = [inactive_node]
        ironic_mock.set_target_power_state.side_effect = ValueError

        self.script.run()

        ironic_mock.set_target_power_state.assert_called_once_with(
            inactive_node, states.REBOOT)
