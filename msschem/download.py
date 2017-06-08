# -*- coding: utf-8 -*-

from __future__ import with_statement

from collections import OrderedDict
from contextlib import closing
import datetime
from ftplib import FTP, FTP_TLS
import os.path
import re
import shutil

try:  # Py2
    from urllib import urlencode
    from urllib2 import urlopen
except ImportError:  # Py3
    from urllib.parse import urlencode
    from urllib.request import urlopen


"""****************
msschem.download
****************

This module provides functions downloading CTM chemical forecasts

This file is part of mss-chem.

:copyright: Copyright 2017 Andreas Hilboll
:copyright: Copyright 2017 by the mss-chem team, see AUTHORS.rst
:license: APACHE-2.0, see LICENSE for details.

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

"""

"""
*****
NOTES
*****

- SILAM download URLs:

  http://silam.fmi.fi/thredds/ncss/silam_europe_v5_5/runs/silam_europe_v5_5_RUN_2017-03-31T00:00:00Z?disableLLSubset=on&disableProjSubset=on&horizStride=1&time_start=2017-03-31T01%3A00%3A00Z&time_end=2017-04-05T00%3A00%3A00Z&timeStride=1&vertCoord=&accept=netcdf
  http://silam.fmi.fi/thredds/ncss/silam_europe_v5_5/runs/silam_europe_v5_5_RUN_2017-03-31T00:00:00Z?disableLLSubset=on&disableProjSubset=on&horizStride=1&time_start=2017-03-31T01%3A00%3A00Z&time_end=2017-04-05T00%3A00%3A00Z&timeStride=1&vertCoord=&addLatLon=true&accept=netcdf

  http://silam.fmi.fi/thredds/ncss/silam_europe_v5_5/runs/silam_europe_v5_5_RUN_2017-03-31T00:00:00Z?var=cnc_NO2_gas&disableLLSubset=on&disableProjSubset=on&horizStride=1&time_start=2017-03-31T01%3A00%3A00Z&time_end=2017-04-05T00%3A00%3A00Z&timeStride=1&vertCoord=&accept=netcdf
  http://silam.fmi.fi/thredds/ncss/silam_europe_v5_5/runs/silam_europe_v5_5_RUN_2017-03-31T00:00:00Z?var=cnc_NO2_gas&disableLLSubset=on&disableProjSubset=on&horizStride=1&time_start=2017-03-31T01%3A00%3A00Z&time_end=2017-04-05T00%3A00%3A00Z&timeStride=1&vertCoord=&addLatLon=true&accept=netcdf


****
TODO
****

- [ ] foresee timeout setting (SILAM)
- [ ] check if data are all available (CAMS global manifest)


"""


class DownloadDriver(object):
    pass


class FTPDownload(DownloadDriver):

    conn = None

    def construct_urls(self, params):
        raise NotImplementedError(
                '"construct_urls()" must be implemented for the "{}" class'
                ''.format(self.__class__))

    @staticmethod
    def download_file(url, fn):
        # download recipe from http://stackoverflow.com/a/7244263
        with urlopen(url) as resp, open(os.path.expanduser(fn), 'wb') as out:
            shutil.copyfileobj(resp, out)

    def filter_files(self, fns, species, fcinit, fcstart, fcend):
        """Filter a list of filenames for those relevant to this download
        """
        raise NotImplementedError()

    def login(self):
        if self.conn is not None:  # TODO better test for working connection
            print('Connection already established')
            return
        self.conn = self.ftpobj(self.host, self.username, self.password)
        self.conn.set_pasv(self.passive)

    def logout(self):
        self.conn.close()
        self.conn = None

    def get(self, species, fcinit, fcstart, fcend, fn_out):
        """Download all files for a given species / init_time

        Parameters
        ----------
        fn_out : str
            Dummy filename of output file.  For a value of
            ``/PATH/TO/MYFILE.nc``, the actual output files will be called
            ``/PATH/TO/MYFILE_NN.nc``, where ``_NN`` is a counter.

        Returns
        -------
        fns : list of str
            A list of all files which have been downloaded

        """
        # open FTP connection
        self.login()

        # change to correct directory
        ftpdir = self.path.format(species=species, fcinit=fcinit, fcend=fcend)
        self.conn.cwd(ftpdir)

        # get a list of all files to retrieve
        ftpallfiles = self.conn.nlst()
        ftpfiles = self.filter_files(ftpallfiles, species, fcinit, fcstart,
                                     fcend)

        # prepare output filename construction
        path, ext = os.path.splitext(fn_out)

        # retrieve all files
        outfiles = []
        for i, fn in enumerate(ftpfiles):
            fn_out = path + '_{:03d}'.format(i) + ext
            with open(fn_out, 'wb') as fd:
                # TODO make fault tolerant
                self.conn.retrbinary('RETR {}'.format(fn), fd.write)
            outfiles.append(fn_out)

        # close FTP connection
        self.logout()

        return outfiles

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
        # TODO make fault tolerant
        with closing(urlopen(url)) as resp, open(os.path.expanduser(fn), 'wb') as out:
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
    # Data download, as defined under "Online data" on
    # http://www.regional.atmosphere.copernicus.eu/ the token is available
    # directly on the CAMS website; when one clicks on "Accept license", the
    # URL generated contains this token.  So this is no secret!
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

    # TODO implement check? available_from_time = datetime.time(11, 30)

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
    ftpobj = FTP
    host = "dissemination.ecmwf.int"
    path = '/DATA/CAMS_NREALTIME/{fcinit:%Y%m%d%H}'
    fnpattern = ('z_cams_c_ecmf_{fcinit:%Y%m%d%H%M%S}_prod_{fctype}_'
                 '{layer_type}_(\d{{3}})_{species}.nc')
    layer_type = 'ml'  # TODO make this configurable
    fctype = 'fc'  # TODO make this configurable

    def filter_files(self, fns, species, fcinit, fcstart, fcend):
        manifest = 'z_cams_c_ecmf_{:%Y%m%d%H}0000_prod.manifest'.format(fcinit)
        if manifest not in fns:
            raise ValueError('Manifest file doesn\'t exist yet')
        allfiles = {}
        pattern = self.fnpattern.format(fcinit=fcinit, fctype=self.fctype,
                                        layer_type=self.layer_type,
                                        species=species)
        for fn in fns:
            m = re.match(pattern, fn)
            if m:
                allfiles[m.group(1)] = fn
        files = OrderedDict(sorted(allfiles.items(), key=lambda t: t[0]))

        result = [f for t, f in files.items()
                  if fcstart <= fcinit + datetime.timedelta(hours=int(t))
                             <= fcend]
        return result
