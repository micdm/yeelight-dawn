from argparse import ArgumentParser
from datetime import datetime, time, timedelta
import logging
from time import sleep
from typing import Tuple

from yeelight import Bulb

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s]: %(message)s')
logger = logging.getLogger(__name__)

MIN_BRIGHTNESS, MAX_BRIGHTNESS = 1, 100
MIN_TEMPERATURE, MAX_TEMPERATURE = 1700, 4000
STEP = timedelta(seconds=15)


def get_args() -> dict:
    parser = ArgumentParser()
    parser.add_argument('dawn-time')
    parser.add_argument('dawn-duration', type=int)
    parser.add_argument('wait-duration', type=int)
    parser.add_argument('bulb-address')
    parser.add_argument('--immediately', action='store_true')
    return vars(parser.parse_args())


def parse_args(raw_args: dict) -> Tuple[time, timedelta, timedelta, str, bool]:
    dawn_time = time(*map(int, raw_args['dawn-time'].split(':')))
    dawn_duration = timedelta(minutes=raw_args['dawn-duration'])
    wait_duration = timedelta(minutes=raw_args['wait-duration'])
    return dawn_time, dawn_duration, wait_duration, raw_args['bulb-address'], raw_args['immediately']


def is_dawn_time(dawn_time: time) -> bool:
    date_now = datetime.now().date()
    time_now = datetime.now().time()
    return date_now.weekday() < 5 and time_now.hour == dawn_time.hour and time_now.minute == dawn_time.minute \
           and time_now.second == dawn_time.second


def start_dawn(duration: timedelta, bulb: Bulb):
    steps = duration // STEP
    logger.info('Starting dawn in %s steps...', steps)
    bulb.turn_on()
    for step in range(steps):
        temperature = get_value(MIN_TEMPERATURE, MAX_TEMPERATURE, steps, step)
        brightness = get_value(MIN_BRIGHTNESS, MAX_BRIGHTNESS, steps, step)
        logger.debug('Setting up temperature to %s and brightness to %s on %s step', temperature, brightness, step)
        bulb.set_color_temp(temperature)
        bulb.set_brightness(brightness)
        sleep(STEP.seconds)
    logger.info('Rise and shine!')


def wait_more(duration: timedelta, bulb: Bulb):
    logger.info('Sleeping a bit more for %s', timedelta)
    sleep(duration.seconds)
    logger.info('Turning off...')
    bulb.turn_off()


def get_value(min_value: int, max_value: int, steps: int, step: int) -> int:
    return int((max_value - min_value) ** ((step + 1) / float(steps)) + min_value)


def run():
    raw_args = get_args()
    dawn_time, dawn_duration, wait_duration, bulb_address, is_test_run = parse_args(raw_args)
    if is_test_run:
        logger.info('Dawn will be started immediately and will take %s', dawn_duration)
    else:
        logger.info('Dawn scheduled at %s and will take %s', dawn_time, dawn_duration)
    while True:
        try:
            if is_dawn_time(dawn_time) or is_test_run:
                bulb = Bulb(bulb_address)
                start_dawn(dawn_duration, bulb)
                wait_more(wait_duration, bulb)
            else:
                sleep(1)
        except KeyboardInterrupt:
            logger.info('Exiting...')
            break


if __name__ == '__main__':
    run()
