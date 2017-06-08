import datetime
import os.path
import unittest

from msschem.models import SilamDriver
from msschem.download import SilamDownload

import msschem_settings


class TestSilamDriver(unittest.TestCase):

    def setUp(self):
        self.driver = msschem_settings.register_datasources['SILAM']
        yesterday = datetime.date.today() - datetime.timedelta(1)
        self.fcinit = datetime.datetime(yesterday.year, yesterday.month, yesterday.day)



    def test_get(self):
        self.driver.get('NMVOC', self.fcinit, fcend=self.fcinit + datetime.timedelta(hours=3))
        self.driver.get('PM10', self.fcinit, fcend=self.fcinit + datetime.timedelta(hours=3))
        self.driver.get('NO2', self.fcinit, fcend=self.fcinit + datetime.timedelta(hours=3))
        self.driver.get('AIR_PRESSURE', self.fcinit, fcend=self.fcinit + datetime.timedelta(hours=3))


if __name__ == '__main__':
    unittest.main()
