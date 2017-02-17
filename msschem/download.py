from collections import OrderedDict
import datetime
from ftplib import FTP
import os.path
import re
import shutil

try:  # Py2
    from urllib import urlencode
    from urllib2 import urlopen
except ImportError:  # Py3
    from urllib.parse import urlencode
    from urllib.request import urlopen


class DownloadDriver(object):
    pass


class FTPDownload(DownloadDriver):

    def construct_urls(self, params):
        raise NotImplementedError(
                '"construct_urls()" must be implemented for the "{}" class'
                ''.format(self.__class__))

    @staticmethod
    def download_files(url, fn):
        # download recipe from http://stackoverflow.com/a/7244263
        with urlopen(url) as resp, open(os.path.expanduser(fn), 'wb') as out:
            shutil.copyfileobj(resp, out)

    def get(self, species, fcinit, fcstart, fcend, fn_out):
        urls = self.construct_urls(dict(species=species, fcinit=fcinit,
                                        fcstart=fcstart, fcend=fcend),
                                   os.path.expanduser(fn_out))
        fns = []
        for url, fn in urls:
            self.download_file(url, fn)
            fns.append(fn)
        return fns

    def __init__(self, host, passive=True, username=None, password=None):
        self.host = host
        self.passive = passive
        self.username = username
        self.password = password


class HTTPDownload(DownloadDriver):

    def construct_urls(self, params):
        raise NotImplementedError(
                '"construct_urls()" must be implemented for the "{}" class'
                ''.format(self.__class__))

    @staticmethod
    def download_file(url, fn):
        # download recipe from http://stackoverflow.com/a/7244263
        with urlopen(url) as resp, open(os.path.expanduser(fn), 'wb') as out:
            shutil.copyfileobj(resp, out)

    def get(self, species, fcinit, fcstart, fcend, fn_out):
        urls = self.construct_urls(dict(species=species, fcinit=fcinit,
                                        fcstart=fcstart, fcend=fcend),
                                   os.path.expanduser(fn_out))
        fns = []
        for url, fn in urls:
            self.download_file(url, fn)
            fns.append(fn)
        return fns


class CAMSRegDownload(HTTPDownload):
    urlbase = ('http://download.regional.atmosphere.copernicus.eu/services/'
               'CAMS50')
    urlparams = {'token': '{token}',
                 'grid': '0.1',
                 'model': '{model}',
                 'package': 'FORECAST_{species}_ALLLEVELS',
                 'time': '{fcrange}',
                 'referencetime': '{fcinit:%Y-%m-%dT%H:%M:%SZ}',
                 'format': 'NETCDF',
                 'licence': 'yes'}

    _modelnames = ['CHIMERE', 'EMEP', 'ENSEMBLE', 'EURAD', 'LOTOSEUROS',
                   'MATCH', 'MOCAGE', 'SILAM']

    def __init__(self, token='', modelname='ENSEMBLE'):
        if modelname not in self._modelnames:
            raise ValueError()
        self.modelname = modelname
        self.token = token

    def construct_urls(self, params, fn_out):
        now = params['fcstart']
        fcrange = []
        while now <= params['fcend']:
            delta = (now - params['fcinit']).total_seconds() / 3600
            if delta <= 24.:
                if fcrange.count('0H24H') == 0:
                    fcrange.append('0H24H')
            elif delta <= 48.:
                if fcrange.count('25H48H') == 0:
                    fcrange.append('25H48H')
            elif delta <= 72.:
                if fcrange.count('49H72H') == 0:
                    fcrange.append('49H72H')
            elif delta <= 96.:
                if fcrange.count('73H96H') == 0:
                    fcrange.append('73H96H')
            else:
                raise ValueError(delta, fcrange)
            now += datetime.timedelta(hours=1)

        urls = []
        params['model'] = self.modelname
        params['token'] = self.token
        for step in fcrange:
            params['fcrange'] = step
            urlparams = {k: v.format(**params)
                         for k, v in self.urlparams.items()}
            urlbase = self.urlbase.format(**params)
            path, ext = os.path.splitext(fn_out)
            fn = path + '_{}'.format(step) + ext
            urls.append((urlbase + '?' + urlencode(urlparams), fn))

        return urls


class SilamDownload(HTTPDownload):
    urlbase = ('http://silam.fmi.fi/thredds/ncss/silam_europe_v5_5/runs/'
               'silam_europe_v5_5_RUN_{fcinit:%Y-%m-%dT%H:%M:%SZ}')

    urlparams = {'var': '{species}', 'disableLLSubset': 'on',
                 'disableProjSubset': 'on', 'horizStride': '1',
                 'time_start': '{fcstart:%Y-%m-%dT%H:%M:%SZ}', ''
                 'time_end': '{fcend:%Y-%m-%dT%H:%M:%SZ}',
                 'timeStride': '1', 'vertStride': '1',
                 'addLatLon': 'true', 'accept': 'netcdf4'}

    def construct_urls(self, params, fn_out):
        urlparams = {k: v.format(**params) for k, v in self.urlparams.items()}
        urlbase = self.urlbase.format(**params)
        return [(urlbase + '?' + urlencode(urlparams), fn_out)]


class CAMSGlobDownload(FTPDownload):
    host = "dissemination.ecmwf.int"
    path = '/DATA/CAMS_NREALTIME/{fcinit:%Y%m%d%H}'
    fnpattern = ('z_cams_c_ecmf_{fcinit:%Y%m%d%H%M%S}_prod_{fctype}_{levtype}_'
                 '(\d{3})_{species}.nc')

    def filter_files(self, fns, species, fcinit, fcstart, fcend, levtype,
                     fctype):
        allfiles = {}
        pattern = self.fnpattern.format(fcinit=fcinit, fctype=fctype,
                                        levtype=levtype, species=species)
        for fn in fns:
            m = re.match(pattern, fn)
            if m:
                allfiles[m.group(1)] = fn
        files = OrderedDict(sorted(allfiles.items(), key=lambda t: t[0]))

        return [f for t, f in files.items()
                if fcstart <= fcinit + datetime.timedelta(hours=t) <= fcend]
