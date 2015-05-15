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

import time

from lib import script
from lib import states

"""
Reboots all nodes that are considered 'inactive', which means no instance
assigned to them, running
"""


class RebootUnprovisioned(script.TeethScript):
    use_ironic = True

    def __init__(self):
        super(RebootUnprovisioned, self).__init__(
            'Utility for rebooting inactive nodes.')
        self.add_argument('--sleep',
                          type=int,
                          default=10,
                          required=False,
                          help='Amount of time in seconds to sleep between '
                               'reboots. Defaults to 10.')

    def _is_inactive(self, node):
        return (
            node['instance_uuid'] is None and
            node['maintenance'] is False and
            node['provision_state'] in (states.AVAILABLE,
                                        states.MANAGEABLE)
        )

    def run(self):
        for node in self.ironic_client.list_nodes():
            if self._is_inactive(node):
                try:
                    self.ironic_client.set_target_power_state(
                        node, states.REBOOT)
                    print('Rebooted {uuid}'.format(**node))
                except Exception:
                    print('Failed to reboot {uuid}'.format(**node))
                # Artificially slow this down to avoid overloading conductors
                # or dropping capacity too fast
                time.sleep(self.get_argument('sleep'))


if __name__ == "__main__":
    RebootUnprovisioned().run()
