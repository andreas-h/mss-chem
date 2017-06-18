***********************
Developer documentation
***********************

Contributing
============

Any contributions to this project are welcome!  The source code is hosted at
Github: https://github.com/andreas-h/mss-chem .


MSS-Chem architecture
=====================

MSS-Chem does two things:

1. Download CTM forecasts
2. Process CTM forecast files so that they can be used by MSS's
   ``MSSChemDataAccess`` class.


Data download
-------------


Data processing
---------------

The ``postprocess`` function is run for each species/forecast-run pair, with a
list of all downloaded data files as extra argument.  It does the following
things:

1. Create an output filename
2. Create the output directory, if it does not already exist
3. Combine all output files for this species/forecast-run pair into one file
4. Patch this one output file so that it adheres to the metadata standards
   expected by MSS's ``MSSChemDataAccess`` class.


Running tests
=============

Preparation
-----------

.. code:: sh

   conda create -nmsschem-dev python=2 jpeg=8 mss

