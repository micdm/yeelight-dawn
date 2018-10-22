import json
import logging
import socket
from argparse import ArgumentParser
from struct import unpack
from time import sleep, time
from typing import Tuple

from .miio import encrypt, decrypt

logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s]: %(message)s')
logger = logging.getLogger(__name__)


HOST = '192.168.13.1'
PORT = 54321


def get_args() -> Tuple[str, str]:
    parser = ArgumentParser()
    parser.add_argument('--ssid')
    parser.add_argument('--password')
    args = parser.parse_args()
    return args.ssid, args.password


def create_socket():
    return socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def get_device_info(sock) -> Tuple[int, int, bytes]:
    logger.info('Receiving token...')
    packet = b'\x21\x31\x00\x20\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff' \
             b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff'
    sock.sendto(packet, (HOST, PORT))
    data, _ = sock.recvfrom(1024)
    logger.debug('HELLO response is %s', data)
    return unpack('!II16s', data[8:])


def get_mac() -> str:
    with open('/proc/net/arp') as arp:
        for line in arp:
            if line.startswith(HOST):
                return line[41:58]
        raise RuntimeError('MAC not found')


def enable_developer_mode(sock, device_id: int, stamp: int, token: bytes) -> dict:
    logger.info('Enabling developer mode...')
    payload = build_payload('set_ps', ['cfg_lan_ctrl', '1'])
    return send_packet(sock, device_id, stamp, token, payload)


def write_credentials(sock, device_id: int, stamp: int, token: bytes, ssid: str, password: str) -> dict:
    logger.info('Writing credentials %s:%s...', ssid, password)
    payload = build_payload('miIO.config_router', {
        'ssid': ssid,
        'passwd': password,
        'uid': 1
    })
    return send_packet(sock, device_id, stamp, token, payload)


def build_payload(method: str, params: dict or list) -> bytes:
    return ('{"id": %s, "method": "%s", "params": %s}' % (int(time()), method, json.dumps(params))).encode()


def send_packet(sock, device_id: int, stamp: int, token: bytes, payload: bytes) -> dict:
    logger.debug('Payload is %s', payload)
    packet = encrypt(device_id, stamp, token, payload)
    logger.debug('Packet is %s', packet)
    sock.sendto(packet, (HOST, PORT))
    data, _ = sock.recvfrom(1024)
    return json.loads(decrypt(token, data))


def check_response(response: dict):
    if response['result'][0] != 'ok':
        logger.warning('Response is %s', response)
        raise RuntimeError('unexpected response')
    logger.info('Success!')


def run():
    sock = create_socket()
    device_id, stamp, token = get_device_info(sock)
    logger.info('Device ID is %s, stamp is %s, token is %s', device_id, stamp, token)
    mac = get_mac()
    logger.info('MAC is %s', mac)
    ssid, password = get_args()
    if ssid and password:
        response = enable_developer_mode(sock, device_id, stamp, token)
        check_response(response)
        # Wait a bit to allow the bulb to process previous command
        sleep(2)
        response = write_credentials(sock, device_id, stamp, token, ssid, password)
        check_response(response)
    else:
        logger.info('Provide SSID and password to enable developer mode and set up WiFi')


if __name__ == '__main__':
    run()
