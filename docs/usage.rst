*******************
How to use MSS-Chem
*******************

Installation
============

::

   pip install

.. todo:: add pip command line


Dependencies
------------

MSS-Chem works with both Python2.7 and Python3.4+.  It needs the following
libraries to operate properly:

- netCDF4
- NumPy
- pandas


Running MSS-Chem
================

::

   usage: msschem-dl [-h] (-m MODEL | -a) [-d DATE] [-c CONFIG] [-q | -v]
   
   MSS-Chem downloader
   
   optional arguments:
     -h, --help            show this help message and exit
     -m MODEL, --model MODEL
                           Model to download
     -a, --all             Download data from all configured models
     -d DATE, --date DATE  Date to download data for (YYYY-MM-DD)
     -c CONFIG, --config CONFIG
                           MSS-Chem configuration file
     -q, --quiet           No output except for errors
     -v, --verbosity       Increase output verbosity (can be supplied multiple times)

   
Configuration of MSS-Chem
=========================

The location of a configuration file can be passed to the ``msschem-dl`` script
with the ``--config`` option.  Alternatively, MSS-Chem tries to import a module
``msschem_settings``.  In that case, the file ``msschem_settings.py`` has to be
somewhere in your ``$PYTHONPATH``.

The configuration file could look like this:

.. literalinclude:: msschem_settings.py


Configuration of MSS
====================

In ``mss_wms_settings.py``, the ``nwpaccess`` dict needs to be populated with
instances of the ``mslib.mswms.dataaccess.MSSChemDataAccess`` class::

   mslib.mswms.dataaccess.MSSChemDataAccess(
           'path', 'modelname', 'modelstr', 'layer_type'),
   
- ``path`` is the base path of the model files.  This should be set to the
  directory ``basepath`` + ``/`` + ``name``, with ``basepath`` and ``name`` from
  the MSS-Chem settings.
- ``modelname`` is the name which will be used in the MSS plots to identify this
  model.  This parameter can be chosen freely.
- ``modelstr`` is the model identifier with which the names of the netCDF files
  prepared by MSS-Chem start.  This is identical to the ``name`` parameter in
  the MSS-Chem settings.
- ``layer_type`` has to be set to either of ``ml``, ``al``, ``pl``, depending on
  the model's vertical layering (model, altitude, or pressure levels,
  respectively).

For example, the ``nwpaccess`` dict could look as follows::

   nwpaccess = {
       "CAMSglb": mslib.mswms.dataaccess.MSSChemDataAccess(
               '/path/to/CAMSGlob', "CAMSglob", "CAMSGlob", "ml"),
       "CAMSregENS": mslib.mswms.dataaccess.MSSChemDataAccess(
               '/path/to/CAMSReg-ENSEMBLE',
               "CAMSregENS", "CAMSregENS", "al"),
       "SILAM": mslib.mswms.dataaccess.MSSChemDataAccess(
               '/path/to/SILAM', "SILAM", "SILAM", "al"),
   }

Furthermore, the horizontal and vertical layers have to be configured.  The MSS *layer styles* are classes which follow the following naming scheme::

   mpl_hsec_styles.HS_MSSChemStyle_LAYERTYPE_SPECIES_QUANTITY

Here, ``LAYERTYPE`` is the ``layer_type`` from above (but in upper case),
``SPECIES`` is the species to be plotted (also in upper case), and ``QUANTITY``
identifies the quantity to be plotted.  ``QUANTITY`` can be one of

- ``mfrac`` for *mass fractions* (in kg/kg)
- ``mconc`` for *mass concentrations* (in kg/m³)

For example, the entries could look like this::

   register_horizontal_layers = [
       (mpl_hsec_styles.HS_MSSChemStyle_AL_NO2_mconc, ["CAMSregENS"]),
       (mpl_hsec_styles.HS_MSSChemStyle_ML_NO2_mfrac, ["CAMSglb"]),
       (mpl_hsec_styles.HS_MSSChemStyle_AL_NO2_mconc, ["SILAM"]),
   ]

   register_vertical_layers = [
       (mpl_vsec_styles.VS_MSSChemStyle_AL_NO2_mconc, ["CAMSregENS"]),
       (mpl_vsec_styles.VS_MSSChemStyle_ML_NO2_mfrac, ["CAMSglb"]),
       (mpl_vsec_styles.VS_MSSChemStyle_AL_NO2_mconc, ["SILAM"]),
   ]
