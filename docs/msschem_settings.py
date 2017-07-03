import os.path

from msschem.models import CAMSRegDriver
from msschem.download import CAMSRegDownload

from msschem.models.cams_global import CAMSGlobDriver
from msschem.download import CAMSGlobDownload

from msschem.models import EMEPDriver
from msschem.download import FTPDownload

from msschem.models import SilamDriver
from msschem.download import SilamDownload

from msschem.download import SCPDownload
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
