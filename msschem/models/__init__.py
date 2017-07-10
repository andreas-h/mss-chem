# -*- coding: utf-8 -*-

from collections import OrderedDict
import copy
import datetime
import glob
import logging
import os, os.path
import shutil
import tempfile

from netCDF4 import Dataset, MFDataset, date2num, num2date
import numpy as np

try:
    from nco import Nco
    _NCO = True
except ImportError:
    _NCO = False

# from .version import __version__

from ..species import species_names
from ..fileutils import touch
from .. import DataNotAvailable

#__all__ = ['CTMDriver', 'CAMSGlobDriver']


"""**************
msschem.models
**************

This module provides the model-specific pre-processing pipelines to prepare the
CTM data for ingestion by MSS

This file is part of mss-chem.

:copyright: Copyright 2017 Andreas Hilboll
:copyright: Copyright 2017 by the mss-chem team, see AUTHORS.rst
:license: APACHE-2.0, see LICENSE for details.

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""

"""
*****
NOTES
*****

- [ ] 


"""


class CTMDriver(object):

    needed_vars = []

    datavar_attrs_no_copy = ['_FillValue', 'add_offset', 'scale_factor']
    dimensions_no_copy = []

    need_to_convert_to_nc4c = False

    def __init__(self, cfg):
        self.log = logging.getLogger('msschem')
        if cfg.get('force') is None:
            cfg['force'] = False
        if cfg.get('temppath') is None:
            cfg['temppath'] = os.path.join(cfg['basepath'], 'tmp')
        if not os.path.isdir(cfg['temppath']):
            os.makedirs(cfg['temppath'])
        for sp in cfg.get('species', []):
            if sp not in self.species.keys():
                raise ValueError(
                    'The requested species `{}` is not supported for model '
                    '`{}`'.format(sp, cfg.get('name')))
        if ('AIR_PRESSURE' in self.species.keys() and
                'AIR_PRESSURE' not in cfg.get('species', [])):
            cfg['species'] = cfg['species'] + ['AIR_PRESSURE']
        self.cfg = cfg

    def check_day(self, day):
        if isinstance(day, datetime.datetime):
            day = day.date()
        if not isinstance(day, (datetime.date, datetime.datetime)):
            raise ValueError('"day" parameter to "download" method is not a '
                             'date nor a datetime')
        if isinstance(day, datetime.date):
            day = datetime.datetime(day.year, day.month, day.day)
        if day > datetime.datetime.now():
            raise ValueError('cannot retrieve future forecast base times')
        return day

    def get_dims(self, species):
        dimsize = copy.deepcopy(self.dims)
        return OrderedDict(dimsize)

    def convert_dl_to_nc4c(self, fns):
        self.log.debug('Converting to NETCDF4_CLASSIC ...')
        if not _NCO:
            self.log.error(
                    'Cannot convert to NETCDF4_CLASSIC: nco is not installed')
            raise ImportError('cannot import nco library')
        nco = Nco()
        fns_new = []
        for fn in fns:
            fn_new = tempfile.mktemp(suffix='.nc', dir=self.cfg['temppath'])
            nco.ncks(input=fn, output=fn_new, options=['-O', '-7'])
            fns_new.append(fn_new)
            self.cfg['dldriver'].clean_tempfiles([fn])
        self.log.debug('... done.')
        return fns_new

    def check_download(self, fns, species, fcinit, fcstart, fcend, nt=None):
        dimsize = self.get_dims(species)
        nt = self.get_nt(fcinit, fcstart, fcend)
        dimsize['t'] = nt
        varname = self.species[species]['varname']
        with MFDataset(fns, 'r', aggdim=self.aggdim) as nc:
            var = nc.variables[varname]
            for i, (k, v) in enumerate(dimsize.items()):
                if var.shape[i] != v:
                    raise ValueError('Downloaded file(s) has wrong dimension'
                                     ' size {}={}'.format(k, var.shape[i]))

    def download(self, species, fcinit, fcend=None, fcstart=None):
        """Download data for one species.

        Parameters
        ==========
        species : str

        fcinit : datetime.date or datetime.datetime

        fcend : datetime.datetime or datetime.timedelta or int

        fcstart : datetime.datetime or datetime.timedelta or int

        """
        if species not in self.species.keys():
            raise ValueError()
        fcinit = self.check_day(fcinit)
        fcstart = self.get_fctime('start', fcinit, fcstart)
        fcend = self.get_fctime('end', fcinit, fcend)

        fn_temp = tempfile.mktemp(suffix='.nc', dir=self.cfg['temppath'])
        # TODO check if we need to download force_dl = self.cfg['force'])
        fns = self.cfg['dldriver'].get(self.species[species]['urlname'],
                                       fcinit, fcstart, fcend, fn_temp)
        if self.need_to_convert_to_nc4c:
            fns = self.convert_dl_to_nc4c(fns)

        self.check_download(fns, species, fcinit, fcstart, fcend)
        return fns

    def run(self, day):
        """Download all configured data for one day"""
        self.log.info('Starting {}: init_time {:%Y-%m-%dT%H:%M:%S}'.format(
                self.name, day))
        all_species = self.cfg['species']

        if not all_species:
            self.log.info('    ... no species requested')
            return

        target_dir = os.path.dirname(self.output_filename(all_species[0], day))
        lockfile = os.path.join(target_dir, 'msschem.lock')
        donefile = os.path.join(target_dir, 'msschem.done')

        if not os.path.isdir(target_dir):
            os.makedirs(target_dir)

        # check if donefile exists
        if os.path.isfile(donefile):
            # TODO add option to re-download
            self.log.info('{}/{:%Y%m%d} already downloaded.'.format(self.name,
                                                                    day))
            return

        # check if lockfile exists
        if os.path.isfile(lockfile):
            self.log.info('{}/{:%Y%m%d} lockfile exists. Aborting.'
                          ''.format(self.name, day))
            return

        # create lockfile
        touch(lockfile)

        # TODO add option to download in parallel, only for http
        # start processing this model
        for species in all_species:
            try:
                self.get(species, day)
            except DataNotAvailable:
                self.log.warning('No data available {}/{:%Y%m%d}'.format(
                        self.name, day))
                if os.path.isfile(lockfile):
                    os.remove(lockfile)
                return

        if os.path.isfile(lockfile):
            os.remove(lockfile)

        touch(donefile)
        self.log.info('Finished {}: init_time {:%Y-%m-%dT%H:%M:%S}'.format(
                self.name, day))

    def prune(self, n_days):
        """Clean up old files downloaded for this model"""
        self.log.debug('Cleanup {} (n_days={})'.format(self.name, n_days))
        date_threshold = datetime.date.today() - datetime.timedelta(n_days)

        # TODO get list of all existing date directories
        # each date is a tuple (datetime.date, path)

        outdir = os.path.join(self.cfg['basepath'], self.cfg['name'])
        paths = glob.glob(os.path.join(outdir, '*'))
        dates = [datetime.datetime.strptime(os.path.split(p)[1],
                                            '%Y-%m-%d_%H').date()
                 for p in paths]

        if not len(paths):
            self.log.info('No data to cleanup for {} (n_days={})'.format(
                    self.name, n_days))
            return

        for date, path in zip(dates, paths):
            if date < date_threshold:
                self.log.info('Removing {:%Y-%m-%d} ({})'.format(date,
                                                                 self.name))
                shutil.rmtree(path)

    def get(self, species, fcinit, fcend=None, fcstart=None):
        self.log.debug('Starting {}/{:%Y%m%d}:{}'.format(
                self.name, fcinit, species))
        fns_temp = self.download(species, fcinit, fcend, fcstart)
        self.postprocess(species, fcinit, fns_temp)
        self.cfg['dldriver'].clean_tempfiles(fns_temp)
        self.log.debug('Finished {}/{:%Y%m%d}:{}'.format(
                self.name, fcinit, species))

    def output_filename(self, species, fcinit):
        outdir = os.path.join(self.cfg['basepath'], self.cfg['name'],
                              '{:%Y-%m-%d_%H}'.format(fcinit))
        outname = '{name}_{fcinit:%Y-%m-%d_%H}_{layer}_{species}.nc'.format(
                name=self.cfg['name'], species=species.lower(),
                layer=self.layer_type, fcinit=fcinit)
        return os.path.join(outdir, outname)

    def postprocess(self, species, fcinit, fns):
        fn_out = self.output_filename(species, fcinit)
        dirname = os.path.dirname(fn_out)
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
        self.write_dataset(self.species[species]['varname'], fns, fn_out)
        self.fix_dataset(fn_out, species, fcinit)

    def set_standard_name(self, nc, species):
        if species == 'AIR_PRESSURE':
            stdname = 'air_pressure'
        elif species == 'AIR_TEMPERATURE':
            stdname = 'air_temperature'
        else:
            stdname = '{}_{}_of_{}_in_air'.format(
                    self.concentration_type, self.quantity_type,
                    species_names[species])
        try:
            nc.variables[self.species[species]['varname']].setncattr(
                    'standard_name', stdname)
        except KeyError:
            if species == 'AIR_PRESSURE':
                nc.variables['P'].setncattr('standard_name', stdname)
            else:
                raise

    def fix_dataset(self, fn_out, species, fcinit):
        raise NotImplementedError(
                'The method `fix_dataset` must be implemented in the '
                'model implementation.')

    def copy_dimensions(self, nc_in, nc_out):
        for name, dim in nc_in.dimensions.items():
            if name not in self.dimensions_no_copy:
                nc_out.createDimension(
                        name, None if dim.isunlimited() else dim.size)

    @staticmethod
    def copy_global_attrs(nc_in, nc_out):
        for name in nc_in.ncattrs():
            nc_out.setncattr(name, nc_in.__dict__[name])

    def copy_vars(self, nc_in, nc_out, varname_species):
        for name, var in nc_in.variables.items():
            if name not in self.needed_vars + [varname_species]:
                continue
            try:
                dtype = var.datatype
            except AttributeError:
                dtype = np.float32
            try:
                endian = var.endian()
            except AttributeError:
                endian = 'native'
            nc_out.createVariable(
                    name, dtype, var.dimensions,
                    zlib=(name not in nc_out.dimensions.keys()),
                    complevel=6, shuffle=True, fletcher32=True,
                    endian=endian)
            nc_out.variables[name][:] = var[:]

            # copy variable attributes
            for attr in var.ncattrs():
                if attr in self.datavar_attrs_no_copy:
                    continue
                nc_out.variables[name].setncattr(attr, var.__dict__[attr])

    def write_dataset(self, varname_species, fns_in, fn_out):
        with Dataset(fn_out, 'w', format='NETCDF4_CLASSIC') as nc_out, MFDataset(fns_in, 'r', aggdim=self.aggdim) as nc_in:
            # copy dimensions
            self.copy_dimensions(nc_in, nc_out)

            # copy global attributes
            self.copy_global_attrs(nc_in, nc_out)

            # copy variables
            self.copy_vars(nc_in, nc_out, varname_species)

    def get_fctime(self, start_or_end, fcinit, fctime):
        if start_or_end.lower() == 'start':
            offset = self.fcstart_offset
        elif start_or_end.lower() == 'end':
            offset = self.fcend_offset
        else:
            raise ValueError()

        if fctime is None:
            fctime = offset
        elif isinstance(fctime, int):
            fctime = datetime.timedelta(hours=fctime)
        elif isinstance(fctime, datetime.timedelta):
            fctime = fctime
        elif isinstance(fctime, datetime.datetime):
            fctime = fctime - fcinit
        else:
            raise ValueError(fctime.__class__)

        if not self.fcstart_offset <= fctime <= self.fcend_offset:
            raise ValueError()

        if fctime.total_seconds() % self.fcstep.total_seconds():
            raise ValueError('{} is not a valid fc_{}'.format(fctime,
                                                              start_or_end))

        return fcinit + fctime

    def get_nt(self, fcinit, fcstart, fcend):
        dt = (fcend - fcstart).total_seconds()
        return int(dt / self.fcstep.total_seconds()) + 1


class CAMSRegDriver(CTMDriver):

    fcstep = datetime.timedelta(hours=1)

    # offset of first forecast step relative to fcinit
    fcstart_offset = datetime.timedelta(hours=0)

    # maximum forecast step relative to fcinit
    fcend_offset = datetime.timedelta(hours=96)

    # dimensions
    dims = [('t', None), ('z', 8), ('y', 400), ('x', 700)]

    species = {'CO': dict(varname='co_conc', urlname='CO'),
               'NH3': dict(varname='nh3_conc', urlname='NH3'),
               'NMVOC': dict(varname='nmvoc_conc', urlname='NMVOC'),
               'NO2': dict(varname='no2_conc', urlname='NO2'),
               'NO': dict(varname='no_conc', urlname='NO'),
               'O3': dict(varname='o3_conc', urlname='O3'),
               'PANS': dict(varname='pans_conc', urlname='PANS'),
               'PM10': dict(varname='pm10_conc', urlname='PM10'),
               'PM25': dict(varname='pm2p5_conc', urlname='PM25'),
               'SO2': dict(varname='so2_conc', urlname='SO2'),
               }

    needed_vars = ['longitude', 'latitude', 'level', 'time']

    concentration_type = 'mass'
    quantity_type = 'concentration'
    layer_type = 'al'
    aggdim = 'time'
    name = 'CAMS_regional'

    def get_nt(self, fcinit, fcstart, fcend):
        # CAMS Regional files have 25 steps for the first forecast day
        # (including step 0), and 24 steps for later days.
        offset_start = fcstart - fcinit
        offset_end = fcend - fcinit
        nt = 0
        if offset_start <= datetime.timedelta(1):
            nt += 25
        if offset_end > datetime.timedelta(1):
            nt += 24
        if offset_end > datetime.timedelta(2):
            nt += 24
        if offset_end > datetime.timedelta(3):
            nt += 24
        return nt

    def fix_dataset(self, fn_out, species, fcinit):
        with Dataset(fn_out, 'a', format='NETCDF4_CLASSIC') as nc:
            nc.variables['time'].setncattr(
                'units', 'hours since {:%Y-%m-%dT%H:%M:%S}'.format(fcinit))
            nc.variables['time'].setncattr('standard_name', 'time')
            nc.variables['latitude'].setncattr('standard_name', 'latitude')
            nc.variables['longitude'].setncattr('standard_name', 'longitude')
            nc.variables['level'].setncattr('standard_name',
                                            'atmosphere_altitude_coordinate')
            self.set_standard_name(nc, species)


class SilamDriver(CTMDriver):

    fcstep = datetime.timedelta(hours=1)

    # offset of first forecast step relative to fcinit
    fcstart_offset = datetime.timedelta(hours=1)

    # maximum forecast step relative to fcinit
    fcend_offset = datetime.timedelta(hours=120)

    # dimensions
    dims = [('t', None), ('z', 10), ('y', 420), ('x', 700)]

    species = {'CO': dict(varname='cnc_CO_gas',
                          urlname='cnc_CO_gas'),
               'NO': dict(varname='cnc_NO_gas',
                          urlname='cnc_NO_gas'),
               'NO2': dict(varname='cnc_NO2_gas',
                           urlname='cnc_NO2_gas'),
               'NMVOC': dict(varname='cnc_NMVOC_gas',
                             urlname='cnc_NMVOC_gas'),
               'O3': dict(varname='cnc_O3_gas',
                          urlname='cnc_O3_gas'),
               'PANS': dict(varname='cnc_PAN_gas',
                            urlname='cnc_PAN_gas'),
               'PM10': dict(varname='cnc_PM10',
                            urlname='cnc_PM10'),
               'SO2': dict(varname='cnc_SO2_gas',
                           urlname='cnc_SO2_gas'),
               'AIR_PRESSURE': dict(varname='pressure',
                                    urlname='pressure'),
               'AIR_TEMPERATURE': dict(varname='temperature',
                                       urlname='temperature'),
               }

    needed_vars = ['lon', 'lat', 'height', 'time']

    concentration_type = 'mass'
    quantity_type = 'concentration'
    layer_type = 'al'
    aggdim = 'time'
    name = 'SILAM'

    def fix_dataset(self, fn_out, species, fcinit):
        with Dataset(fn_out, 'a', format='NETCDF4_CLASSIC') as nc:
            # convert time to hours since fcinit
            t_obj = num2date(nc.variables['time'][:],
                             nc.variables['time'].units)
            t_unit = 'hours since {:%Y-%m-%dT%H:%M:%S}'.format(fcinit)
            nc.variables['time'][:] = date2num(t_obj, t_unit)
            nc.variables['time'].setncattr('units', t_unit)
            nc.variables['time'].setncattr('standard_name', 'time')
            nc.variables['height'].setncattr('standard_name',
                                             'atmosphere_altitude_coordinate')
            # set standard name of data variable
            self.set_standard_name(nc, species)


class EMEPDriver(CTMDriver):

    fcstep = datetime.timedelta(hours=1)

    # offset of first forecast step relative to fcinit
    fcstart_offset = datetime.timedelta(hours=1)

    # maximum forecast step relative to fcinit
    fcend_offset = datetime.timedelta(hours=97)

    # dimensions
    dims = [('t', None), ('z', 20), ('y', 321), ('x', 281)]

    species = {'O3': dict(varname='D3_ug_O3', urlname=''),
               'NO2': dict(varname='D3_ug_NO2', urlname=''),
               'PM25': dict(varname='D3_ug_PM25_wet', urlname=''),
               'PM10': dict(varname='D3_ug_PM10_wet', urlname=''),
               'NO': dict(varname='D3_ug_NO', urlname=''),
               'SO2': dict(varname='D3_ug_SO2', urlname=''),
               'CO': dict(varname='D3_ug_CO', urlname='co'),
               'NH3': dict(varname='D3_ug_NH3', urlname=''),
               'PANS': dict(varname='D3_ug_PAN', urlname=''),
               'NMVOC': dict(varname='D3_ug_NMVOC', urlname=''),
               'AIR_PRESSURE': dict(varname='PS', urlname='pressure'),
               }

    needed_vars = ['lon', 'lat', 'lev', 'hyam', 'hybm', 'time']

    aggdim = 'time'

    concentration_type = 'mass'
    quantity_type = 'concentration'
    layer_type = 'ml'

    name = 'EMEP'
    need_to_convert_to_nc4c = True

    dimensions_no_copy = ['ilev']

    def get_dims(self, species):
        dimsize = copy.deepcopy(self.dims)
        if species == 'AIR_PRESSURE':  # air pressure doesn't have z dimension
            dimsize = [(k, v) for k, v in dimsize if k != 'z']
        dimsize = OrderedDict(dimsize)
        return dimsize

    def fix_dataset(self, fn_out, species, fcinit):
        with Dataset(fn_out, 'a', format='NETCDF4_CLASSIC') as nc:
            # convert time to hours since fcinit
            t_obj = num2date(nc.variables['time'][:],
                             nc.variables['time'].units)
            t_unit = 'hours since {:%Y-%m-%dT%H:%M:%S}'.format(fcinit)
            nc.variables['time'][:] = date2num(t_obj, t_unit)
            nc.variables['time'].setncattr('units', t_unit)
            nc.variables['time'].setncattr('standard_name', 'time')

            # MSS doesn't like it when the vertical coordinate dimension,
            # after being cast to int, isn't unique. EMEP has values 0..1,
            # so we just overwrite these values with 1..20 here
            v_lev = nc.variables['lev']
            v_lev[:] = np.arange(v_lev[:].size) + 1

            # set standard name of data variable
            self.set_standard_name(nc, species)
            # TODO can we make a generic function for this?
            # calculate air pressure
            if species == 'AIR_PRESSURE':
                a_ = nc.variables['hyam'][:]
                b_ = nc.variables['hybm'][:]
                ps_ = nc.variables['PS'][:]
                nc.variables['PS'].setncattr('standard_name',
                                             'surface_air_pressure')
                # calculate air_pressure
                p_ = (a_[np.newaxis, :, np.newaxis, np.newaxis] +
                      b_[np.newaxis, :, np.newaxis, np.newaxis] *
                      ps_[:, np.newaxis, :, :]) * 100.
                # write air_pressure to file
                nc.createVariable(
                    'P', p_.dtype, ('time', 'lev', 'lat', 'lon'),
                    zlib=True,
                    complevel=6, shuffle=True, fletcher32=True)
                nc.variables['P'][:] = p_
                # set air_pressure attributes
                nc.variables['P'].setncattr('standard_name', 'air_pressure')
                nc.variables['P'].setncattr('units', 'Pa')
                # delete surface pressure variable
                del nc.variables['PS']

    def write_dataset(self, varname_species, fns_in, fn_out):
        # TODO make generic method more generic, to make special case obsolete
        with Dataset(fn_out, 'w', format='NETCDF4_CLASSIC') as nc_out, Dataset(fns_in[0], 'r') as nc_in:
            # copy dimensions
            self.copy_dimensions(nc_in, nc_out)

            # copy global attributes
            self.copy_global_attrs(nc_in, nc_out)

            # copy variables
            self.copy_vars(nc_in, nc_out, varname_species)
