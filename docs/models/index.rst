*****************************************************
Atmospheric chemistry models integrated into mss-chem
*****************************************************

.. toctree::
   :hidden:

   cams_regional
   silam


The following CTMs are integrated into *mss-chem*:

====================  ===========  ======  ==========  ========  ==========================
Model                 Institute    Domain  resolution  # layers  forecast (step / duration)
====================  ===========  ======  ==========  ========  ==========================
`CAMS (global)`_      Copernicus_  global  0.4°        60        3h / 120h
:doc:`cams_regional`  Copernicus_  Europe  0.1°        8         1h / 96h
:doc:`silam`          FMI_         Europe  0.1°        10        1h / 120h
====================  ===========  ======  ==========  ========  ==========================


.. _`CAMS (global)`:  http://atmosphere.copernicus.eu/
.. _Copernicus:  http://copernicus.eu/
.. _SILAM: http://silam.fmi.fi/
.. _FMI: http://en.ilmatieteenlaitos.fi/
