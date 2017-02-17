from collections import OrderedDict
import datetime
import os.path
import tempfile

from netCDF4 import Dataset, MFDataset
import numpy as np

# from .download import CAMSRegDownload, SilamDownload
# from .version import __version__

species_names = {'CO': 'carbon_monoxide',
                 'CO2': 'carbon_dioxide',
                 'NH3': 'ammonia',
                 'NMVOC': 'nmvoc_expressed_as_carbon',
                 'NO': 'nitrogen_monoxide',
                 'NO2': 'nitrogen_dioxide',
                 'O3': 'ozone',
                 'PANS': 'peroxyacetyl_nitrate',
                 'PM10': 'pm10_ambient_aerosol',
                 'PM25': 'pm2p5_ambient_aerosol',
                 'SO2': 'sulfur_dioxide',
                 }


class CTMDriver(object):
    def __init__(self, cfg):
        if cfg.get('force') is None:
            cfg['force'] = False
        if cfg.get('temppath') is None:
            cfg['temppath'] = os.path.join(cfg['basepath'], 'tmp')
        if not os.path.isdir(cfg['temppath']):
            os.makedirs(cfg['temppath'])
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

    def check_download(self, fns, species, fcinit, fcstart, fcend, nt=None):
        dimsize = OrderedDict(self.dims)
        nt = self.get_nt(fcinit, fcstart, fcend)
        dimsize['t'] = nt

        varname = self.species[species]['varname']
        with MFDataset(fns, 'r') as nc:
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
        self.check_download(fns, species, fcinit, fcstart, fcend)
        return fns

    def get(self, species, fcinit, fcend=None, fcstart=None):
        fns_temp = self.download(species, fcinit, fcend, fcstart)
        self.postprocess(species, fcinit, fns_temp)
        for fn in fns_temp:
            os.remove(fn)

    def output_filename(self, species, fcinit):
        outdir = os.path.join(self.cfg['basepath'], self.cfg['name'],
                              '{:%Y-%m-%dT%H}'.format(fcinit))
        outname = 'MSSChem_{name}_{species}_{fcinit:%Y-%m-%dT%H}.nc'.format(
                name=self.cfg['name'], species=species, fcinit=fcinit)
        return os.path.join(outdir, outname)

    def postprocess(self, species, fcinit, fns):
        fn_out = self.output_filename(species, fcinit)
        dirname = os.path.dirname(fn_out)
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
        self.write_dataset(fns, fn_out)
        self.fix_dataset(fn_out, species, fcinit)

    def set_standard_name(self, nc, species):
        stdname = '{}_concentration_of_{}_in_air'.format(
                self.concentration_type, species_names[species])
        nc.variables[self.species[species]['varname']].setncattr(
                'standard_name', stdname)

    @staticmethod
    def write_dataset(fns_in, fn_out):
        with Dataset(fn_out, 'w') as nc_out, MFDataset(fns_in, 'r') as nc_in:
            # copy dimensions
            for name, dim in nc_in.dimensions.items():
                nc_out.createDimension(
                        name, None if dim.isunlimited() else dim.size)

            # copy global attributes
            for name in nc_in.ncattrs():
                nc_out.setncattr(name, nc_in.__dict__[name])

            # copy variables
            for name, var in nc_in.variables.items():
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
                    nc_out.variables[name].setncattr(attr, var.__dict__[attr])

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

        if fctime % self.fcstep:
            raise ValueError('{} is not a valid fc_{}'.format(fctime,
                                                              start_or_end))

        return fcinit + fctime

    def get_nt(self, fcinit, fcstart, fcend):
        return int((fcend - fcstart) / self.fcstep) + 1


class CAMSGlobDriver(CTMDriver):

    fcstep = datetime.timedelta(hours=3)

    # offset of first forecast step relative to fcinit
    fcstart_offset = datetime.timedelta(hours=0)

    # maximum forecast step relative to fcinit
    fcend_offset = datetime.timedelta(hours=120)

    # dimensions
    dims = [('t', None), ('z', 60), ('y', 451), ('x', 900)]

    species = {'NO2': dict(varname='no2', urlname='no2'),
               }

    concentration_type = 'mass'


class CAMSRegDriver(CTMDriver):

    fcstep = datetime.timedelta(hours=1)

    # offset of first forecast step relative to fcinit
    fcstart_offset = datetime.timedelta(hours=0)

    # maximum forecast step relative to fcinit
    fcend_offset = datetime.timedelta(hours=96)

    # dimensions
    dims = [('t', None), ('z', 8), ('y', 400), ('x', 700)]

    species = {'CO': dict(varname='co_conc',
                          urlname='CO'),
               }

    concentration_type = 'mass'

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
        with Dataset(fn_out, 'a') as nc:
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
    fend_offset = datetime.timedelta(hours=120)

    # dimensions
    dims = [('t', None), ('z', 10), ('y', 420), ('x', 700)]

    species = {'HCHO': dict(varname='cnc_HCHO_gas',
                            urlname='cnc_HCHO_gas'),
               }
