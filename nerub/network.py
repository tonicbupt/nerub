# coding: utf-8

import pickle
import more_itertools
from netaddr import IPNetwork, IPAddress
from redis import Redis


rds = Redis()


class IP(object):

    _ENDPOINT_KEY = 'nerub:ip:endpoint_id:%s'

    def __init__(self, ip, hostname, endpoint_id, network_id):
        self.ip = ip
        self.hostname = hostname
        self.endpoint_id = endpoint_id
        self.network_id = network_id

    @classmethod
    def create(cls, ip, hostname, endpoint_id, network_id):
        ip = cls(ip, hostname, endpoint_id, network_id)
        rds.set(cls._ENDPOINT_KEY % endpoint_id, pickle.dumps(ip))
        return ip

    @classmethod
    def get(cls, endpoint_id):
        value = rds.get(cls._ENDPOINT_KEY % endpoint_id)
        if not value:
            return None
        return pickle.loads(value)

    @property
    def network(self):
        return Network.get(self.network_id)

    def release(self):
        rds.delete(self._ENDPOINT_KEY % self.endpoint_id)
        network = Network.get(self.network_id)
        if network:
            network.release_ip(self.ip)

    def __str__(self):
        return str(self.ip)


class Network(object):

    _CIDR_KEY = 'nerub:network:%s:cidr'
    _NETWORK_ID_KEY = 'nerub:network:%s:network_id'
    _NETWORK_IPS_KEY = 'nerub:network:%s:ips'

    def __init__(self, network_id, cidr):
        self.network_id = network_id
        self.cidr = IPNetwork(cidr)

    @classmethod
    def create(cls, network_id, cidr):
        network = cls(network_id, cidr)
        ip_network = network.cidr

        rds.set(cls._CIDR_KEY % network_id, cidr)
        rds.set(cls._NETWORK_ID_KEY % cidr, network_id)

        key = cls._NETWORK_IPS_KEY % network_id
        for ipnums in more_itertools.chunked(xrange(ip_network.first, ip_network.last+1), 500):
            rds.sadd(key, *ipnums)

        return network

    @classmethod
    def get(cls, network_id):
        cidr = rds.get(cls._CIDR_KEY % network_id)
        if not cidr:
            return None
        return cls(network_id, cidr)

    @classmethod
    def get_by_cidr(cls, cidr):
        network_id = rds.get(cls._NETWORK_ID_KEY % cidr)
        if not network_id:
            return None
        return cls(network_id, cidr)

    def acquire_ip(self, endpoint_id, hostname, ip=None):
        key = self._NETWORK_IPS_KEY % self.network_id
        if ip is None:
            ipnum = rds.spop(key)
            ip = IPAddress(ipnum)
        else:
            if isinstance(ip, basestring):
                ip = IPAddress(ip)
            if not rds.sismember(key, ip.value):
                return None
            rds.srem(key, ip.value)

        return IP.create(ip, hostname, endpoint_id, self.network_id)

    def release_ip(self, ip):
        rds.sadd(self._NETWORK_IPS_KEY % self.network_id, ip.value)

    def delete(self):
        total = rds.scard(self._NETWORK_IPS_KEY % self.network_id)
        if total != self.cidr.size:
            raise Exception('Some endpoints still in use')

        rds.delete(self._CIDR_KEY % self.network_id)
        rds.delete(self._NETWORK_ID_KEY % self.cidr)
        rds.delete(self._NETWORK_IPS_KEY % self.network_id)
