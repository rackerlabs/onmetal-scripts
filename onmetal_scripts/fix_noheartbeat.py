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

from onmetal_scripts.lib import ipmi
from onmetal_scripts.lib import script
from onmetal_scripts.lib import states

import datetime
import re
import socket
import time
import traceback

"""
Fixes nodes in a no heartbeat state.

1. Set maintenance mode
2. Remove instance ports
3. Add decom ports
4. Put into decom, decom_target_state none
5. Fix bmc force boot agent
6. Unmaintenance (release lock)

This will leave nodes in maintenance mode should anything fail.
"""


class FixNoHeartbeat(script.TeethScript):
    use_ironic = True
    use_neutron = True
    use_ipmi = True

    def __init__(self):
        super(FixNoHeartbeat, self).__init__(
            'Utility for fixing nodes in a neutron failed state.')

        self.add_argument('--force', action='store_true',
                          help='Do not sanity-check environment first.')
        self.add_argument('--time_since_heartbeat', default=3600)
        self.add_argument('--ipmi_password', default=None)

    def _dt_to_ut(self, t):
        # Ugly, but python timezone handling is crappy in this case
        return datetime.datetime.strptime(t.replace("+00:00", ""),
                                          "%Y-%m-%dT%H:%M:%S")

    def _time_since(self, t):
        # T can be a datetime string or a timestamp
        if isinstance(t, basestring):
            return (datetime.datetime.now() -
                    self._dt_to_ut(t)).total_seconds()
        else:
            return time.time() - t

    def _is_no_heartbeat(self, ironic_node):
        timeout = self.get_argument('time_since_heartbeat')
        time_since_heartbeat = self._time_since(
            ironic_node['driver_internal_info'].get('agent_last_heartbeat', 0))
        time_since_prov = self._time_since(
            ironic_node['provision_updated_at'] or 0)
        if (ironic_node['maintenance'] is True and
                ironic_node['maintenance_reason'] != 'NoHeartbeat'):
            return False

        if ironic_node['reservation']:
            return False

        return ((time_since_heartbeat > timeout and
                 ironic_node['provision_state'] == states.AVAILABLE) or
                (time_since_heartbeat > timeout and
                 ironic_node['provision_state'] == states.CLEANING and
                 time_since_prov > timeout))

    def _get_no_heartbeat_nodes(self):
        print("getting nodes that are not heartbeating...")
        return [node for node in self.ironic_client.list_nodes() if
                self._is_no_heartbeat(node)]

    def _format_node(self, node):
        node_info = {
            'uuid': node['uuid'],
            'last_hb': self._time_since(node['driver_info'].get(
                'agent_last_heartbeat', 0)),
            'reservation': node['reservation'],
            'prov_state': node['provision_state'],
            'decom_step': node['driver_info'].get('decommission_target_state'),
            'bmc_ip': node['driver_info'].get('ipmi_address')
        }

        return ("{uuid} agent_last_heartbeat: {last_hb} reservation: "
                "{reservation} provision_state: {prov_state} "
                "decom step: {decom_step} bmc ip: {bmc_ip}".format(
                    **node_info))

    def _dry_run(self):
        nodes = self._get_no_heartbeat_nodes()
        print("dry_run is set. Would execute on the following nodes:")
        for node in nodes:
            print(self._format_node(node))

    def run(self):

        if not self.get_argument('force'):
            if not re.search(r'conductor', socket.gethostname()):
                raise EnvironmentError(
                    'This script must be run on a conductor')

        ipmi_password = self.get_argument('ipmi_password', check_env=True)

        for node in self._get_no_heartbeat_nodes():

            print("fixing node: {}".format(self._format_node(node)))
            try:
                # Get node again and reverify to avoid some race
                node = self.ironic_client.get_node(node['uuid'])
                if not self._is_no_heartbeat(node):
                    print(
                        "node {} is no longer in a no heartbeat state, "
                        "skipping".format(
                            node['uuid']))
                    continue

                # maintenance the node, we filter only unmaintenanced nodes
                # so this acts a a lock as well as
                # protects us should this fail halfway
                self.ironic_client.set_maintenance(node, "True", 'NoHeartbeat')

                # remove any existing neutron ports, and add decom ports
                self.neutron_client.delete_ports_for_node(node)
                self.neutron_client.add_decom_port(node)

                # force reboot the node and boot from PXE
                self.ipmi_client.force_reboot(node, ipmi.IPMIBootDev.PXE,
                                              ipmi_password)

                # unmaintenance the now fixed node
                self.ironic_client.set_maintenance(node, "False")

            except Exception as e:
                print(traceback.print_exc())
                raise Exception(
                    "node {} failed to be reset because: {}. Exiting".format(
                        node.get('uuid'), str(e)))
            else:
                print("node {} successfully fixed.".format(node['uuid']))


if __name__ == "__main__":
    FixNoHeartbeat().run()
