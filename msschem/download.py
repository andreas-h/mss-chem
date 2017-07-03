# -*- coding: utf-8 -*-

from __future__ import print_function, with_statement

from collections import OrderedDict
from contextlib import closing
import datetime
from distutils.version import LooseVersion
from ftplib import FTP, FTP_TLS
from ftplib import all_errors as FTP_ALL_ERRORS
import logging
import os.path
import re
import shutil
from string import Formatter

try:  # Py2
    from urllib import urlencode
    from urllib2 import urlopen
    from urllib2 import HTTPError
    import httplib as http_client
    __pymsschem__ = 2
except ImportError:  # Py3
    from urllib.parse import urlencode
    from urllib.request import urlopen
    from urllib.error import HTTPError
    import http.client as http_client
    __pymsschem__ = 3

try:
    import paramiko
    _PARAMIKO = True
except ImportError:
    _PARAMIKO = False

from . import DataNotAvailable


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

class DictFormatter(Formatter):
    # from https://stackoverflow.com/a/33621609/152439
    def __init__(self, default='{{{0}}}'):
        self.default = default

    def get_value(self, key, args, kwds):
        if isinstance(key, str):
            return kwds.get(key, self.default.format(key))
        else:
            return Formatter.get_value(key, args, kwds)


class DownloadDriver(object):
    pass


class FilesystemDownload(DownloadDriver):

    def get(self, species, fcinit, fcstart, fcend, fn_out, n_tries=1):
        """Copy all files for a given species / init_time

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
        if self.pre_filter_hook:
            fn, args = self.pre_filter_hook
            args['species'] = species
            args['fcinit'] = fcinit
            args['fcstart'] = fcstart
            args['fcend'] = fcend
            args['fn_out'] = fn_out
            args['path'] = self.path.format(species=species, fcinit=fcinit, fcend=fcend)
            args['path_out'] = os.path.split(fn_out)[0]
            args['fnpattern'] = DictFormatter().format(
                    args.get('fnpattern'), species=species, fcinit=fcinit, fcend=fcend)

            #args['fnpattern'].format(species=species, fcinit=fcinit, fcend=fcend)
            fn(**args)

        # get a list of all files to retrieve
        fullpath = self.path.format(species=species, fcinit=fcinit, fcend=fcend)
        fsallfiles = os.listdir(fullpath)
        fsfiles = self.filter_files(
                fsallfiles, species, fcinit, fcstart, fcend)
        fsfiles = [os.path.join(fullpath, f) for f in fsfiles]

        # prepare output filename construction
        path, ext = os.path.splitext(fn_out)

        # retrieve all files
        outfiles = []
        if self.do_copy:
            for i, fn in enumerate(fsfiles):
                fn_out = path + '_{:03d}'.format(i) + ext
                i_try = 0
                while i_try < n_tries:
                    try:
                        shutil.copy2(fn, fn_out)
                        break
                    except Exception:
                        i_try += 1

                outfiles.append(fn_out)
            return outfiles
        else:
            return fsfiles

    def filter_files(self, fns, species, fcinit, fcstart, fcend):
        allfiles = {}
        pattern = self.fnpattern.format(fcinit=fcinit, species=species)
        for fn in fns:
            m = re.match(pattern, fn)
            if m:
                allfiles[m.group(0)] = fn
        result = sorted(allfiles.values())
        return result

    def __init__(self, path, fnpattern, n_tries=1, do_copy=False,
                 pre_filter_hook=None):

        self.path = path
        self.fnpattern = fnpattern
        self.n_tries = n_tries
        self.do_copy = do_copy
        self.pre_filter_hook = pre_filter_hook


class SCPDownload(DownloadDriver):

    def login(self):
        # TODO: check if connection already exists
        self._ssh.connect(self.host, self.port, self.username,
                          self.password, key_filename=self.ssh_id,
                          compress=True)
        self._sshtransport = self._ssh.get_transport()
        self.conn = paramiko.SFTPClient.from_transport(self._sshtransport)

    def logout(self):
        try:
            self.conn.close()
        except:
            pass
        try:
            self._sshtransport.close()
        except:
            pass
        try:
            self._ssh.close()
        except:
            pass

    def get(self, species, fcinit, fcstart, fcend, fn_out, n_tries=1):
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
        # open SFTP connection
        self.login()

        # change to correct directory
        sftpdir = self.path.format(species=species, fcinit=fcinit, fcend=fcend)
        try:
            self.conn.chdir(sftpdir)
        except IOError as err:
            raise DataNotAvailable

        # get a list of all files to retrieve
        sftpallfiles = self.conn.listdir()
        sftpfiles = self.filter_files(
                sftpallfiles, species, fcinit, fcstart, fcend)

        # prepare output filename construction
        path, ext = os.path.splitext(fn_out)

        # retrieve all files
        outfiles = []
        for i, fn in enumerate(sftpfiles):
            fn_out = path + '_{:03d}'.format(i) + ext
            i_try = 0
            while i_try < n_tries:
                try:
                    self.conn.get(fn, fn_out)
                    break
                except Exception:
                    i_try += 1

            outfiles.append(fn_out)

        # close SFTP connection
        self.logout()

        return outfiles

    def filter_files(self, fns, species, fcinit, fcstart, fcend):
        allfiles = {}
        pattern = self.fnpattern.format(fcinit=fcinit, species=species)
        for fn in fns:
            m = re.match(pattern, fn)
            if m:
                allfiles[m.group(0)] = fn
        result = sorted(allfiles.values())
        return result

    def __init__(self, host, path, fnpattern, username=None, password=None,
                 port=22, ssh_id=None, ssh_hostkey=None,
                 ssh_unknown_hosts=False, n_tries=1):

        self.log = logging.getLogger('msschem')

        if not _PARAMIKO:
            raise ImportError('Cannot import paramiko, which is needed for '
                              'SCPDownload')
        if LooseVersion(paramiko.__version__) < LooseVersion('2.2'):
            self.log.warn('Downloading via SCP with ed25519 hostkeys won\'t '
                          'work (paramiko version < 2.2)')

        self.host = host
        self.path = path
        self.fnpattern = fnpattern
        self.username = username
        self.password = password
        if __pymsschem__ == 3:
            self.password = self.password.encode()
        self.port = port
        self.ssh_id = ssh_id
        self.n_tries = n_tries

        self._ssh = paramiko.SSHClient()
        self._ssh.load_system_host_keys()
        if ssh_hostkey is not None:
            self._ssh.load_host_keys(ssh_hostkey)
        if ssh_unknown_hosts:
            self._ssh.set_missing_host_key_policy(paramiko.WarningPolicy())
        else:
            self._ssh.set_missing_host_key_policy(paramiko.RejectPolicy())


class FTPDownload(DownloadDriver):

    conn = None

    def filter_files(self, fns, species, fcinit, fcstart, fcend):
        """Filter a list of filenames for those relevant to this download
        """
        raise NotImplementedError()

    def login(self):
        if self.conn is not None:  # TODO better test for working connection
            print('Connection already established')
            return
        self.conn = self.ftpobj(self.host)
        self.conn.set_debuglevel(0)  # TODO make this configurable
        self.conn.set_pasv(self.passive)
        self.conn.login(self.username, self.password)

    def logout(self):
        self.conn.close()
        self.conn = None

    def get(self, species, fcinit, fcstart, fcend, fn_out, n_tries=1):
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
        try:
            self.conn.cwd(ftpdir)
        except FTP_ALL_ERRORS as err:
            raise DataNotAvailable

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
            i_try = 0
            while i_try < n_tries:
                try:
                    with open(fn_out, 'wb') as fd:
                        self.conn.retrbinary('RETR {}'.format(fn), fd.write)
                    break
                except FTP_ALL_ERRORS:
                    i_try += 1

            outfiles.append(fn_out)

        # close FTP connection
        self.logout()

        return outfiles

    def __init__(self, host, passive=True, username=None, password=None,
                 n_tries=1):
        self.host = host
        self.passive = passive
        self.username = username
        self.password = password
        self.n_tries = n_tries


class HTTPDownload(DownloadDriver):

    def construct_urls(self, params):
        raise NotImplementedError(
                '"construct_urls()" must be implemented for the "{}" class'
                ''.format(self.__class__))

    def __init__(self, username='', password='', n_tries=1, **kwargs):
        self.password = password
        self.n_tries = n_tries
        for k, v in kwargs.items():
            setattr(self, k, v)

    @staticmethod
    def download_file(url, fn, n_tries=1):
        # download recipe from http://stackoverflow.com/a/7244263
        # retry recipe from https://stackoverflow.com/a/567645
        i = 0
        while i < n_tries:
            try:
                with closing(urlopen(url)) as resp, open(os.path.expanduser(fn), 'wb') as out:
                    shutil.copyfileobj(resp, out)
                break
            except http_client.IncompleteRead:
                i += 1

    def get(self, species, fcinit, fcstart, fcend, fn_out, n_tries=1):
        urls = self.construct_urls(dict(species=species, fcinit=fcinit,
                                        fcstart=fcstart, fcend=fcend),
                                   os.path.expanduser(fn_out))
        fns = []
        for url, fn in urls:
            try:
                self.download_file(url, fn, n_tries=n_tries)
                fns.append(fn)
            except HTTPError as err:
                if err.code == 404:
                    raise DataNotAvailable
                else:
                    raise
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

    def __init__(self, username='', password='', n_tries=1, **kwargs):
        super(CAMSRegDownload, self).__init__(username, password, n_tries,
                                              **kwargs)
        if self.modelname not in self._modelnames:
            raise ValueError()

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
        params['token'] = self.password
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
                 'addLatLon': 'true', 'accept': 'netcdf'}

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
            raise DataNotAvailable('Manifest file doesn\'t exist yet')
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
