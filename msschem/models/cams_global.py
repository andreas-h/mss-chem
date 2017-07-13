from __future__ import absolute_import

from collections import OrderedDict
import copy
import datetime

try:
    from StringIO import StringIO
except ImportError:
    from io import BytesIO as StringIO

from netCDF4 import Dataset, num2date, date2num
import numpy as np

from ..models import CTMDriver


CAMS_LEVELDEV_STR = """ # ECMWF L60 model level definitions, from http://www.ecmwf.int/en/forecasts/documentation-and-support/60-model-levels
n a[Pa] b ph[hPa] pf[hPa] geopot[m] alt[m] temp[K] density[kg/m**3]
0	0.000000	0.000000	0.000000	-	-	-	-	-
1	20.000000	0.000000	0.2000	0.1000	64947.31	65616.42	231.60	0.000150
2	38.425343	0.000000	0.3843	0.2921	57350.89	57872.01	252.87	0.000402
3	63.647804	0.000000	0.6365	0.5104	53125.16	53572.02	264.70	0.000672
4	95.636963	0.000000	0.9564	0.7964	49623.45	50013.12	270.65	0.001025
5	134.483307	0.000000	1.3448	1.1506	46709.58	47054.67	269.84	0.001485
6	180.584351	0.000000	1.8058	1.5753	44259.61	44569.33	262.98	0.002087
7	234.779053	0.000000	2.3478	2.0768	42156.09	42436.98	257.09	0.002814
8	298.495789	0.000000	2.9850	2.6664	40294.73	40551.28	251.88	0.003688
9	373.971924	0.000000	3.7397	3.3623	38600.97	38836.35	247.13	0.004740
10	464.618134	0.000000	4.6462	4.1930	37018.28	37234.70	242.70	0.006018
11	575.651001	0.000000	5.7565	5.2013	35500.64	35699.63	238.45	0.007599
12	713.218079	0.000000	7.1322	6.4443	34017.99	34200.66	234.30	0.009582
13	883.660522	0.000000	8.8366	7.9844	32561.15	32728.48	230.22	0.012082
14	1094.834717	0.000000	10.9483	9.8925	31127.02	31279.89	227.78	0.015130
15	1356.474609	0.000000	13.5647	12.2565	29702.74	29841.91	226.35	0.018863
16	1680.640259	0.000000	16.8064	15.1856	28287.36	28413.56	224.94	0.023518
17	2082.273926	0.000000	20.8227	18.8146	26880.84	26994.77	223.53	0.029322
18	2579.888672	0.000000	25.7989	23.3108	25483.11	25585.48	222.13	0.036557
19	3196.421631	0.000000	31.9642	28.8816	24094.12	24185.62	220.74	0.045579
20	3960.291504	0.000000	39.6029	35.7836	22713.82	22795.11	219.36	0.056826
21	4906.708496	0.000000	49.0671	44.3350	21342.15	21413.91	217.99	0.070849
22	6018.019531	0.000000	60.1802	54.6236	20014.52	20077.62	216.66	0.087826
23	7306.631348	0.000000	73.0663	66.6233	18755.37	18810.77	216.65	0.107127
24	8765.053711	0.000076	87.7274	80.3968	17563.62	17612.18	216.65	0.129274
25	10376.126953	0.000461	104.2288	95.9781	16440.20	16482.75	216.65	0.154328
26	12077.446289	0.001815	122.6137	113.4212	15381.19	15418.43	216.65	0.182375
27	13775.325195	0.005081	142.9017	132.7577	14382.89	14415.44	216.65	0.213467
28	15379.805664	0.011143	165.0886	153.9952	13441.79	13470.22	216.65	0.247616
29	16819.474609	0.020678	189.1466	177.1176	12554.62	12579.42	216.65	0.284796
30	18045.183594	0.034121	215.0251	202.0859	11718.27	11739.87	216.65	0.324943
31	19027.695313	0.051690	242.6523	228.8387	10930.02	10948.81	217.10	0.367189
32	19755.109375	0.073534	272.0593	257.3558	10175.26	10191.54	222.01	0.403822
33	20222.205078	0.099675	303.2174	287.6383	9444.61	9458.63	226.76	0.441886
34	20429.863281	0.130023	336.0439	319.6307	8737.51	8749.51	231.36	0.481280
35	20384.480469	0.164384	370.4072	353.2256	8054.20	8064.40	235.80	0.521847
36	20097.402344	0.202476	406.1328	388.2700	7395.38	7403.97	240.08	0.563389
37	19584.330078	0.243933	443.0086	424.5707	6761.89	6769.08	244.20	0.605674
38	18864.750000	0.288323	480.7907	461.8996	6154.67	6160.62	248.14	0.648445
39	17961.357422	0.335155	519.2093	500.0000	5574.58	5579.46	251.92	0.691426
40	16899.468750	0.383892	557.9734	538.5913	5022.43	5026.39	255.50	0.734331
41	15706.447266	0.433963	596.7774	577.3754	4498.91	4502.09	258.91	0.776863
42	14411.124023	0.484772	635.3060	616.0417	4004.59	4007.11	262.12	0.818729
43	13043.218750	0.535710	673.2403	654.2732	3539.96	3541.93	265.14	0.859634
44	11632.758789	0.586168	710.2627	691.7515	3105.35	3106.86	267.97	0.899295
45	10209.500977	0.635547	746.0635	728.1631	2701.00	2702.14	270.59	0.937436
46	8802.356445	0.683269	780.3455	763.2045	2327.04	2327.89	273.02	0.973801
47	7438.803223	0.728786	812.8303	796.5879	1983.49	1984.11	275.26	1.008150
48	6144.314941	0.771597	843.2634	828.0468	1670.26	1670.70	277.29	1.040270
49	4941.778320	0.811253	871.4203	857.3419	1387.12	1387.43	279.13	1.069971
50	3850.913330	0.847375	897.1118	884.2660	1133.73	1133.93	280.78	1.097099
51	2887.696533	0.879657	920.1893	908.6505	909.57	909.70	282.24	1.121533
52	2063.779785	0.907884	940.5511	930.3702	713.97	714.05	283.51	1.143192
53	1385.912598	0.931940	958.1477	949.3494	546.06	546.11	284.60	1.162039
54	855.361755	0.951822	972.9868	965.5672	404.72	404.74	285.52	1.178087
55	467.333588	0.967645	985.1399	979.0633	288.55	288.57	286.27	1.191403
56	210.393890	0.979663	994.7472	989.9435	195.85	195.85	286.88	1.202112
57	65.889244	0.988270	1002.0236	998.3854	124.48	124.48	287.34	1.210406
58	7.367743	0.994019	1007.2639	1004.6437	71.89	71.89	287.68	1.216546
59	0.000000	0.997630	1010.8487	1009.0563	34.97	34.97	287.92	1.220871
60	0.000000	1.000000	1013.2500	1012.0494	10.00	10.00	288.09	1.223803
"""


def load_vert_coord(leveldev_str):
    hy = np.genfromtxt(StringIO(CAMS_LEVELDEV_STR.encode()),
                       comments='#', delimiter='\t', skip_header=2)
    hyam = hy[1:, 1]
    hybm = hy[1:, 2]
    hyn = hy[1:, 0]
    return hyn, hyam, hybm


class CAMSGlobDriver(CTMDriver):

    fcstep = datetime.timedelta(hours=3)

    # offset of first forecast step relative to fcinit
    fcstart_offset = datetime.timedelta(hours=0)

    # maximum forecast step relative to fcinit
    fcend_offset = datetime.timedelta(hours=120)

    # dimensions
    dims = [('t', None), ('z', 60), ('y', 451), ('x', 900)]

    species = {'CO': dict(varname='co', urlname='co'),
               'O3': dict(varname='go3', urlname='go3'),
               'HCHO': dict(varname='hcho', urlname='hcho'),
               'HNO3': dict(varname='hno3', urlname='hno3'),
               'NO': dict(varname='no', urlname='no'),
               'NO2': dict(varname='no2', urlname='no2'),
               'OH': dict(varname='oh', urlname='oh'),
               'PANS': dict(varname='pan', urlname='pan'),
               'SO2': dict(varname='so2', urlname='so2'),
               # we need ln(surface_air_pressure) to derive 'air_pressure'
               # in fix_dataset() method
               'AIR_PRESSURE': dict(varname='lnsp', urlname='lnsp'),
               }

    needed_vars = ['longitude', 'latitude', 'level', 'time']

    concentration_type = 'mass'
    quantity_type = 'fraction'
    layer_type = 'ml'
    aggdim = 'time'
    name = 'CAMS_global'

    # TODO How to handle two init times per day?

    def get_dims(self, species):
        dimsize = copy.deepcopy(self.dims)
        if species == 'AIR_PRESSURE':  # air pressure doesn't have z dimension
            dimsize = [(k, v) for k, v in dimsize if k != 'z']
        dimsize = OrderedDict(dimsize)
        return dimsize

    def fix_dataset(self, fn_out, species, fcinit):
        # read vertical coordinates
        hyn, hyam, hybm = load_vert_coord(CAMS_LEVELDEV_STR)
        with Dataset(fn_out, 'a', format='NETCDF4_CLASSIC') as nc:
            t_obj = num2date(nc.variables['time'][:],
                             nc.variables['time'].units)
            t_unit = 'hours since {:%Y-%m-%dT%H:%M:%S}'.format(fcinit)
            nc.variables['time'][:] = date2num(t_obj, t_unit)
            nc.variables['time'].setncattr('units', t_unit)
            nc.variables['time'].setncattr('standard_name', 'time')

            nc.variables['latitude'].setncattr('standard_name', 'latitude')
            nc.variables['longitude'].setncattr('standard_name', 'longitude')

            if species == 'AIR_PRESSURE':
                ps_ = nc.variables['lnsp'][:]  # TODO use species definition
                # calculate air_pressure
                p_ = (hyam[np.newaxis, :, np.newaxis, np.newaxis] +
                      hybm[np.newaxis, :, np.newaxis, np.newaxis] *
                      np.exp(ps_[:, np.newaxis, :, :]))
                # create 'level' variable
                nc.createDimension('level', hyn.size)
                v_lev = nc.createVariable('level', np.int32, ('level', ))
                v_lev[:] = np.arange(1, 61, 1, dtype='int32')
                # write air_pressure to file
                nc.createVariable(
                    'P', np.float32,
                    ('time', 'level', 'latitude', 'longitude'),
                    zlib=True, complevel=6, shuffle=True, fletcher32=True)
                nc.variables['P'][:] = p_.astype('float32')
                # set air_pressure attributes
                nc.variables['P'].setncattr('standard_name', 'air_pressure')
                nc.variables['P'].setncattr('units', 'Pa')

            self.set_standard_name(nc, species)

            v_hy = nc.createVariable('hybrid', np.float32, ('level', ))
            v_hy[:] = hyn
            v_hy.setncattr('standard_name',
                           'atmosphere_hybrid_sigma_pressure_coordinate')
            v_hy.setncattr('units', 'sigma')
            v_hy.setncattr('positive', 'down')
            v_hy.setncattr('formula', 'p(time, level, lat, lon) = '
                           'ap(level) + b(level) * exp(lnsp(time, lat, lon))')
            v_hy.setncattr('formula_terms', 'ap: hyam b: hybm lnsp:lnsp')

            v_am = nc.createVariable('hyam', np.float32, ('level', ))
            v_am[:] = hyam
            v_am.setncattr('units', 'Pa')
            v_am.setncattr('standard_name', 'atmosphere_pressure_coordinate')

            v_bm = nc.createVariable('hybm', np.float32, ('level', ))
            v_bm[:] = hybm
            v_bm.setncattr('units', '1')
            v_bm.setncattr('standard_name',
                           'atmosphere_hybrid_height_coordinate')

            nc.variables['level'].setncattr('standard_name',
                                            'model_level_number')

            for var in ['time', 'latitude', 'longitude']:
                nc.variables[var].setncattr('standard_name', var)

            # TODO add history
