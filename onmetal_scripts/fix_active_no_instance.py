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

import logging

from lib import script
from lib import states

"""
This script will take nodes that are active but don't have an instance
assigned to them and tear down them down, then decommission them.

Nodes can get in this state due to bugs in Nova resulting from running
HA nova-computes. Nodes can get rescheduled, but have already attempted
a provision on Ironic. Ironic will continue, but never get an instance
UUID, which means the node doesn't have a customer on it.
"""

logger = logging.getLogger(__name__)


class FixActiveNoInstance(script.TeethScript):
    use_ironic = True

    def __init__(self):
        super(FixActiveNoInstance, self).__init__(
            'Utility for fixing nodes that are active without an instance'
            'UUID.')

    def _is_active_no_instance(self, node):
        return (node['instance_uuid'] is None
                and node['provision_state'] == states.ACTIVE)

    def _reverify(self, node):
        # Returns True if node is still active no instance, False otherwise
        node = self.ironic_client.get_node(node['uuid'])
        if not self._is_active_no_instance(node):
            logger.error(
                'Node {uuid} in unexpected state: instance_uuid: '
                '{instance_uuid}; provision_state: '
                '{provision_state}.'.format(**node))
            return False
        return True

    def run(self):
        nodes = self.ironic_client.list_nodes()
        for node in nodes:
            if self._is_active_no_instance(node):
                if not self._reverify(node):
                    continue
                self.ironic_client.set_target_state(node, states.DELETED)

if __name__ == "__main__":
    FixActiveNoInstance().run()
