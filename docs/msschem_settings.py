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

