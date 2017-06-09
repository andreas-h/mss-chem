# -*- coding: utf-8 -*-

from __future__ import print_function

import datetime
import logging

import msschem_settings

VERBOSE = True
QUIET = False

# TODO allow parallel download of different models
# TODO allow parallel download of species (??)

def _setup_logging(level):
    log = logging.getLogger('msschem')
    log.setLevel(level)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    log.addHandler(ch)


if __name__ == '__main__':
    if VERBOSE:
        loglevel = logging.DEBUG
    elif QUIET:
        loglevel = logging.ERROR
    else:
        loglevel = logging.WARN
    _setup_logging(loglevel)
    today = datetime.date.today()
    fcinit = datetime.datetime(today.year, today.month, today.day)

    for name, driver in msschem_settings.register_datasources.items():
        driver.run(fcinit)
