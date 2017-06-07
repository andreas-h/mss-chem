# -*- coding: utf-8 -*-

from __future__ import print_function

import datetime
import os.path

import msschem_settings


# from https://stackoverflow.com/a/1160227
def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)


if __name__ == '__main__':
    today = datetime.date.today()
    fcinit = datetime.datetime(today.year, today.month, today.day)

    for name, driver in msschem_settings.register_datasources.items():
        print('Processing {}, init_time {:%Y-%m-%dT%H:%M:%S}'.format(
                name, fcinit))
        all_species = driver.cfg['species']
        if not all_species:
            print('  ... no species requested')
            continue
        target_dir = os.path.dirname(driver.output_filename(all_species[0],
                                                            fcinit))

        lockfile = os.path.join(target_dir, 'msschem.lock')
        donefile = os.path.join(target_dir, 'msschem.done')

        if not os.path.isdir(target_dir):
            os.makedirs(target_dir)

        # check if donefile exists
        if os.path.isfile(donefile):
            # TODO add option to re-download
            print('  ... already downloaded. aborting.')
            continue

        # check if lockfile exists
        if os.path.isfile(lockfile):
            print('  ... lockfile exists. aborting.')
            continue

        # create lockfile
        touch(lockfile)

        # start processing this model
        for species in all_species:
            print('  ... {}'.format(species))
            driver.get(species, fcinit)

        if os.path.isfile(lockfile):
            os.remove(lockfile)

        touch(donefile)
