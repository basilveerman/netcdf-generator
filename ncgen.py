import os
import argparse

import netCDF4
import numpy as np

# Approximate representation of BCSD/BCCAQ grid
canada_5k = {'lon': {'start': -141, 'step': 0.08333333, 'count': 1068 },
             'lat': {'start': 41, 'step': 0.08333333, 'count': 510 } }

daily = range(365 * 150) #approx
monthly = range(12 * 150)
yearly = range(150)

def get_base_nc(fname, dims):
    nc = netCDF4.Dataset(fname, 'w')

    l = dims['lat']
    lat = nc.createDimension('lat', l['count'])
    var_lat = nc.createVariable('lat', 'f4', 'lat')
    var_lat.axis = 'Y'
    var_lat.units = 'degrees_north'
    var_lat.long_name = 'latitude'
    var_lat[:] = np.linspace(l['start'], l['start'] + l['step'] * l['count'], l['count'])

    l = dims['lon']
    lon = nc.createDimension('lon', l['count'])
    var_lon = nc.createVariable('lon', 'f4', 'lon')
    var_lon.axis = 'X'
    var_lon.units = 'degrees_east'
    var_lon.long_name = 'longitude'
    var_lon[:] = np.linspace(l['start'], l['start'] + l['step'] * l['count'], l['count'])

    return nc

def add_simple_time(nc, timescale, unlim=False):
    dim_length = len(timescale) if not unlim else 0
    time = nc.createDimension('time', dim_length)
    var_time = nc.createVariable('time', 'i4', 'time')
    var_time[:] = timescale
    var_time.axis = 'T'
    var_time.units = 'records since 1950-01-01'
    var_time.calendar = 'gregorian'
    var_time.long_name = 'time'
    return nc

def add_climo_data(nc, name, attributes={}, timemajor=True):
    if timemajor:
        var = nc.createVariable(name, 'f4', ('time', 'lat', 'lon'), fill_value=1e20)
    else:
        var = nc.createVariable(name, 'f4', ('lat', 'lon', 'time'), fill_value=1e20)
    for key, val in attributes.items():
        setattr(var, key, val)
    for i in range(var.shape[0]):
        var[i,:,:] = np.random.randn(var.shape[1], var.shape[2])
    return nc

def make_nc(fname, num_vars=1, grid=canada_5k, timescale=daily, unlim=False, timemajor=True):
    nc = get_base_nc(fname, grid)
    nc = add_simple_time(nc, timescale, unlim=unlim)

    for i in range(num_vars):
        nc = add_climo_data(nc, 'var_{}'.format(i), timemajor=timemajor)
    return nc

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="NetCDF generator")
    parser.add_argument('outfile', help="Destination file to create, will be overwritten if exists")
    parser.add_argument('-t', '--tres', choices=['daily', 'monthly', 'yearly'],
                        default='daily', help="Time resolution. Defaults to daily")
    args = parser.parse_args()

    tres = locals()[args.tres]
    make_nc(args.outfile, timescale=tres)
