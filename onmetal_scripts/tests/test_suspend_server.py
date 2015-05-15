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

from onmetal_scripts import suspend_server
from onmetal_scripts.tests import base

import mock


class TestSuspend(base.BaseTest):
    def setUp(self):
        self.script = suspend_server.SuspendServer()

    def test__get_node_uuid(self):
        test_node = self._get_test_node(
            instance_uuid='118ad976-084a-443f-9ec5-77d477f2bfcc')

        self.script.get_argument = mock.Mock()
        self.script.get_argument.return_value = test_node['uuid']

        self.assertEqual(test_node['uuid'], self.script._get_node_uuid())

    @mock.patch('onmetal_scripts.suspend_server.SuspendServer.ironic_client')
    def test__get_node_uuid_instance(self, client_mock):
        test_node = self._get_test_node(
            instance_uuid='118ad976-084a-443f-9ec5-77d477f2bfcc')

        self.script.get_argument = mock.Mock()
        self.script.get_argument.side_effect = [AttributeError,
                                                test_node['instance_uuid']]

        client_mock.get_node_by_instance.return_value = test_node

        self.assertEqual(test_node['uuid'], self.script._get_node_uuid())

    def test__get_node_uuid_fail(self):
        self.script.get_argument = mock.Mock()
        self.script.get_argument.side_effect = [AttributeError,
                                                AttributeError]

        self.assertRaises(AttributeError, self.script._get_node_uuid)

    @mock.patch('onmetal_scripts.suspend_server.SuspendServer.neutron_client')
    @mock.patch('onmetal_scripts.suspend_server.SuspendServer.ironic_client')
    @mock.patch('onmetal_scripts.suspend_server.SuspendServer._get_node_uuid')
    def test_run_suspend(self, uuid_mock, client_mock, neutron_mock):
        test_node = self._get_test_node(
            instance_uuid='118ad976-084a-443f-9ec5-77d477f2bfcc')

        uuid_mock.return_value = test_node['uuid']
        client_mock.get_node.return_value = test_node

        self.script.get_argument = mock.Mock()
        self.script.get_argument.return_value = 'suspend'

        self.script.run()

        neutron_mock.suspend_node.assert_called_once_with(test_node)

    @mock.patch('onmetal_scripts.suspend_server.SuspendServer.neutron_client')
    @mock.patch('onmetal_scripts.suspend_server.SuspendServer.ironic_client')
    @mock.patch('onmetal_scripts.suspend_server.SuspendServer._get_node_uuid')
    def test_run_unsuspend(self, uuid_mock, client_mock, neutron_mock):
        test_node = self._get_test_node(
            instance_uuid='118ad976-084a-443f-9ec5-77d477f2bfcc')

        uuid_mock.return_value = test_node['uuid']
        client_mock.get_node.return_value = test_node

        self.script.get_argument = mock.Mock()
        self.script.get_argument.return_value = 'unsuspend'

        self.script.run()

        neutron_mock.unsuspend_node.assert_called_once_with(test_node)
