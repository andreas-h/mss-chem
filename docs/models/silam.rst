*****
SILAM
*****

SILAM_, the *System for Integrated modeLling of Atmospheric coMposition*, is a
global-to-meso-scale dispersion model developed for atmospheric composition, air
quality, and emergency decision support applications, as well as for inverse
dispersion problem solution.

The model incorporates both Eulerian and Lagrangian transport routines, 8
chemico-physical transformation modules (basic acid chemistry and secondary
aerosol formation, ozone formation in the troposphere and the stratosphere,
radioactive decay, aerosol dynamics in the air, pollen transformations), 3- and
4-dimensional variational data assimilation modules.

SILAM source terms include point- and area- source inventories, sea salt,
wind-blown dust, natural pollen, natural volatile organic compounds, nuclear
explosion, as well as interfaces to ship emission system STEAM and fire
information system IS4FRIES.


Data access
===========

Data access is realized with the `NetCDF Subset Service`_.  The most recent two
forecasts are available on a rolling basis.  The request can be constructed
`interactively
<http://silam.fmi.fi/thredds/catalog/silam_europe_v5_5/runs/catalog.html>`__; an
example request looks like this:

   http://silam.fmi.fi/thredds/ncss/silam_europe_v5_5/runs/silam_europe_v5_5_RUN_2017-02-15T00:00:00Z?var=cnc_HCHO_gas&var=cnc_HNO3_gas&var=pressure&disableLLSubset=on&disableProjSubset=on&horizStride=1&time_start=2017-02-15T01%3A00%3A00Z&time_end=2017-02-20T00%3A00%3A00Z&timeStride=1&vertStride=1&addLatLon=true&accept=netcdf4


.. _SILAM: http://silam.fmi.fi/
.. _FMI: http://en.ilmatieteenlaitos.fi/
.. _`NetCDF Subset Service`:  https://www.unidata.ucar.edu/software/thredds/current/tds/reference/NetcdfSubsetServiceReference.html


Available species
=================

As of 08 June 2017, the following species are available from the SILAM model
(all on with altitude levels 12.5 50.0 125.0 275.0 575.0 1150.0 2125.0 3725.0
5725.0 7725.0 m):

===================  ===================================
Variable             Description
===================  ===================================
 air_dens            Air density [kg/m3] 
 cnc_ALD2_gas        Concentration in air ALD2_gas 
 cnc_C2O3_gas        Concentration in air C2O3_gas 
 cnc_C5H8_gas        Concentration in air C5H8_gas 
 cnc_CH3O2_gas       Concentration in air CH3O2_gas 
 cnc_CH3OOH_gas      Concentration in air CH3OOH_gas 
 cnc_CO_gas          Concentration in air CO_gas 
 cnc_CRES_gas        Concentration in air CRES_gas 
 cnc_CRO_gas         Concentration in air CRO_gas 
 cnc_ETH_gas         Concentration in air ETH_gas 
 cnc_H2O2_gas        Concentration in air H2O2_gas 
 cnc_HCHO_gas        Concentration in air HCHO_gas 
 cnc_HNO3_gas        Concentration in air HNO3_gas 
 cnc_HO2_gas         Concentration in air HO2_gas 
 cnc_HONO_gas        Concentration in air HONO_gas 
 cnc_MGLY_gas        Concentration in air MGLY_gas 
 cnc_N2O5_gas        Concentration in air N2O5_gas 
 cnc_NH3_gas         Concentration in air NH3_gas 
 cnc_NH415SO4_m_20   Concentration in air NH415SO4_m_20 
 cnc_NH415SO4_m_70   Concentration in air NH415SO4_m_70 
 cnc_NH4NO3_m_70     Concentration in air NH4NO3_m_70 
 cnc_NMVOC_gas       Concentration NMVOC 
 cnc_NO2_gas         Concentration in air NO2_gas 
 cnc_NO3_c_m3_0      Concentration in air NO3_c_m3_0 
 cnc_NO3_gas         Concentration in air NO3_gas 
 cnc_NO3rad_gas      Concentration in air NO3rad_gas 
 cnc_NOP_gas         Concentration in air NOP_gas 
 cnc_NO_gas          Concentration in air NO_gas 
 cnc_O1D_gas         Concentration in air O1D_gas 
 cnc_O3_gas          Concentration in air O3_gas 
 cnc_OH_gas          Concentration in air OH_gas 
 cnc_OLE_gas         Concentration in air OLE_gas 
 cnc_OPEN_gas        Concentration in air OPEN_gas 
 cnc_O_gas           Concentration in air O_gas 
 cnc_PAN_gas         Concentration in air PAN_gas 
 cnc_PAR_gas         Concentration in air PAR_gas 
 cnc_PM10            Concentration in air PM10 
 cnc_PM2_5           Concentration in air PM2_5 
 cnc_PM_FRP_m1_1     Concentration in air PM_FRP_m1_1 
 cnc_PM_FRP_m3_1     Concentration in air PM_FRP_m3_1 
 cnc_PM_FRP_m_17     Concentration in air PM_FRP_m_17 
 cnc_PM_GFAS_m_50    Concentration in air PM_GFAS_m_50 
 cnc_PM_m6_0         Concentration in air PM_m6_0 
 cnc_PM_m_50         Concentration in air PM_m_50 
 cnc_PNA_gas         Concentration in air PNA_gas 
 cnc_ROR_gas         Concentration in air ROR_gas 
 cnc_SO2_gas         Concentration in air SO2_gas 
 cnc_SO4_m_20        Concentration in air SO4_m_20 
 cnc_SO4_m_70        Concentration in air SO4_m_70 
 cnc_TO2_gas         Concentration in air TO2_gas 
 cnc_TOL_gas         Concentration in air TOL_gas 
 cnc_XO2N_gas        Concentration in air XO2N_gas 
 cnc_XO2_gas         Concentration in air XO2_gas 
 cnc_XYL_gas         Concentration in air XYL_gas 
 cnc_dust            Concentration in air dust 
 cnc_dust_m1_5       Concentration in air dust_m1_5 
 cnc_dust_m20        Concentration in air dust_m20 
 cnc_dust_m6_0       Concentration in air dust_m6_0 
 cnc_dust_m_30       Concentration in air dust_m_30 
 cnc_sslt            Concentration in air sslt 
 cnc_sslt_m20        Concentration in air sslt_m20 
 cnc_sslt_m3_0       Concentration in air sslt_m3_0 
 cnc_sslt_m9_0       Concentration in air sslt_m9_0 
 cnc_sslt_m_05       Concentration in air sslt_m_05 
 cnc_sslt_m_50       Concentration in air sslt_m_50 
 pressure            pressure [Pa] 
 temperature         temperature [K] 
===================  ===================================
