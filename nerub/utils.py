# coding: utf-8

import string
import random


def random_hex(length):
    return ''.join(random.choice(string.hexdigits) for _ in xrange(length))


def random_mac():
    return ':'.join([random_hex(2).upper() for _ in xrange(6)])


def random_veth():
    return 'veth.%s' % random_hex(6)
