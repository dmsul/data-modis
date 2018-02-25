import os
import glob
import pandas as pd
import numpy as np
from pyhdf.SD import SD, SDC

from econtools import load_or_build

from modis.util.env import data_path


@load_or_build(data_path('modis_{}.pkl'), path_args=[0])
def load_modis_year(year, _rebuild_down=False):
    def _wrapper(a, b):
        try:
            return load_modis_day(a, b, _rebuild=_rebuild_down)
        except ValueError:
            return pd.DataFrame()

    dfs = [_wrapper(year, x) for x in range(1, 366)]
    df = pd.concat(dfs)
    del dfs

    df = df.astype(np.float32).set_index(['x', 'y'])

    return df


@load_or_build(data_path('{}', '{}.pkl'), path_args=[0, 1])
def load_modis_day(year, day):
    return load_modis_day_hdf(year, day)


def load_modis_day_hdf(year, day):
    """ Append all the DF's for a single day """
    df = pd.DataFrame()
    files = filenames_modis_day_hdf(year, day)
    if not files:
        raise ValueError("No files found!")
    print(files[0])
    dfs = [hdf_to_df(load_hdf(filepath)) for filepath in files]
    df = pd.concat(dfs).reset_index(drop=True)

    # Compress dtypes
    for col in ('x', 'y', 'aod'):
        df[col] = df[col].astype(np.float32)

    return df


def filenames_modis_day_hdf(year, day):
    day_str = str(day).zfill(3)
    src_path_str = 'e:/modis/src/'
    files = glob.glob(os.path.join(src_path_str, f'{year}/{day_str}/*.hdf'))
    return files


def hdf_to_df(hdf):
    table_lon = hdf.select('Longitude')
    table_lat = hdf.select('Latitude')
    table_depth = hdf.select('Optical_Depth_Land_And_Ocean')

    lat = _flatten_tables_data(table_lat)
    lon = _flatten_tables_data(table_lon)
    depth, scale_factor, add_offset = _flatten_tables_data(table_depth,
                                                           return_offset=True)

    df = pd.DataFrame(
        np.hstack((lon, lat, depth)),
        columns=['x', 'y', 'aod']
    )

    # Add scan time
    table_time = hdf.select('Scan_Start_Time')
    scan_time, time_origin = _flatten_time_data(table_time)
    df['time'] = pd.to_datetime(scan_time, unit='s', origin=time_origin)

    # Drop missings
    df = df[df['aod'] != scale_factor * (-9999 - add_offset)].copy()

    if 1:
        # Restrict to continental U.S.
        x0 = -124.7844079
        x1 = -66.9513812
        y0 = 24.7433195
        y1 = 49.3457868
        in_cotus = (df['x'].between(x0, x1)) & (df['y'].between(y0, y1))
        df = df[in_cotus]

    return df

def _flatten_tables_data(hdf_table, return_offset=False):
    """
    Take an `hdf_table` and make its data a 2D vector (2D for use with
    `np.hstack`)
    """
    arr = hdf_table[:, :]
    scale_factor = hdf_table.attributes()['scale_factor']
    add_offset = hdf_table.attributes()['add_offset']
    flat_arr = scale_factor * (arr.reshape(-1, 1) - add_offset)
    if return_offset:
        return flat_arr, scale_factor, add_offset
    else:
        return flat_arr

def _flatten_time_data(hdf_table):
    """
    Take an `hdf_table` and make its data a 2D vector (2D for use with
    `np.hstack`)
    """
    arr = hdf_table[:, :]
    scale_factor = hdf_table.attributes()['scale_factor']
    add_offset = hdf_table.attributes()['add_offset']
    flat_arr = arr.reshape(-1, 1).astype(np.int64).squeeze()
    if scale_factor == 1 and add_offset == 0:
        pass
    else:
        flat_arr = scale_factor * (flat_arr - add_offset)

    # Get time origin
    origin_str = hdf_table.attributes()['units']
    origin_str = origin_str.replace('Seconds since ', '')
    origin_str = ' '.join(origin_str.split(' ')[:-1])
    origin_datetime = pd.Timestamp(origin_str)

    return flat_arr, origin_datetime


def load_hdf(filepath):
    hdf = SD(filepath, SDC.READ)

    return hdf


def print_datasets():
    """ Standalone script to print dataset names and descriptions. """
    FILE_NAME = '../data/src/2000/55/MOD04_3K.A2000055.2015.hdf'
    hdf = load_hdf(FILE_NAME)
    dataset_names = hdf.datasets().keys()
    for name in dataset_names:
        this_dataset = hdf.select(name)
        print(name)
        print(this_dataset.attributes()['long_name'])
        print('\n')


if __name__ == '__main__':
    for year in range(2000, 2017):
        df = load_modis_year(year, _rebuild=True, _rebuild_down=True)
        del df
