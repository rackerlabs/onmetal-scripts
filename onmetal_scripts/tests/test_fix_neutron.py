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

from onmetal_scripts import fix_neutron_failed
from onmetal_scripts.lib import states
from onmetal_scripts.tests import base

import mock


error_messages = [
    'Tear down failed: update_port_postcommit failed.',

    'Tear down failed: create_port_postcommit failed.',

    'exception: Port 118ad976-084a-443f-9ec5-77d477f2bfcc could not be found',

    'Tear down failed: Could not remove public network '
    '118ad976-084a-443f-9ec5-77d477f2bfcc from '
    '218ad976-084a-443f-9ec5-77d477f2bfcc, possible network issue',

    'Tear down failed: <html><body><h1>502 Bad Gateway</h1>\nThe server '
    'returned an invalid or incomplete response.\n</body></html>\n\n',

    'Tear down failed: <html><body><h1>504 Gateway Time-out</h1>\nThe server '
    'didn\'t respond in time.\n</body></html>\n\n'
]


class TestFixNeutronFailed(base.BaseTest):
    def setUp(self):
        self.script = fix_neutron_failed.FixNeutronFailed()

    def test__should_redelete(self):
        for message in error_messages:
            test_node = self._get_test_node(
                provision_state=states.CLEANFAIL,
                instance_uuid=None,
                last_error=message)
            self.assertTrue(self.script._should_redelete(test_node))

        test_node = self._get_test_node(
            provision_state=states.CLEANFAIL,
            instance_uuid=None,
            last_error=None)

        self.assertFalse(self.script._should_redelete(test_node))

    @mock.patch('onmetal_scripts.fix_neutron_failed.FixNeutronFailed.'
                'ironic_client')
    def test_run(self, ironic_mock):
        test_node = self._get_test_node(
            provision_state=states.CLEANFAIL,
            instance_uuid=None,
            last_error=error_messages[0])

        ironic_mock.list_nodes.return_value = [test_node]

        self.script.run()

        ironic_mock.set_target_state.has_calls([
            mock.call(test_node, states.VERBS['manage']),
            mock.call(test_node, states.VERBS['provide'])])
