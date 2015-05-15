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

from onmetal_scripts.lib import agent_client
from onmetal_scripts.lib import script

import json


class RunCleanStep(script.TeethScript):
    def __init__(self):
        super(RunCleanStep, self).__init__(
                'Utility for running a clean step on a single agent')
        self.add_argument('--ip',
                help=('IP Address of agent to run clean step against'))
        self.add_argument('--flavor',
                help=('OnMetal flavor node object should emulate'),
                choices=['onmetal-io1', 'onmetal-compute1', 'onmetal-memory1'])
        self.add_argument('step',
                help=('Name of clean step to run'))

    def _create_node(self):
        """Creates a node object suitable for most agent cleaning steps."""
        flavor = self.get_argument('flavor', required=True)
        ip = self.get_argument('ip', required=True)
        flavors = {
                   'onmetal-io1': {
                       'memory': 131072,
                       'cpus': 40},
                   'onmetal-compute1': {
                       'memory': 32768,
                       'cpus': 20},
                   'onmetal-memory1': {
                       'memory': 524288,
                       'cpus': 24}
                  }
        memory = flavors[flavor]['memory']
        cpus = flavors[flavor]['cpus']
        agent_url = 'http://%s:9999' % ip
        return {
                'properties': {
                    'memory_mb': memory,
                    'cpu_arch': "amd64",
                    'local_gb': 32,
                    'cpus': cpus
                },
                'driver_info': {
                    'agent_url': agent_url
                }}

    def run(self):
        node = self._create_node()
        step = self.get_argument('step', required=True)
        method = 'decom.decommission'
        params = {'node': node,
                  'ports': [],
                  'decommission_target_state': step}
        ac = agent_client.AgentClient()
        print(json.dumps(ac._command(node, method, params, True), indent=2))

if __name__ == "__main__":
    RunCleanStep().run()
