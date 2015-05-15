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

import copy
import unittest


test_node = {
    u'instance_uuid': None,
    u'target_power_state': None,
    u'links': [
        {
            u'href':
                u'http://ironic-api-vip.m0002.preprod-ord.ohthree.com'
                u':6385/v1/nodes/04522204-d787-4e8e-b19f-18cfc2457412',
            u'rel': u'self'
        },
        {
            u'href':
                u'http://ironic-api-vip.m0002.preprod-ord.ohthree.com'
                u':6385/nodes/04522204-d787-4e8e-b19f-18cfc2457412',
            u'rel': u'bookmark'
        }
    ],
    u'uuid': u'04522204-d787-4e8e-b19f-18cfc2457412',
    u'driver_info': {u'ipmi_address': u'10.255.0.2'},
    u'driver_internal_info': {
        u'agent_url': u'http://10.1.0.2:9999',
        u'hardware_manager_version': None,
        u'ipmi_address': u'10.255.0.2',
        u'decommission_target_state': None,
        u'agent_last_heartbeat': 1419889938},
    u'target_provision_state': None, u'last_error': None,
    u'console_enabled': False,
    u'extra': {
        u'hardware/interfaces/0/switch_port_id': u'Eth1/1',
        u'rackid': u'RACKID01',
        u'hardware/interfaces/1/switch_chassis_id': u'c1-11-2.ord1',
        u'core_id': 565445,
        u'uutsn': u'UUTSN01',
        u'racklocation': u'M01',
        u'hardware/interfaces/1/switch_port_id': u'Eth1/1',
        u'hardware/interfaces/0/switch_chassis_id': u'c1-11-1.ord1'
    },
    u'driver': u'agent_ipmitool',
    u'updated_at': u'2014-12-29T21:52:25+00:00', u'instance_info': {},
    u'provision_updated_at': u'2014-12-12T22:41:51+00:00',
    u'maintenance': False,
    u'maintenance_reason': None,
    u'reservation': None,
    u'provision_state': None,
    u'chassis_uuid': None,
    u'created_at': u'2014-10-23T20:14:47+00:00',
    u'power_state': u'power on',
    u'properties': {
        u'memory_mb': 524288,
        u'cpu_arch': u'amd64',
        u'local_gb': 32,
        u'cpus': 24
    },
    u'ports': [
        {
            u'href': u'http://ironic-api-vip.m0002.preprod-ord.ohthree.com'
                     u':6385/v1/nodes/04522204-d787-4e8e-b19f-18cfc2457412'
                     u'/ports',
            u'rel': u'self'
        },
        {
            u'href':
                u'http://ironic-api-vip.m0002.preprod-ord.ohthree.com'
                u':6385/nodes/04522204-d787-4e8e-b19f-18cfc2457412'
                u'/ports',
            u'rel': u'bookmark'}
    ]
}

test_port = {
    u'allowed_address_pairs': [],
    u'extra_dhcp_opts': [],
    u'device_owner': u'',
    u'binding:profile': {},
    u'trunked': False,
    u'fixed_ips': [],
    u'id': u'f68b7daf-0246-4ffd-ac07-6d8417e441f8',
    u'security_groups': [
        u'a84bcc62-7501-4c53-91e5-ba5a52323f81'
    ],
    u'binding:vif_details': {},
    u'binding:vif_type': u'unbound',
    u'mac_address': u'fa:16:3e:aa:aa:aa',
    u'status': u'DOWN',
    u'binding:host_id': u'',
    u'switch:hardware_id': u'fa39a693-1284-4ff6-b0cc-b287c06f578c',
    u'device_id': u'',
    u'name': u'',
    u'admin_state_up': True,
    u'network_id': u'22222222-2222-2222-2222-222222222222',
    u'tenant_id': u'fake',
    u'binding:vnic_type': u'normal',
    u'switch:ports': [
        {
            u'name': u'eth1',
            u'hardware_id': u'fa39a693-1284-4ff6-b0cc-b287c06f578c',
            u'switch_id': u'c1-11-2.ord1',
            u'port': u'eth1/1',
            u'mac_address': None,
            u'id': u'11732638-622c-4d00-8bc8-3e98135df0bb'
        },
        {
            u'name': u'eth0',
            u'hardware_id': u'fa39a693-1284-4ff6-b0cc-b287c06f578c',
            u'switch_id': u'c1-11-1.ord1',
            u'port': u'eth1/1',
            u'mac_address': None,
            u'id': u'8a7b10b3-651d-44fe-849c-db9f6604b8e6'
        }
    ],
    u'commit': True}


class BaseTest(unittest.TestCase):
    def _get_test_node(self, **kwargs):
        node = copy.copy(test_node)
        for k, v in kwargs.items():
            node[k] = v
        return node

    def _get_test_port(self, **kwargs):
        port = copy.copy(test_port)
        for k, v in kwargs.items():
            port[k] = v
        return port
