# coding: utf-8

import sys
import socket
import logging

from flask import Flask, jsonify, request
from netaddr import IPAddress
from nerub.network import IP, Network


hostname = socket.gethostname()
app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.DEBUG)
app.logger.info('Application started')


@app.route('/Plugin.Activate', methods=['POST'])
def activate():
    resp = {'Implements': ['NetworkDriver']}
    app.logger.info('Activate response JSON=%s', resp)
    return jsonify(resp)


@app.route('/NetworkDriver.GetCapabilities', methods=['POST'])
def get_capabilities():
    resp = {'Scope': 'global'}
    app.logger.debug('GetCapabilities response JSON=%s', resp)
    return jsonify(resp)


@app.route('/NetworkDriver.CreateNetwork', methods=['POST'])
def create_network():
    data = request.get_json(force=True)
    app.logger.debug('CreateNetwork JSON=%s', data)

    network_id = data['NetworkID']
    app.logger.info('Creating profile %s', network_id)

    ip_data = data['IPv4Data']
    if ip_data:
        Network.create(network_id, ip_data['Pool'])

    app.logger.debug('CreateNetwork response JSON=%s', '{}')
    return jsonify({})


@app.route('/NetworkDriver.CreateEndpoint', methods=['POST'])
def create_endpoint():
    data = request.get_json(force=True)
    app.logger.debug('CreateEndpoint JSON=%s', data)

    endpoint_id = data['EndpointID']
    network_id = data['NetworkID']
    interface = data['Interface']

    app.logger.info('Creating endpoint %s', endpoint_id)

    # Get the addresses to use from the request JSON.
    address_ip4 = interface.get('Address', None)
    address_ip4 = address_ip4 and IPAddress(address_ip4) or None

    # Get the gateway from the data passed in during CreateNetwork
    network = Network.get(network_id)

    if not network:
        error_message = "CreateEndpoint called but network doesn\'t exist" \
                        " Endpoint ID: %s Network ID: %s" % \
                        (endpoint_id, network_id)
        app.logger.error(error_message)
        raise Exception(error_message)

    network.acquire_ip(endpoint_id, hostname, ip=address_ip4)
    app.logger.debug('CreateEndpoint response JSON=%s', {})
    return jsonify({})


@app.route('/NetworkDriver.Join', methods=['POST'])
def join():
    data = request.get_json(force=True)
    app.logger.debug('Join JSON=%s', data)

    endpoint_id = data['EndpointID']
    app.logger.info('Joining endpoint %s', endpoint_id)

    IP.get(endpoint_id)

    # TODO 不知道要怎么搞了, 先看看

    # # The host interface name matches the name given when creating the endpoint
    # # during CreateEndpoint
    # host_interface_name = generate_cali_interface_name(IF_PREFIX, endpoint_id)

    # # The temporary interface name is what gets passed to libnetwork.
    # # Libnetwork renames the interface using the DstPrefix (e.g. cali0)
    # temp_interface_name = generate_cali_interface_name('tmp', endpoint_id)

    # try:
    #     # Create the veth pair.
    #     netns.create_veth(host_interface_name, temp_interface_name)

    #     # Set the mac as libnetwork doesn't do this for us (even if we return
    #     # it on the CreateNetwork)
    #     netns.set_veth_mac(temp_interface_name, FIXED_MAC)
    # except CalledProcessError as e:
    #     # Failed to create or configure the veth, ensure veth is removed.
    #     remove_veth(host_interface_name)
    #     raise e

    # return_json = {
    #     'InterfaceName': {
    #         'SrcName': temp_interface_name,
    #         'DstPrefix': IF_PREFIX
    #     },
    #     'Gateway': '',  # Leave gateway empty to trigger auto-gateway behaviour
    # }

    # app.logger.debug('Join Response JSON=%s', return_json)
    # return jsonify(return_json)
    return jsonify({})


@app.route('/NetworkDriver.EndpointOperInfo', methods=['POST'])
def endpoint_oper_info():
    data = request.get_json(force=True)
    app.logger.debug('EndpointOperInfo JSON=%s', data)
    endpoint_id = data['EndpointID']

    app.logger.info('Endpoint operation info requested for %s', endpoint_id)

    # Might need to return MAC here but it currently crashes Docker
    # https://github.com/docker/libnetwork/issues/605
    # ret_json = {'com.docker.network.endpoint.macaddress': FIXED_MAC}

    app.logger.debug('EP Oper Info Response JSON=%s', {})
    return jsonify({'Value': {}})


@app.route('/NetworkDriver.DeleteNetwork', methods=['POST'])
def delete_network():
    data = request.get_json(force=True)
    app.logger.debug('DeleteNetwork JSON=%s', data)

    network_id = data['NetworkID']
    network = Network.get(network_id)
    if network:
        network.delete()

    app.logger.info('Removed network %s', network_id)
    return jsonify({})


@app.route('/NetworkDriver.DeleteEndpoint', methods=['POST'])
def delete_endpoint():
    data = request.get_json(force=True)
    app.logger.debug('DeleteEndpoint JSON=%s', data)

    endpoint_id = data['EndpointID']
    app.logger.info('Removing endpoint %s', endpoint_id)

    ip = IP.get(endpoint_id)
    if ip:
        ip.release()

    app.logger.debug('DeleteEndpoint response JSON=%s', '{}')
    return jsonify({})


@app.route('/NetworkDriver.Leave', methods=['POST'])
def leave():
    data = request.get_json(force=True)
    app.logger.debug('Leave JSON=%s', data)

    endpoint_id = data['EndpointID']
    app.logger.info('Leaving endpoint %s', endpoint_id)

    IP.get(endpoint_id)
    # TODO 这里又不知道怎么做了
    # 是说去掉这块网卡吧
    # remove_veth(generate_cali_interface_name(IF_PREFIX, ep_id))

    app.logger.debug('Leave response JSON=%s', '{}')
    return jsonify({})


@app.route('/NetworkDriver.DiscoverNew', methods=['POST'])
def discover_new():
    data = request.get_json(force=True)
    app.logger.debug('DiscoverNew JSON=%s', data)
    app.logger.debug('DiscoverNew response JSON=%s', '{}')
    return jsonify({})


@app.route('/NetworkDriver.DiscoverDelete', methods=['POST'])
def discover_delete():
    data = request.get_json(force=True)
    app.logger.debug('DiscoverNew JSON=%s', data)
    app.logger.debug('DiscoverDelete response JSON=%s', '{}')
    return jsonify({})
