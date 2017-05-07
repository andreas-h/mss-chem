import datetime
import unittest
import urllib

from msschem.models import CAMSRegDriver

import msschem_settings


class TestCAMSRegDriver(unittest.TestCase):

    def setUp(self):
        self.driver = msschem_settings.register_datasources['CAMSReg_ENSEMBLE']

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


    def test_postprocess(self):

        dr = self.driver

        dr.postprocess('NO2',
                       datetime.datetime(2017, 3, 31),
                       ['/home2/hilboll/tmp/msschem/cams_regional/0H24H.nc',
                        '/home2/hilboll/tmp/msschem/cams_regional/25H48H.nc',
                        '/home2/hilboll/tmp/msschem/cams_regional/49H72H.nc',
                        '/home2/hilboll/tmp/msschem/cams_regional/73H96H.nc'])

#    def test_download(self):
#
#        dr = self.driver
#
#        init = (datetime.datetime.now() - datetime.timedelta(1)).replace(
#                hour=0, minute=0, second=0, microsecond=0)
#        start = init + datetime.timedelta(days=1, hours=1)
#        end = init + datetime.timedelta(2)
#        #import pdb; pdb.set_trace()
#
#        print(dr.download('CO', init, end, start))

class TestEMEPDriver(unittest.TestCase):

    def setUp(self):
        self.driver = msschem_settings.register_datasources['EMEP']

    def test_postprocess(self):

        dr = self.driver

        dr.postprocess('NO2',
                       datetime.datetime(2017, 3, 31),
                       ['/home2/hilboll/tmp/msschem/emep/CWF_12FCe-20170313_hourInst.nc'])
        dr.postprocess('AIR_PRESSURE',
                       datetime.datetime(2017, 3, 31),
                       ['/home2/hilboll/tmp/msschem/emep/CWF_12FCe-20170313_hourInst.nc'])

if __name__ == '__main__':
    unittest.main()
