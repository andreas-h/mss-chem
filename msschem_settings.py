import os.path

from msschem.models import CAMSRegDriver
from msschem.download import CAMSRegDownload

from msschem.models import CAMSGlobDriver
from msschem.download import CAMSGlobDownload

register_datasources = {
    'CAMSReg_ENSEMBLE': CAMSRegDriver(
        dict(
            dldriver=CAMSRegDownload(
                token='MYTOKEN',
                modelname='ENSEMBLE'),
            force=False,
            basepath=os.path.expanduser('~/tmp/mss/data/'),
            name='CAMSReg-ENSEMBLE',
            temppath=None,
        )
    )
    'CAMSGlob': CAMSGlobDriver(
        dict(
            dldriver=CAMSGlobDownload(
                username="MYUSER"
                password="MYPASSWORD"
                host="dissemination.ecmwf.int"),
            force=False,
            basepath=os.path.expanduser('~/tmp/mss/data/'),
            name='CAMSGlob',
            temppath=None,
        )
    )
}
