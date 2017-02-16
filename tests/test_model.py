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

        dr.postprocess('CO', datetime.datetime(2017, 2, 15), ['/home2/hilboll/tmp/mss/data/tmp/tmp7yk61fce_25H48H.nc'])

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

if __name__ == '__main__':
    unittest.main()
