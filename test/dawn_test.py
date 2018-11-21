from datetime import time, timedelta

import pytest
from freezegun import freeze_time

import lib.dawn as dawn
from lib.dawn import get_value, is_dawn_time, parse_args, start_dawn, wait_more


def test_parse_args():
    result = parse_args({
        'dawn-time': '10:11:12',
        'dawn-duration': 20,
        'wait-duration': 30,
        'bulb-address': 'address',
        'immediately': False
    })
    assert result == (time(10, 11, 12), timedelta(minutes=20), timedelta(minutes=30), 'address', False)


@freeze_time('2018-10-21 10:00:00')
def test_is_dawn_time_if_weekend():
    result = is_dawn_time(None)
    assert not result


@freeze_time('2018-10-22 10:00:00')
def test_is_dawn_time_if_dawn():
    result = is_dawn_time(time(10, 0, 0))
    assert result


@freeze_time('2018-10-22 10:00:00')
def test_is_dawn_time_if_not_dawn():
    result = is_dawn_time(time(11, 0, 0))
    assert not result


def test_start_dawn(mocker):
    mocker.patch.object(dawn, 'sleep')
    start_dawn(timedelta(minutes=1), mocker.Mock())


def test_wait_more(mocker):
    mocker.patch.object(dawn, 'sleep')
    wait_more(timedelta(minutes=1), mocker.Mock())


@pytest.mark.parametrize('step,expected', (
    (0, 1),
    (15, 4),
    (30, 17),
    (40, 43),
    (49, 100),
))
def test_get_value(step, expected):
    result = get_value(0, 100, 50, step)
    assert result == expected
