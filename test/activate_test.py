import pytest
from freezegun import freeze_time

from lib.activate import check_response, build_payload, send_packet, get_device_info


def test_get_device_info(mocker):
    sock = mocker.Mock()
    sock.recvfrom.return_value = (b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\n\x00\x00\x00\x14hellothereazazaz',
                                  None)
    result = get_device_info(sock)
    assert result == (10, 20, b'hellothereazazaz')


@freeze_time('2018-10-22 10:00:00')
def test_build_payload():
    result = build_payload('method', [])
    assert result == b'{"id": 1540202400, "method": "method", "params": []}'


def test_send_packet(mocker):
    sock = mocker.Mock()
    sock.recvfrom.return_value = (b'!1\x000\x00\x00\x00\x00\x02\xbd\xdbw\x00\x00\x00\x01\x87\x8c\xb3y\xbc\xa1y\x89\xb8'
                                  b'\xdev\x85l\xef\x15/Z1\x7fs\x04n\x89\x1a;`\xd3\xa3^h\xc7\x9f', None)
    result = send_packet(sock, 1, 1, b'token', b'payload')
    assert result == {"id": 1}


def test_check_response_if_ok():
    check_response({'result': ['ok']})


def test_check_response_if_fail():
    with pytest.raises(RuntimeError):
        check_response({'result': ['fail']})
