*****
SILAM
*****

Data access is realized with the `NetCDF Subset Service`_.  The most recent two
forecasts are available on
a rolling basis.  The request can be constructed `interactively <http://silam.fmi.fi/thredds/catalog/silam_europe_v5_5/runs/catalog.html>`__; an example request looks like this:

   http://silam.fmi.fi/thredds/ncss/silam_europe_v5_5/runs/silam_europe_v5_5_RUN_2017-02-15T00:00:00Z?var=cnc_HCHO_gas&var=cnc_HNO3_gas&var=pressure&disableLLSubset=on&disableProjSubset=on&horizStride=1&time_start=2017-02-15T01%3A00%3A00Z&time_end=2017-02-20T00%3A00%3A00Z&timeStride=1&vertStride=1&addLatLon=true&accept=netcdf4


.. _SILAM: http://silam.fmi.fi/
.. _FMI: http://en.ilmatieteenlaitos.fi/
.. _`NetCDF Subset Service`:  https://www.unidata.ucar.edu/software/thredds/current/tds/reference/NetcdfSubsetServiceReference.html