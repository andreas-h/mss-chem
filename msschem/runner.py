# -*- coding: utf-8 -*-

from __future__ import print_function

import argparse
import datetime
import logging
import os.path
import runpy

VERBOSE = True
QUIET = False

# TODO allow parallel download of different models
# TODO allow parallel download of species (??)


def _valid_date(s):
    try:
        return datetime.datetime.strptime(s, "%Y-%m-%d").date()
    except ValueError:
        msg = "Not a valid date: '{0}'.".format(s)
        raise argparse.ArgumentTypeError(msg)


def _setup_logging(level):
    log = logging.getLogger('msschem')
    log.setLevel(level)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    log.addHandler(ch)


def _setup_argparse():
    parser = argparse.ArgumentParser(description='MSS-Chem downloader')

    datagroup = parser.add_mutually_exclusive_group(required=True)
    datagroup.add_argument('-m', '--model', type=str, default='',
                           help='Model to download')
    datagroup.add_argument('-a', '--all', action='store_true',
                           help='Download data from all configured models')

    parser.add_argument('-d', '--date', type=_valid_date,
                        default=datetime.date.today(),
                        help='Date to download data for (YYYY-MM-DD)')

    parser.add_argument('-p', '--prune', type=int,
                        help='Delete data older than PRUNE days')

    parser.add_argument('-c', '--config', type=str, default='',
                        help='MSS-Chem configuration file')

    loggroup = parser.add_mutually_exclusive_group()
    loggroup.add_argument('-q', '--quiet', action='store_true',
                          help='No output except for errors')
    loggroup.add_argument('-v', '--verbosity', action='count', default=0,
                          help='Increase output verbosity (can be supplied '
                               'multiple times)')

    return parser


def read_config(configfile):
    if configfile:
        configfile = os.path.expanduser(configfile)
        if os.path.isfile(configfile):
            try:
                cfg = runpy.run_path(configfile)['datasources']
            except:
                raise ValueError('Cannot read configuration from file {}'
                                 ''.format(configfile))
        else:
            raise IOError('Configuration file {} does not exist'
                          ''.format(configfile))
    else:
        from msschem_settings import datasources as cfg
    return cfg


if __name__ == '__main__':
    parser = _setup_argparse()
    args = parser.parse_args()

    if args.verbosity > 1:
        loglevel = logging.DEBUG
    elif args.verbosity == 1:
        loglevel = logging.INFO
    elif not args.quiet:
        loglevel = logging.WARN
    else:
        loglevel = logging.ERROR
    _setup_logging(loglevel)

    fcinit = datetime.datetime(args.date.year, args.date.month, args.date.day)

    datasources = read_config(args.config)

    if args.model:
        datasources[args.model].run(fcinit)
        try:
            datasources[args.model].prune(args.prune)
        except:
            raise
    else:
        for driver in datasources.values():
            driver.run(fcinit)
            try:
                datasources[args.model].prune(args.prune)
            except:
                raise
