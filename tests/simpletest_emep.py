import datetime
import unittest
import urllib

from msschem.models import CAMSRegDriver

import msschem_settings


class TestEMEPDriver(unittest.TestCase):

    def setUp(self):
        self.driver = msschem_settings.register_datasources['EMEP']

    @unittest.skip('This takes too long ...')
    def test_postprocess(self):
        dr = self.driver
        #dr.postprocess('NO2',
        #               datetime.datetime(2017, 5, 8),
        #               ['/home2/hilboll/tmp/msschem/emep/CWF_12FCe-20170508_hourInst.nc'])
        dr.postprocess('AIR_PRESSURE',
                       datetime.datetime(2017, 5, 8),
                       ['/home2/hilboll/tmp/msschem/emep/CWF_12FCe-20170508_hourInst.nc'])

if __name__ == '__main__':
    unittest.main()
