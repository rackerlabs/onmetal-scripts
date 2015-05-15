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

from onmetal_scripts import fix_active_no_instance
from onmetal_scripts.lib import states
from onmetal_scripts.tests import base

import mock


class TestActiveNoInstance(base.BaseTest):
    def setUp(self):
        self.script = fix_active_no_instance.FixActiveNoInstance()

    @mock.patch('onmetal_scripts.fix_active_no_instance.FixActiveNoInstance.'
                'ironic_client')
    def test__reverify(self, client_mock):
        test_node = self._get_test_node(
            instance_uuid=None,
            provision_state=states.ACTIVE)
        client_mock.get_node.return_value = test_node
        self.assertTrue(self.script._reverify(test_node))

    @mock.patch('onmetal_scripts.fix_active_no_instance.FixActiveNoInstance.'
                'ironic_client')
    def test__reverify_fail(self, client_mock):
        test_node = self._get_test_node(
            instance_uuid=None,
            provision_state=states.AVAILABLE)
        client_mock.get_node.return_value = test_node
        self.assertFalse(self.script._reverify(test_node))

    @mock.patch('onmetal_scripts.fix_active_no_instance.FixActiveNoInstance.'
                'ironic_client')
    def test_run(self, client_mock):
        anomalous_node = self._get_test_node(
            instance_uuid=None,
            provision_state=states.ACTIVE)
        inactive_node = self._get_test_node(
            instance_uuid=None,
            provision_state=states.AVAILABLE,
            uuid='6dd10677-07b1-4cf1-847e-2cb55f0c657a')

        client_mock.list_nodes.return_value = [anomalous_node, inactive_node]
        client_mock.get_node.side_effect = [anomalous_node, inactive_node]

        self.script.run()

        client_mock.set_target_state.assert_called_once_with(
            anomalous_node, states.DELETED)

    @mock.patch('onmetal_scripts.fix_active_no_instance.FixActiveNoInstance.'
                'ironic_client')
    def test_run_fail_reverify(self, client_mock):
        anomalous_node = self._get_test_node(
            instance_uuid=None,
            provision_state=states.ACTIVE)
        # Same node, but with a fixed state
        fixed_node = self._get_test_node(
            instance_uuid=None,
            provision_state=states.AVAILABLE)

        client_mock.list_nodes.return_value = [anomalous_node]
        client_mock.get_node.side_effect = [fixed_node]

        self.script.run()

        self.assertFalse(client_mock.set_target_state.called)
