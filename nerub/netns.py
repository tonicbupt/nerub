# coding: utf-8

import logging
import os
import errno
import uuid

from subprocess32 import check_output, STDOUT
from netaddr import IPAddress

_log = logging.getLogger(__name__)
_log.addHandler(logging.NullHandler())

IP_CMD_TIMEOUT = 5
"""How long to wait (seconds) for IP commands to complete."""


def create_veth(veth, eth, ip):
    check_output(['ip', 'link', 'add', veth, 'link', eth, 'type', 'macvlan', 'mode', 'bridge'])
    check_output(['ip', 'addr', 'add', '%s/16' % ip, 'dev', veth])
    check_output(['ip', 'link', 'set', veth, 'up'])


def add_ns_default_route(namespace, next_hop, veth_name_ns):
    """
    Add a default route to the namespace.

    :param namespace: The namespace to operate in.
    :type namespace Namespace
    :param next_hop: The next hop IP used as the default route in the namespace.
    :param veth_name_ns: The name of the interface in the namespace.
    :return: None. Raises CalledProcessError on error.
    """
    assert isinstance(next_hop, IPAddress)
    with NamedNamespace(namespace) as ns:
        # Connected route to next hop & default route.
        ns.check_output(["ip", "-%s" % next_hop.version, "route", "replace",
                       str(next_hop), "dev", veth_name_ns])
        ns.check_output(["ip", "-%s" % next_hop.version, "route", "replace",
                      "default", "via", str(next_hop), "dev", veth_name_ns])


def add_ip_to_ns_veth(namespace, ip, veth_name_ns):
    """
    Add an IP to an interface in a namespace.

    :param namespace: The namespace to operate in.
    :type namespace Namespace
    :param ip: The IPAddress to add.
    :param veth_name_ns: The interface to add the address to.
    :return: None. Raises CalledProcessError on error.
    """
    with NamedNamespace(namespace) as ns:
        ns.check_output(["ip", "-%s" % ip.version, "addr", "add",
                       "%s/%s" % (ip, ip.network.cidr.hostmast),
                       "dev", veth_name_ns])


def remove_ip_from_ns_veth(namespace, ip, veth_name_ns):
    """
    Remove an IP from an interface in a namespace.

    :param namespace: The namespace to operate in.
    :type namespace Namespace
    :param ip: The IPAddress to remove.
    :param veth_name_ns: The interface to remove the address from.
    :return: None. raises CalledProcessError on error.
    """
    assert isinstance(ip, IPAddress)
    with NamedNamespace(namespace) as ns:
        ns.check_output(["ip", "-%s" % ip.version, "addr", "del",
                       "%s/%s" % (ip, ip.network.cidr.hostmask),
                       "dev", veth_name_ns])


class NamedNamespace(object):
    """
    Create a named namespace to allow us to run commands
    from within the namespace using standard `ip netns exec`.

    An alternative approach would be to use nsenter, which allows us to exec
    directly in a PID namespace.  However, this is not installed by default
    on some OSs that we need to support.
    """
    def __init__(self, namespace):
        """
        Create a NamedNamespace from a Namespace object.

        :param namespace: The source namespace to link to.
        :type namespace Namespace
        """
        self.name = uuid.uuid1().hex
        self.ns_path = namespace.path
        self.nsn_dir = "/var/run/netns/%s" % self.name
        if not os.path.exists(self.ns_path):
            raise NamespaceError("Namespace pseudofile %s does not exist." %
                                 self.ns_path)

    def __enter__(self):
        """
        Add the appropriate configuration to name the namespace.  This links
        the PID to the namespace name.
        """
        _log.debug("Creating link between namespace %s and PID %s",
                   self.name, self.ns_path)
        try:
            os.makedirs("/var/run/netns")
        except os.error as oserr:
            if oserr.errno != errno.EEXIST:
                _log.error("Unable to create /var/run/netns dir")
                raise
        os.symlink(self.ns_path, self.nsn_dir)
        return self

    def __exit__(self, _type, _value, _traceback):
        try:
            os.unlink(self.nsn_dir)
        except BaseException:
            _log.exception("Failed to remove link: %s", self.nsn_dir)
        return False

    def check_output(self, command):
        """
        Run a command within the named namespace.
        :param command: The command to run.
        :param shell: Whether this is a shell command.
        :param timeout: Command timeout in seconds.
        """
        command = self._get_nets_command(command)
        _log.debug("Run command: %s", command)
        return check_output(command, timeout=IP_CMD_TIMEOUT, stderr=STDOUT)

    def _get_nets_command(self, command):
        """
        Construct the netns command to execute.

        :param command: The command to execute.  This may either be a list or a
        single string.
        :return: The command to execute wrapped in the appropriate netns exec.
        If the original command was in list format, this returns a list,
        otherwise returns as a single string.
        """
        assert isinstance(command, list)
        return ["ip", "netns", "exec", self.name] + command


class NamespaceError(Exception):
    """
    Error creating or manipulating a network namespace.
    """
    pass


class Namespace(object):
    def __init__(self, path):
        self.path = path
