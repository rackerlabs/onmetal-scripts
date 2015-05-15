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


class SuspendServer(script.TeethScript):
    use_ironic = True
    use_neutron = True

    def __init__(self):
        super(SuspendServer, self).__init__(
            'Utility for temporarily cutting network access to a node.')
        self.add_ironic_node_or_instance_uuid_arguments()
        self.add_argument('command',
                          help='Run command.',
                          choices=['suspend', 'unsuspend'])

    def _get_node_uuid(self):
        # Convert instance uuid to node uuid if necessary
        try:
            uuid = self.get_argument('node_uuid')
        except AttributeError:
            try:
                instance_uuid = self.get_argument('instance_uuid')
            except AttributeError:
                raise AttributeError(
                    'Must specify either a node uuid or an instance uuid')
            uuid = self.ironic_client.get_node_by_instance(
                instance_uuid)['uuid']
        return uuid

    def run(self):
        uuid = self._get_node_uuid()
        node = self.ironic_client.get_node(uuid)

        if self.get_argument('command') == 'suspend':
            self.neutron_client.suspend_node(node)
        elif self.get_argument('command') == 'unsuspend':
            self.neutron_client.unsuspend_node(node)


if __name__ == "__main__":
    SuspendServer().run()
