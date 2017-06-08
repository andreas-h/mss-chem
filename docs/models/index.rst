*****************************************************
Atmospheric chemistry models integrated into mss-chem
*****************************************************

.. toctree::
   :hidden:

   cams_global
   cams_regional
   silam


The following CTMs are integrated into *mss-chem*:

====================  ===========  ======  ==========  ========  ==========================
Model                 Institute    Domain  resolution  # layers  forecast (step / duration)
====================  ===========  ======  ==========  ========  ==========================
:doc:`cams_global`    Copernicus_  global  0.4°        60        3h / 120h
:doc:`cams_regional`  Copernicus_  Europe  0.1°        8         1h / 96h
:doc:`silam`          FMI_         Europe  0.1°        10        1h / 120h
====================  ===========  ======  ==========  ========  ==========================


.. _Copernicus:  http://copernicus.eu/
.. _SILAM: http://silam.fmi.fi/
.. _FMI: http://en.ilmatieteenlaitos.fi/
