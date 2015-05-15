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

from onmetal_scripts import fix_noheartbeat
from onmetal_scripts.lib import ipmi
from onmetal_scripts.lib import states
from onmetal_scripts.tests import base

import mock


class TestFixNoHeartbeat(base.BaseTest):
    def setUp(self):
        self.script = fix_noheartbeat.FixNoHeartbeat()

    @mock.patch('time.time')
    def test__get_no_heartbeat_nodes_false(self, time_mock):
        self.script.get_argument = mock.Mock()
        self.script.get_argument.return_value = 1000

        time_mock.return_value = 1400001001.000000

        # Only 1 second since heartbeat
        under_heartbeat_node = self._get_test_node(
            driver_internal_info={'agent_last_heartbeat': 1400001000.000000},
            provision_state=states.CLEANING)

        # Only 1 second since provision_state update
        under_provision_node = self._get_test_node(
            provision_updated_at=u'2014-05-13T17:10:00+00:00',
            provision_state=states.CLEANING)

        maintenance_node = self._get_test_node(
            maintenance=True,
            provision_state=states.CLEANING)

        locked_node = self._get_test_node(
            reservation='conductor1',
            provision_state=states.CLEANING)

        for node in (under_heartbeat_node, under_provision_node,
                     maintenance_node, locked_node):
            self.assertFalse(self.script._is_no_heartbeat(node))

    @mock.patch('time.time')
    def test__get_no_heartbeat_nodes_true(self, time_mock):
        self.script.get_argument = mock.Mock()
        self.script.get_argument.return_value = 1000

        time_mock.return_value = 1400001001.000000

        no_hb_inactive = self._get_test_node(
            driver_internal_info={'agent_last_heartbeat': 1400000000.000000},
            provision_state=states.AVAILABLE)

        no_hb_cleaning = self._get_test_node(
            driver_internal_info={'agent_last_heartbeat': 1400000000.000000},
            provision_updated_at=u'2014-05-13T17:09:00+00:00',
            provision_state=states.CLEANING)

        for node in (no_hb_inactive, no_hb_cleaning):
            self.assertTrue(self.script._is_no_heartbeat(node))

    @mock.patch('onmetal_scripts.fix_noheartbeat.FixNoHeartbeat.'
                'ipmi_client')
    @mock.patch('onmetal_scripts.fix_noheartbeat.FixNoHeartbeat.'
                'neutron_client')
    @mock.patch('onmetal_scripts.fix_noheartbeat.FixNoHeartbeat.'
                'ironic_client')
    def test_run(self, ironic_client, neutron_client, ipmi_client):
        self.script.get_argument = mock.Mock()
        self.script.get_argument.side_effect = [True, 'password']

        no_hb_node = self._get_test_node(
            driver_info={'agent_last_heartbeat': 1400000000.000000},
            provision_state=states.AVAILABLE)

        hb_node = self._get_test_node(
            driver_info={'agent_last_heartbeat': 1400001000.000000},
            provision_state=states.CLEANING)

        self.script._get_no_heartbeat_nodes = mock.Mock()
        self.script._get_no_heartbeat_nodes.return_value = [
            no_hb_node, hb_node]

        ironic_client.get_node.side_effect = [no_hb_node, hb_node]

        self.script._is_no_heartbeat = mock.Mock()
        self.script._is_no_heartbeat.side_effect = [True, False]

        self.script.run()

        ironic_client.set_mainteance.assert_has_calls = [
            mock.call(no_hb_node, "True"),
            mock.call(no_hb_node, "False")
        ]

        neutron_client.delete_ports_for_node.assert_called_once_with(
            no_hb_node)
        neutron_client.add_decom_port.assert_called_once_with(no_hb_node)

        ipmi_client.force_reboot.assert_called_once_with(
            no_hb_node, ipmi.IPMIBootDev.PXE, 'password')
