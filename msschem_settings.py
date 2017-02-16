import os.path

from msschem.models import CAMSRegDriver
from msschem.download import CAMSRegDownload

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
}
