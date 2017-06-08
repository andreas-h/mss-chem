import os.path

from msschem.models import CAMSRegDriver
from msschem.download import CAMSRegDownload

from msschem.models.cams_global import CAMSGlobDriver
from msschem.download import CAMSGlobDownload

from msschem.models import SilamDriver
from msschem.download import SilamDownload

register_datasources = {
    'CAMSReg_ENSEMBLE': CAMSRegDriver(
        dict(
            dldriver=CAMSRegDownload(
                password='MYTOKEN',
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
                username="MYUSER",
                password="MYPASSWORD",
                host="dissemination.ecmwf.int"),
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
}