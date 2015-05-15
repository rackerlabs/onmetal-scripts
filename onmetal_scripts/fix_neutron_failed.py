#!/usr/bin/env python

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

from onmetal_scripts.lib import script
from onmetal_scripts.lib import states

import re

"""
This script will take nodes in a known failed state and put them through a
a tear down and decommission.

Right now, the script only works for nodes that failed to remove the customer
network and/or failed to add the decom network during tear down, which would
happen if Neutron couldn't access the switches or there was a temporary
network failure of some kind.

IAD usage: IRONIC_URL='http://ironic-api-vip.m0001.iad.ohthree.com:6385/v1' \
           OS_AUTH_TOKEN=lol python redelete.py
"""


class FixNeutronFailed(script.TeethScript):
    use_ironic = True
    use_neutron = True

    def __init__(self):
        super(FixNeutronFailed, self).__init__(
            'Utility for fixing nodes in a neutron failed state.')

    def _should_redelete(self, node):
        """Returns True if the node should be redeleted, False otherwise."""
        return (
            node['provision_state'] in (states.DEPLOYFAIL,
                                        states.CLEANFAIL) and
            node['instance_uuid'] is None and
            node['last_error'] is not None and
            (re.search(
                r'Tear down failed: (create|update)_port_postcommit failed.',
                node['last_error']) or
             re.search(
                 r'exception: Port [A-Za-z0-9\-]+ could not be found',
                 node['last_error']) or
             re.search(
                 'Tear down failed: Could not remove public network '
                 '[0-9A-Fa-f-]{36} from [0-9A-Fa-f-]{36}, '
                 'possible network issue',
                 node['last_error']) or
             node['last_error'] == (
                 'Tear down failed: <html><body><h1>502 Bad '
                 'Gateway</h1>\nThe server returned an '
                 'invalid or incomplete response.\n</body>'
                 '</html>\n\n') or
             node['last_error'] == (
                 'Tear down failed: <html><body><h1>504 '
                 'Gateway Time-out</h1>\nThe server '
                 'didn\'t respond in time.\n</body></html>\n\n')
            )
        )

    def run(self):
        nodes = self.ironic_client.list_nodes()
        for node in nodes:
            if self._should_redelete(node):
                if node['provision_state'] == states.DEPLOYFAIL:
                    self.ironic_client.set_target_state(node, states.DELETED)
                elif node['provision_state'] == states.CLEANFAIL:
                    self.ironic_client.set_target_state(
                        node, states.VERBS['manage'])
                    self.ironic_client.set_target_state(
                        node, states.VERBS['provide'])


if __name__ == "__main__":
    FixNeutronFailed().run()
