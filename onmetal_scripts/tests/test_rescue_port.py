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

from onmetal_scripts import rescue_port
from onmetal_scripts.tests import base

import mock


class TestRescuePort(base.BaseTest):
    def setUp(self):
        self.script = rescue_port.RescuePort()

    @mock.patch('onmetal_scripts.rescue_port.RescuePort.neutron_client')
    @mock.patch('onmetal_scripts.rescue_port.RescuePort.ironic_client')
    def test_run_add(self, mock_ironic, mock_neutron):
        test_node = self._get_test_node()
        self.script.get_argument = mock.Mock()
        self.script.get_argument.side_effect = [test_node['uuid'], 'add']
        mock_ironic.get_node.return_value = test_node

        self.script.run()

        mock_neutron.add_rescue_port.assert_called_with(test_node)

    @mock.patch('onmetal_scripts.rescue_port.RescuePort.neutron_client')
    @mock.patch('onmetal_scripts.rescue_port.RescuePort.ironic_client')
    def test_run_remove(self, mock_ironic, mock_neutron):
        test_node = self._get_test_node()
        self.script.get_argument = mock.Mock()
        self.script.get_argument.side_effect = [test_node['uuid'], 'remove']
        mock_ironic.get_node.return_value = test_node

        self.script.run()

        mock_neutron.remove_rescue_port.assert_called_with(test_node)
