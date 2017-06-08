*************
CAMS (global)
*************

The `Copernicus Atmosphere Monitoring Service (CAMS)`_ uses a comprehensive
global monitoring and forecasting system that estimates the state of the
atmosphere on a daily basis, combining information from models and observations,
and it provides a daily 5-day forecast.


Available species
=================

The following species are available from CAMS regional data:

=======  ===============  =============================================
Species  Parameter value  Description
=======  ===============  =============================================
lnsp     AIR_PRESSURE     Logarithm of surface pressure
aermr01                   Sea Salt Aerosol (0.03 - 0.5 um) Mixing Ratio
aermr02                   Sea Salt Aerosol (0.5 - 5 um) Mixing Ratio
aermr03                   Sea Salt Aerosol (5 - 20 um) Mixing Ratio
aermr04                   Dust Aerosol (0.03 - 0.55 um) Mixing Ratio
aermr05                   Dust Aerosol (0.55 - 0.9 um) Mixing Ratio
aermr06                   Dust Aerosol (0.9 - 20 um) Mixing Ratio
aermr07                   Hydrophobic Organic Matter Aerosol Mixing Ratio
aermr08                   Hydrophilic Organic Matter Aerosol Mixing Ratio
aermr09                   Hydrophobic Black Carbon Aerosol Mixing Ratio
aermr10                   Hydrophilic Black Carbon Aerosol Mixing Ratio
aermr11                   Sulphate Aerosol Mixing Ratio
no2      NO2              Nitrogen dioxide
so2      SO2              Sulphur dioxide
co       CO               Carbon monoxide
hcho     HCHO             Formaldehyde
go3      O3               GEMS Ozone
ch4      CH4              Methane
hno3     HNO3             Nitric acid
pan      PANS             Peroxyacetyl nitrate
c5h8                      Isoprene
no       NO               Nitrogen monoxide
oh       OH               Hydroxyl radical
c2h6                      Ethane
c3h8                      Propane
=======  ===============  =============================================

.. warning::

   Not all these species have been implemented for MSS-Chem yet.  If you receive
   errors trying to download a species, please open a `Github issue
   <https://github.com/andreas-h/mss-chem/issues/new>`__ and I will promptly add
   it to the code base.

In order to include a species in the download, add the species' *Parameter
value* to the ``species`` list in the configuration.


Configuration
=============

In order to download CAMS global data, MSS-Chem must be configured as follows::

   import os.path
   
   from msschem.models import CAMSRegDriver
   from msschem.download import CAMSRegDownload
   
   register_datasources = {
       'CAMSGlob': CAMSGlobDriver(
           dict(
               dldriver=CAMSGlobDownload(
                   username="MYUSERNAME",
                   password="MYPASSWORD",
                   host="dissemination.ecmwf.int",
                   n_tries=1),
               force=False,
               basepath=os.path.expanduser('~/tmp/mss/data/'),
               name='CAMSGlob',
               temppath=None,
               species=['CO', 'O3', 'HCHO', 'HNO3', 'NO', 'NO2', 'OH', 'PANS',
                        'SO2'],
           )
       ),
   }


Data access
===========

CAMS global forecast data can be accessed via an `FTP service
<http://atmosphere.copernicus.eu/ftp-access-global-data>`__.  Access is free of
charge, but requires accepting a data license.  ECMWF will then e-mail you a
username and a password, both to be used in the MSS-Chem configuratiion (see
above).

.. _`Copernicus Atmosphere Monitoring Service (CAMS)`:  http://atmosphere.copernicus.eu/
