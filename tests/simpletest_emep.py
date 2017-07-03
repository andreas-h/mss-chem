import datetime
import unittest
import urllib

from msschem.models import CAMSRegDriver

import msschem_settings


class TestEMEPDriver(unittest.TestCase):

    def setUp(self):
        self.driver = msschem_settings.datasources['EMEP']
        yesterday = datetime.date.today() - datetime.timedelta(0)
        self.fcinit = datetime.datetime(yesterday.year, yesterday.month, yesterday.day)
        self.testnc4fns = ['/home2/hilboll/code/mss-chem/tmp/tmp3cmptd45_000.nc']

    @unittest.skip('This takes too long ...')
    def test_postprocess(self):
        dr = self.driver
        #dr.postprocess('NO2',
        #               datetime.datetime(2017, 5, 8),
        #               ['/home2/hilboll/tmp/msschem/emep/CWF_12FCe-20170508_hourInst.nc'])
        dr.postprocess('AIR_PRESSURE',
                       datetime.datetime(2017, 7, 2),
                       ['/home2/hilboll/code/mss-chem/tmp/tmpbjmm3z5z.nc'])
                       #['/home2/hilboll/tmp/msschem/emep/CWF_12FCe-20170508_hourInst.nc'])

    #@unittest.skip('This takes too long ...')
    def test_get(self):
        #self.driver.get('NO2', self.fcinit)
        self.driver.get('AIR_PRESSURE', self.fcinit)

    @unittest.skip('This takes too long ...')
    def test_nc4c(self):
        dr = self.driver
        dr.convert_dl_to_nc4c(self.testnc4fns)

if __name__ == '__main__':
    unittest.main()
