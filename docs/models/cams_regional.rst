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
