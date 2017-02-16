import datetime
import unittest
import urllib

from msschem.download import CAMSRegDownload, SilamDownload

import msschem_settings


class TestCAMSRegDownload(unittest.TestCase):

    def test_construct_urls_single(self):
        required_urls = ['http://download.regional.atmosphere.copernicus.eu/services/CAMS50?&token=MYTOKEN&grid=0.1&model=ENSEMBLE&package=FORECAST_CO_ALLLEVELS&time=0H24H&referencetime=2017-02-15T00:00:00Z&format=NETCDF&licence=yes']
        required_fns = ['test_0H24H.nc']

        dl = msschem_settings.register_datasources['CAMSReg_ENSEMBLE'].cfg['dldriver']
        params = {'fcinit': datetime.datetime(2017, 2, 15, 0),
                  'fcstart': datetime.datetime(2017, 2, 15, 0),
                  'fcend': datetime.datetime(2017, 2, 16, 0),
                  'species': 'CO',}

        actual = dl.construct_urls(params, 'test.nc')
        for (act_url, act_fn), req_url, req_fn in zip(
                    actual, required_urls, required_fns):

            act_host, act_query = urllib.parse.splitquery(act_url)
            req_host, req_query = urllib.parse.splitquery(req_url)
            act_params = urllib.parse.parse_qs(act_query)
            req_params = urllib.parse.parse_qs(req_query)
            act_params.pop('token'), req_params.pop('token')
            self.assertEqual(act_fn, req_fn)
            self.assertEqual(act_host, req_host)
            self.assertEqual(act_params, req_params)

    def test_construct_urls_multiple(self):
        required_urls = ['http://download.regional.atmosphere.copernicus.eu/services/CAMS50?&token=MYTOKEN&grid=0.1&model=ENSEMBLE&package=FORECAST_CO_ALLLEVELS&time=0H24H&referencetime=2017-02-15T00:00:00Z&format=NETCDF&licence=yes',
                         'http://download.regional.atmosphere.copernicus.eu/services/CAMS50?&token=MYTOKEN&grid=0.1&model=ENSEMBLE&package=FORECAST_CO_ALLLEVELS&time=25H48H&referencetime=2017-02-15T00:00:00Z&format=NETCDF&licence=yes']
        required_fns = ['test_0H24H.nc', 'test_25H48H.nc']

        dl = msschem_settings.register_datasources['CAMSReg_ENSEMBLE'].cfg['dldriver']
        params = {'fcinit': datetime.datetime(2017, 2, 15, 0),
                  'fcstart': datetime.datetime(2017, 2, 16, 0),
                  'fcend': datetime.datetime(2017, 2, 16, 1),
                  'species': 'CO',}

        actual = dl.construct_urls(params, 'test.nc')

        for (act_url, act_fn), req_url, req_fn in zip(
                    actual, required_urls, required_fns):

            act_host, act_query = urllib.parse.splitquery(act_url)
            req_host, req_query = urllib.parse.splitquery(req_url)
            act_params = urllib.parse.parse_qs(act_query)
            req_params = urllib.parse.parse_qs(req_query)
            act_params.pop('token'), req_params.pop('token')
            self.assertEqual(act_fn, req_fn)
            self.assertEqual(act_host, req_host)
            self.assertEqual(act_params, req_params)


class TestSilamDownload(unittest.TestCase):

    def test_construct_urls(self):
        required_urls = ['http://silam.fmi.fi/thredds/ncss/silam_europe_v5_5/runs/silam_europe_v5_5_RUN_2017-02-15T00:00:00Z?var=cnc_HCHO_gas&disableLLSubset=on&disableProjSubset=on&horizStride=1&time_start=2017-02-15T01%3A00%3A00Z&time_end=2017-02-20T00%3A00%3A00Z&timeStride=1&vertStride=1&addLatLon=true&accept=netcdf4']
        required_fns = ['test.nc']

        dl = SilamDownload()
        params = {'fcinit': datetime.datetime(2017, 2, 15),
                  'fcstart': datetime.datetime(2017, 2, 15, 1),
                  'fcend': datetime.datetime(2017, 2, 20),
                  'species': 'cnc_HCHO_gas'}


        actual = dl.construct_urls(params, 'test.nc')
        for (act_url, act_fn), req_url, req_fn in zip(
                    actual, required_urls, required_fns):

            act_host, act_query = urllib.parse.splitquery(act_url)
            req_host, req_query = urllib.parse.splitquery(req_url)
            act_params = urllib.parse.parse_qs(act_query)
            req_params = urllib.parse.parse_qs(req_query)
            self.assertEqual(act_fn, req_fn)
            self.assertEqual(act_host, req_host)
            self.assertEqual(act_params, req_params)


def test_camsreg_download():
    dl = msschem_settings.register_datasources['CAMSReg_ENSEMBLE'].cfg['dldriver']
    dl.get('CO', datetime.datetime(2017, 2, 15),
           datetime.datetime(2017, 2, 16, 0),
           datetime.datetime(2017, 2, 16, 1),
           '~/tmp/mss/test_camsreg_dl.nc')


def test_silam_download():
    dl = SilamDownload()
    params = {'fcinit': datetime.datetime(2017, 2, 15),
              'fcstart': datetime.datetime(2017, 2, 15, 1),
              'fcend': datetime.datetime(2017, 2, 15, 1),
              'species': 'cnc_HCHO_gas'}

    url, fn = dl.construct_urls(params, '~/tmp/mss/test_silam_dl.nc')[0]
    dl.download_file(url, fn)


if __name__ == '__main__':
    unittest.main()
