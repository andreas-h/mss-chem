import os.path
from subprocess import check_call
from nco import Nco

from msschem import DataNotAvailable

from msschem.models import CAMSRegDriver
from msschem.download import CAMSRegDownload

from msschem.models.cams_global import CAMSGlobDriver
from msschem.download import CAMSGlobDownload

from msschem.models import EMEPDriver
from msschem.download import FTPDownload

from msschem.models import SilamDriver
from msschem.download import SilamDownload

from msschem.download import SCPDownload, FilesystemDownload
from msschem.download import DictFormatter


datasources = {
    'CAMSReg_ENSEMBLE': CAMSRegDriver(
        dict(
            dldriver=CAMSRegDownload(
                password='__M0bChV6QsoOFqHz31VRqnpr4GhWPtcpaRy3oeZjBNSg__',
                modelname='ENSEMBLE',
                n_tries=3),
            force=False,
            basepath=os.path.expanduser('~/tmp/mss/data/'),
            name='CAMSReg-ENSEMBLE',
            temppath=None,
            species=['CO', 'NH3', 'NMVOC', 'NO2', 'NO', 'O3', 'PANS', 'PM10',
                     'PM25', 'SO2'],
        )
    ),
    'CAMSGlob': CAMSGlobDriver(
        dict(
            dldriver=CAMSGlobDownload(
                username="andreas.hilboll",
                password="bMmGkpWn",
                host="dissemination.ecmwf.int",
                n_tries=1),
            force=False,
            basepath=os.path.expanduser('~/tmp/mss/data/'),
            name='CAMSGlob',
            temppath=None,
            species=['CO', 'O3', 'HCHO', 'HNO3', 'NO', 'NO2', 'OH', 'PANS',
                     'SO2'],
        )
    ),
    'SILAM': SilamDriver(
        dict(
            dldriver=SilamDownload(n_tries=1),
            force=False,
            basepath=os.path.expanduser('~/tmp/mss/data/'),
            name='SILAM',
            temppath=None,
            species=['CO', 'NO2', 'NO', 'NMVOC', 'O3', 'PANS', 'PM10', 'SO2'],
        )
    ),
    'EMEP': EMEPDriver(
        dict(
            dldriver=SCPDownload(
                host='glogin',
                path='.',
                fnpattern='CWF_12-{fcinit:%Y%m%d}_hourInst.nc',
                username='metno',
                password='EdEh2gS.'),
            force=False,
            basepath=os.path.expanduser('~/tmp/mss/data/'),
            name='EMEP',
            temppath='/home2/hilboll/code/mss-chem/tmp',
            species=['NO2', 'PM25'],
        )
    ),
}


EMEP_PERT_CITIES = ['AmsRot', 'London', 'Paris', 'PoVall', 'Ruhr']


def preprocess_emep_perturbation(**kwargs):
    
    varlist = ['D3_ug_CO', 'PS', 'hyam', 'hybm', 'P0']

    species = kwargs['species']

    options_string = ['-7', '-O']  # for NETCDF4_CLASSIC output
    nco = Nco()

    city = kwargs.get('city')
    fn_city = os.path.join(kwargs.get('path'),
                           DictFormatter().format(kwargs.get('fnpattern'),
                                                  city_id='{}_ALL_P15_'.format(city)))
    if not os.path.isfile(fn_city):
        raise DataNotAvailable
    if species == 'co':
        fn_orig = os.path.join(kwargs.get('path'), DictFormatter().format(kwargs.get('fnpattern'), city_id=''))
        if not os.path.isfile(fn_orig):
            raise DataNotAvailable
        fn_tmp_orig = os.path.join(kwargs.get('path_out'), '{}_orig.nc'.format(city))
        fn_tmp_city = os.path.join(kwargs.get('path_out'), '{}_pert.nc'.format(city))
        options_string += ['-v' + ','.join(varlist)]
        nco.ncks(input=fn_orig, output=fn_tmp_orig, options=options_string)
        nco.ncks(input=fn_city, output=fn_tmp_city, options=options_string)
        fn_out_tracer = os.path.join(kwargs.get('path_out'), 'emep_pert_{}_co.nc'.format(city))
        check_call(['ncdiff', '-7', '-O', '-vD3_ug_CO', fn_tmp_orig,
                    fn_tmp_city, fn_out_tracer])
        os.remove(fn_tmp_city)
        os.remove(fn_tmp_orig)
    elif species == 'pressure':
        options_string += ['-v' + ','.join(varlist[1:])]
        fn_out_pressure = os.path.join(kwargs.get('path_out'), 'emep_pert_{}_pressure.nc'.format(city))
        nco.ncks(input=fn_city, output=fn_out_pressure, options=options_string)
    else:
        raise ValueError

    # extract variables of interest
    # create pressure


for city in EMEP_PERT_CITIES:
    driver = EMEPDriver(
            dict(dldriver=FilesystemDownload(
                    path=os.path.expanduser('~/tmp/mss/data/tmp'),
                    fnpattern='emep_pert_{}_{{species}}.nc'.format(city),
                    do_copy=False,
                    pre_filter_hook=(preprocess_emep_perturbation,
                                     dict(city=city,
                                          fnpattern='CWF_12-{fcinit:%Y%m%d}_{city_id}hourInst.nc'))),
                                        #'/home/home/metno',
                                        #os.path.expanduser('~/tmp/mss/data/tmp'),
                                        #os.path.expanduser('~/tmp/mss/data/tmp')])),
            force=False,
            basepath=os.path.expanduser('~/tmp/mss/data/'),
            name='EMEP_' + city,
            temppath=os.path.expanduser('~/tmp/mss/data/tmp'),
            species=['CO'],
            )
    )
    driver.need_to_convert_to_nc4c = False
    driver.name = 'EMEP_' + city
    datasources['EMEP_' + city] = driver


class CAMSTracerDriver(CAMSGlobDriver):

    def fix_dataset(self, fn_out, species, fcinit):
        from netCDF4 import Dataset, num2date, date2num
        # read vertical coordinates
        with Dataset(fn_out, 'a', format='NETCDF4_CLASSIC') as nc:
            # fix time variable
            t_obj = num2date(nc.variables['time'][:],
                             nc.variables['time'].units)
            t_unit = 'hours since {:%Y-%m-%dT%H:%M:%S}'.format(fcinit)
            nc.variables['time'][:] = date2num(t_obj, t_unit)
            nc.variables['time'].setncattr('units', t_unit)
            nc.variables['time'].setncattr('standard_name', 'time')

            nc.variables['level'].setncattr('standard_name',
                                            'atmosphere_pressure_coordinate')
            # convert to Pa; otherwise, vsec plotting doesn't work
            nc.variables['level'][:] *= 100.
            nc.variables['level'].setncattr('units', 'Pa')

            self.set_standard_name(nc, species)

            # TODO add history


CAMS_TRACER = [('London', 'p26.212', '{fcinit:%Y%m%d}_tracer4emerge_pl.nc', (10, 101, 177), 'CO'),
               ('Ruhr', 'p27.212', '{fcinit:%Y%m%d}_tracer4emerge_pl.nc', (10, 101, 177), 'CO'),
               ('Berlin', 'p28.212', '{fcinit:%Y%m%d}_tracer4emerge_pl.nc', (10, 101, 177), 'CO'),
               ('PoValley', 'p29.212', '{fcinit:%Y%m%d}_tracer4emerge_pl.nc', (10, 101, 177), 'CO'),
               ('Madrid', 'p30.212', '{fcinit:%Y%m%d}_tracer4emerge_pl.nc', (10, 101, 177), 'CO'),
               ('Paris', 'p31.212', '{fcinit:%Y%m%d}_tracer4emerge_pl.nc', (10, 101, 177), 'CO'),
               ('Amsterdam', 'p33.212', '{fcinit:%Y%m%d}_tracer4emerge_pl.nc', (10, 101, 177), 'CO'),
               ('Rome', 'p34.212', '{fcinit:%Y%m%d}_tracer4emerge_pl.nc', (10, 101, 177), 'CO'),
               ('BB-NA', 'p32.212', '{fcinit:%Y%m%d}_tracer4emerge_nh_pl.nc', (10, 226, 900), 'CO'),
               ('BB-Sib', 'p25.212', '{fcinit:%Y%m%d}_tracer4emerge_nh_pl.nc', (10, 226, 900), 'CO'),
               ('O3strat', 'o3s', '{fcinit:%Y%m%d}_tracer4emerge_o3s_pl.nc', (10, 101, 177), 'O3'),
]


for name, varname, fn, dims, species in CAMS_TRACER:
    #print(name, varname, fn, dims, species)
    driver = CAMSTracerDriver(
            dict(
                dldriver=FilesystemDownload(
                    path=os.path.expanduser('/misc/gomzo2/home2/annebl/Tracer-Runs/'),
                    fnpattern=fn,
                    do_copy=False,
                    n_tries=1),
                force=False,
                basepath=os.path.expanduser('~/tmp/mss/data/'),
                name='CAMSTr_' + name,
                temppath=None,
                species=[species],
            ),
        )

    # set variable name
    driver.species = {species: dict(varname=varname, urlname=varname)}

    # set layer type
    driver.layer_type = 'pl'

    # remove AIR_PRESSURE - we don't need it for pressure_level data
    if 'AIR_PRESSURE' in driver.cfg['species']:
        driver.cfg['species'].pop(driver.cfg['species'].index('AIR_PRESSURE'))

    # set lat/lon dimensions so that sanity check doesn't fail
    driver.dims = [('t', None), ('z', dims[0]), ('y', dims[1]), ('x', dims[2])]

    assert 'CAMSTr_' + name not in datasources.keys()

    driver.name = 'CAMSTr_' + name
    datasources['CAMSTr_' + name] = driver

    driver = None
    del driver
