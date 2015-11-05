# coding: utf-8

import pytest
import hashlib
from netaddr import IPNetwork
from nerub.network import Network, IP


def test_network_create(test_db):
    network_id = hashlib.sha1('network_id').hexdigest()
    network = Network.create(network_id, '10.100.0.1/16')
    assert network is not None
    assert network.network_id == network_id
    assert network.cidr == IPNetwork('10.100.0.1/16')
    assert network.cidr.size == 65536

    n1 = Network.get(network_id)
    assert n1.network_id == network.network_id
    n2 = Network.get('random id')
    assert n2 is None

    n3 = Network.get_by_cidr('10.100.0.1/16')
    assert n3.network_id == network.network_id
    n4 = Network.get_by_cidr('10.100.0.1/15')
    assert n4 is None


def test_ip_acquire(test_db):
    network_id = hashlib.sha1('network_id').hexdigest()
    ep_id1 = hashlib.sha1('ep_id1').hexdigest()
    ep_id2 = hashlib.sha1('ep_id2').hexdigest()

    network = Network.create(network_id, '10.100.0.1/16')

    ip1 = network.acquire_ip(ep_id1, 'hostname')
    assert ip1 is not None
    assert ip1.hostname == 'hostname'
    assert ip1.endpoint_id == ep_id1
    assert ip1.network_id == network_id
    assert ip1.ip

    ip2 = network.acquire_ip(ep_id2, 'hostname', '10.100.0.2')
    assert ip2 is not None
    assert ip2.hostname == 'hostname'
    assert ip2.endpoint_id == ep_id2
    assert ip2.network_id == network_id
    assert str(ip2.ip) == '10.100.0.2'

    ip3 = network.acquire_ip(ep_id2, 'hostname', '10.101.0.1')
    assert ip3 is None

    ip4 = IP.get(ep_id1)
    assert ip4.endpoint_id == ip1.endpoint_id == ep_id1
    ip5 = IP.get(ep_id2)
    assert ip5.endpoint_id == ip2.endpoint_id == ep_id2


def test_network_delete(test_db):
    network_id1 = hashlib.sha1('network_id1').hexdigest()
    network_id2 = hashlib.sha1('network_id2').hexdigest()
    ep_id = hashlib.sha1('ep_id').hexdigest()

    n1 = Network.create(network_id1, '10.100.0.1/16')
    n1.delete()
    n2 = Network.get(network_id1)
    assert n2 is None

    n3 = Network.create(network_id2, '10.100.0.1/16')
    n3.acquire_ip(ep_id, 'hostname')
    with pytest.raises(Exception):
        n3.delete()

    n4 = Network.get(network_id2)
    assert n4.network_id == n3.network_id == network_id2
