"""
simple server config for demodata
"""
import os
import mslib.mswms.dataaccess
from mslib.mswms import mpl_hsec_styles
from mslib.mswms import mpl_vsec_styles
import mslib.mswms


_vt_cache = os.path.join(os.path.expanduser("~"), "tmp", "mss", "vt_cache")
mslib.mswms.dataaccess.valid_time_cache = _vt_cache

_datapath = os.path.join(os.path.expanduser("~"), "tmp", "mss", "data")
nwpaccess = {
#    "ecmwf_EUR_LL015": mslib.mswms.dataaccess.ECMWFDataAccess(os.path.join(_datapath, "ecmwf"), "EUR_LL015"),
    "CAMSglb": mslib.mswms.dataaccess.MSSChemDataAccess(
            os.path.join(_datapath, "CAMSGlob"),
            "CAMSglob", "cams-global", "ml"),
    "CAMSregENS": mslib.mswms.dataaccess.MSSChemDataAccess(
            os.path.join(_datapath, "CAMSReg-ENSEMBLE"),
            "CAMSregENS", "CAMSReg-ENSEMBLE", "al"),
    "SILAM": mslib.mswms.dataaccess.MSSChemDataAccess(
            os.path.join(_datapath, "SILAM"),
            "SILAM", "SILAM", "al"),
#            "CAMSregENS", "cams-regional", "al"),
}

epsg_to_mpl_basemap_table = {
    # EPSG:4326, the standard cylindrical lat/lon projection.
    4326: {"projection": "cyl"},
    77790000: {"projection": "stere", "lat_0": 90., "lon_0": 0.}
}
#
# Registration of horizontal layers.                     ###
#

# The following list contains tuples of the format (instance of
# visualisation classes, data set). The visualisation classes are
# defined in mpl_hsec.py and mpl_hsec_styles.py. Add only instances of
# visualisation products for which data files are available. The data
# sets must be defined in mss_config.py. The WMS will only offer
# products registered here.

if mpl_hsec_styles is not None:
    register_horizontal_layers = [
        # ECMWF standard pressure level products.
#        (mpl_hsec_styles.HS_TemperatureStyle_PL_01, ["ecmwf_EUR_LL015"]),
#        (mpl_hsec_styles.HS_GeopotentialWindStyle_PL, ["ecmwf_EUR_LL015"]),
#        (mpl_hsec_styles.HS_RelativeHumidityStyle_PL_01, ["ecmwf_EUR_LL015"]),
#        (mpl_hsec_styles.HS_EQPTStyle_PL_01, ["ecmwf_EUR_LL015"]),
#        (mpl_hsec_styles.HS_WStyle_PL_01, ["ecmwf_EUR_LL015"]),
#        (mpl_hsec_styles.HS_DivStyle_PL_01, ["ecmwf_EUR_LL015"]),
        # CAMS Regional standard pressure level products.
        (mpl_hsec_styles.HS_MSSChemStyle_AL_NO2_mconc, ["CAMSregENS"]),
        (mpl_hsec_styles.HS_MSSChemStyle_AL_NO2_mfrac, ["CAMSglb"]),
        (mpl_hsec_styles.HS_MSSChemStyle_AL_NO2_mconc, ["SILAM"]),
        # CAMS Global standard model level products.
#        (mpl_hsec_styles.HS_MSSChemStyle_ML_NO2_mfrac, ["CAMSglb"]),
#        (mpl_hsec_styles.HS_MSSChemStyle_ML_NO2_mfrac, ["CAMSglb"]),
#        (mpl_hsec_styles.HS_MSSChemStyle_ML_NO2_mfrac_pcontours, ["CAMSglb"]),
        #(mpl_hsec_styles.HS_MSSChemStyle_PL_NO2_mfrac, ["CAMSglb"]),
    ]

#
# Registration of vertical layers.                       ###
#

# The same as above, but for vertical cross-sections.
register_vertical_layers = None
if mpl_vsec_styles is not None:
    register_vertical_layers = [
        # ECMWF standard vertical section styles.
#        (mpl_vsec_styles.VS_CloudsStyle_01, ["ecmwf_EUR_LL015"]),
#        (mpl_vsec_styles.VS_HorizontalVelocityStyle_01, ["ecmwf_EUR_LL015"]),
#        (mpl_vsec_styles.VS_PotentialVorticityStyle_01, ["ecmwf_EUR_LL015"]),
#        (mpl_vsec_styles.VS_ProbabilityOfWCBStyle_01, ["ecmwf_EUR_LL015"]),
#        (mpl_vsec_styles.VS_VerticalVelocityStyle_01, ["ecmwf_EUR_LL015"]),
#        (mpl_vsec_styles.VS_RelativeHumdityStyle_01, ["ecmwf_EUR_LL015"]),
#        (mpl_vsec_styles.VS_SpecificHumdityStyle_01, ["ecmwf_EUR_LL015"]),
#        (mpl_vsec_styles.VS_TemperatureStyle_01, ["ecmwf_EUR_LL015"]),
        # CAMS Regional standard altitude level products.
        (mpl_vsec_styles.VS_MSSChemStyle_AL_NO2_mconc, ["CAMSregENS"]),
        (mpl_vsec_styles.VS_MSSChemStyle_AL_NO2_mfrac, ["CAMSglb"]),
        (mpl_vsec_styles.VS_MSSChemStyle_AL_NO2_mconc, ["SILAM"]),
        # CAMS Global standard model level products.
#        (mpl_vsec_styles.VS_MSSChemStyle_ML_NO2_mfrac, ["CAMSglb"]),
    ]
