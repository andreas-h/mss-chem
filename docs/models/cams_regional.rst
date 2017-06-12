***************
CAMS (regional)
***************

The `regional air quality (RAQ) production`_ of the `Copernicus Atmosphere
Monitoring Service (CAMS)`_ is based on seven state-of-the-art numerical air
quality models developed in Europe : CHIMERE from INERIS (France), EMEP from MET
Norway (Norway), EURAD-IM from University of Cologne (Germany), LOTOS-EUROS from
KNMI and TNO (Netherlands), MATCH from SMHI (Sweden), MOCAGE from METEO-FRANCE
(France) and SILAM from FMI (Finland). Common to all models, the meteorological
parameters settings (coming from the ECMWF global weather operating sytem), the
boundary conditions for chemical species (coming fron the CAMS IFS-MOZART global
production), the emissions coming from CAMS emission (for anthropic emissions
over Europe and for biomass burning).


Available species
=================

The following species are available from CAMS regional data:

=======  ===============
Species  Parameter value
=======  ===============
CO       CO
NH3      NH3
NMVOC    NMVOC
NO       NO
NO2      NO2
O3       O3
PAN      PANS
PM10     PM10
PM2.5    PM25
=======  ===============


Configuration
=============

In order to download CAMS regional data, MSS-Chem must be configured as
follows::

   import os.path
   
   from msschem.models import CAMSRegDriver
   from msschem.download import CAMSRegDownload
   
   register_datasources = {
       'CAMSReg_ENSEMBLE': CAMSRegDriver(
           dict(
               dldriver=CAMSRegDownload(
                   password='MYTOKEN',
                   modelname='ENSEMBLE',
                   n_tries=3),
               force=False,
               basepath=os.path.expanduser('~/tmp/mss/data/'),
               name='CAMSReg-ENSEMBLE',
               temppath=None,
               species=['CO', 'NH3', 'NMVOC', 'NO2', 'NO', 'O3', 'PANS', 'PM10',
                        'PM25', 'SO2'],
           )
       ),
   }

The ``modelname`` value in the ``CAMSRegDownload`` constructor must be set to
model which shall be downloaded.  The following values are supported:

- ``CHIMERE``
- ``EMEP``
- ``ENSEMBLE``
- ``EURAD-IM``
- ``LOTOS-EUROS``
- ``MATCH``
- ``MOCAGE``
- ``SILAM``

By default (i.e., if ``modelname`` is not specified), the ``ENSEMBLE`` will be
downloaded.

The ``password`` value in the ``CAMSRegDownload`` constructor must be set to the
access token of the CAMS regional website (see below on how to obtain this
token).

The ``species`` value is a list of the *Parameter values* of all species which
are to be downloaded (see above for a list of *Parameter value* s).


Data access
===========

There are two ways of accessing the CAMS Regional forecast: a web service, and a
download option.  For MSS-Chem, we use the data download option.  

When a user clicks on the "Online data" link at
http://www.regional.atmosphere.copernicus.eu/ , one can see that the token
needed for download is automatically filled into the request URL when one clicks
on "Accept license".  So this token is no secret!  The options (defined in the
``CAMSRegDownload`` class) are::

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


Web service access (not used by MSS-Chem)
-----------------------------------------

For the web service, the user has to register.  However, the web service only
offers downloading 2D fields.  In order to get the 4D fields needed by MSS
(time, level, longitude, latitude), we would need to loop over both time and
altitude.  For future reference, these are the parameters for the web service
(without implementing the level selection)::

   urlbase = ('http://geoservices.regional.atmosphere.copernicus.eu/services/CAMS50-{model}-FORECAST-01-EUROPE-WCS')
   urlparams = {'service': 'WCS',
                'token': '{token}',
                'request': 'GetCoverage',
                'version': '2.0.1',
                'coverageId': '{species}__SPECIFIC_HEIGHT_LEVEL_ABOVE_GROUND___{fcinit:%Y-%m-%dT%H:%M:%SZ}',
   }


.. _`Copernicus Atmosphere Monitoring Service (CAMS)`:  http://atmosphere.copernicus.eu/
.. _`regional air quality (RAQ) production`:  http://www.regional.atmosphere.copernicus.eu/
