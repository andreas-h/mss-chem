import datetime
import os.path
import unittest

from msschem.models.cams_global import CAMSGlobDriver
from msschem.download import CAMSGlobDownload

import msschem_settings


class TestCAMSGlobDriver(unittest.TestCase):

    def setUp(self):
        self.driver = msschem_settings.register_datasources['CAMSGlob']
        yesterday = datetime.date.today() - datetime.timedelta(1)
        self.fcinit = datetime.datetime(yesterday.year, yesterday.month, yesterday.day)


    #@unittest.skip('This takes too long ...')
    #def test_postprocess(self):

    #    dr = self.driver

    #    dr.postprocess('NO2',
    #                   datetime.datetime(2017, 3, 31),
    #                   ['/home2/hilboll/tmp/msschem/cams_regional/0H24H.nc',
    #                    '/home2/hilboll/tmp/msschem/cams_regional/25H48H.nc',
    #                    '/home2/hilboll/tmp/msschem/cams_regional/49H72H.nc',
    #                    '/home2/hilboll/tmp/msschem/cams_regional/73H96H.nc',
    #                    ])

    #def test_download(self):
    #    self.filenames_tmp = self.driver.download('NO2', self.fcinit)

    def test_get(self):
        self.driver.get('NO2', self.fcinit, fcend=self.fcinit + datetime.timedelta(hours=6))
        self.driver.get('AIR_PRESSURE', self.fcinit, fcend=self.fcinit + datetime.timedelta(hours=6))


#class TestCAMSRegDownload(unittest.TestCase):
#
#    def setUp(self):
#        self.driver = msschem_settings.register_datasources['CAMSReg_ENSEMBLE']
#
#    def test_download(self):
#        yesterday = datetime.date.today() - datetime.timedelta(1)
#        fcinit = datetime.datetime(yesterday.year, yesterday.month, yesterday.day)
#        fcstart = fcinit
#        fcend = fcstart + datetime.timedelta(4)
#        dl = self.driver.dldriver
#        dl.get('NO2', fcinit, fcstart, fcend, 'blatest1.nc')
##    def get(self, species, fcinit, fcstart, fcend, fn_out):

if __name__ == '__main__':
    unittest.main()
