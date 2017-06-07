import datetime
import os.path
import unittest
import urllib

from msschem.models import CAMSRegDriver
from msschem.download import CAMSRegDownload

import msschem_settings


class TestCAMSRegDriver(unittest.TestCase):

    def setUp(self):
        self.driver = msschem_settings.register_datasources['CAMSReg_ENSEMBLE']
        yesterday = datetime.date.today() - datetime.timedelta(0)
        self.fcinit = datetime.datetime(yesterday.year, yesterday.month, yesterday.day)

    def test_get_nt(self):

        dr = self.driver

        init = datetime.datetime(2017, 2, 15, 0, 0)

        start = datetime.datetime(2017, 2, 15, 0, 0)
        end = datetime.datetime(2017, 2, 15, 1, 0)
        self.assertEqual(dr.get_nt(init, start, end), 25)

        start = datetime.datetime(2017, 2, 15, 0, 0)
        end = datetime.datetime(2017, 2, 16, 0, 0)
        self.assertEqual(dr.get_nt(init, start, end), 25)

        start = datetime.datetime(2017, 2, 15, 0, 0)
        end = datetime.datetime(2017, 2, 16, 1, 0)
        self.assertEqual(dr.get_nt(init, start, end), 49)

        start = datetime.datetime(2017, 2, 16, 0, 0)
        end = datetime.datetime(2017, 2, 17, 0, 0)
        self.assertEqual(dr.get_nt(init, start, end), 49)

        start = datetime.datetime(2017, 2, 16, 1, 0)
        end = datetime.datetime(2017, 2, 17, 0, 0)
        self.assertEqual(dr.get_nt(init, start, end), 24)

        start = datetime.datetime(2017, 2, 15, 3, 0)
        end = datetime.datetime(2017, 2, 18, 7, 0)
        self.assertEqual(dr.get_nt(init, start, end), 97)

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
        self.driver.get('NO2', self.fcinit)


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
