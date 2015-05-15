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
from onmetal_scripts.lib import utils


class MaintenanceMode(script.TeethScript):
    use_ironic = True

    def __init__(self):

        self.default_snapshot_filename = '~/onmetal_maintenance_snapshot.json'

        super(MaintenanceMode, self).__init__(
            'Utility for putting groups of nodes into maintenance mode.')
        self.add_ironic_node_or_instance_uuid_arguments()
        self.add_argument('--cab',
                          help=('Run against all nodes in a cab '
                                '(ex: f4-22-[1,2].iad3).'))
        self.add_argument('--file',
                          help=('Location for saving/reading snapshot '
                                'of maintenance state. Defaults to %s' %
                                self.default_snapshot_filename))
        self.add_argument('--overwrite_snapshot', action='store_true',
                          help=('Allow the script to overwrite an existing '
                                'snapshot file when putting nodes in '
                                'maintenance.'))
        self.add_argument('--no_snapshot', action='store_true',
                          help=('Do not take or read a snapshot of '
                                'the current node(s) maintenance state.'))
        self.add_argument('--reason',
                          help='Maintenance reason to set on node(s).',
                          required=True)
        self.add_argument('command',
                          help='Run command.',
                          default='Maintenance Mode Script',
                          choices=['maintenance', 'unmaintenance',
                                   'snapshot', 'show'])

    def _get_nodes(self):

        # We can operate on a single node or entire cab, so make sure
        # we only do one or the other here.
        node_uuid = self.get_argument('node_uuid', required=False)
        instance_uuid = self.get_argument('instance_uuid', required=False)
        cab = self.get_argument('cab', required=False)

        if node_uuid and instance_uuid:
            raise Exception(
                'Cannot specify both node_uuid and instance_uuid.')
        if not (node_uuid or instance_uuid) and not cab:
            raise Exception(
                'Must specify either node_uuid/instance_uuid OR cab.')
        if (node_uuid or instance_uuid) and cab:
            raise Exception(
                'Cannot specify both node_uuid/instance_uuid and cab.')

        nodes = []
        if node_uuid:
            nodes = [self.ironic_client.get_node(node_uuid)]
        if instance_uuid:
            nodes = [self.ironic_client.get_node_by_instance(instance_uuid)]
        if cab:
            nodes = self.ironic_client.list_nodes_by_cab(cab)

        return nodes

    def _set_maintenance(self, nodes, new_mode):

        for node in nodes:

            current_mode = node['maintenance']
            current_reason = node['maintenance_reason']
            reason = self.get_argument('reason')

            # If the node is already in the desired state, we can skip it.
            if current_mode == new_mode:
                print('Maintenance mode for node %s already in desired mode: '
                      '%s' % (node['uuid'], new_mode))
                continue

            # If the node was maintenanced in the snapshot and we are trying to
            # unmaintenance it, we skip it.
            if new_mode is False and current_reason != reason:
                print('Node %(node)s was previously maintenanced, with reason'
                      '%(reason)s skipping unmaintenance.' %
                      {'node': node['uuid'], 'reason': current_reason})
                continue

            # Otherwise, set it
            try:
                print('Setting maintenance mode for node %s: '
                      'current_mode: %s new_mode: %s' % (node['uuid'],
                                                         current_mode,
                                                         new_mode))
                self.ironic_client.set_maintenance(node, str(new_mode), reason)
            except Exception as e:
                # We will get locked nodes sometimes, so don't choke
                print(e)

    def run(self):

        nodes = self._get_nodes()
        print('Found %s nodes' % len(nodes))

        if self.get_argument('command') == 'show':
            for node in nodes:
                port_info = utils.get_port_info(node)
                print('uuid: %s cab0: %s cab1: %s maintenance: %s'
                      % (node['uuid'], port_info['cab0'],
                         port_info['cab1'], node['maintenance']))

        elif self.get_argument('command') == 'maintenance':
            self._set_maintenance(nodes, True)

        elif self.get_argument('command') == 'unmaintenance':
            self._set_maintenance(nodes, False)


if __name__ == "__main__":
    MaintenanceMode().run()
