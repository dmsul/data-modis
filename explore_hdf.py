import os
import glob
import pandas as pd
import numpy as np
from pyhdf.SD import SD, SDC

from econtools import load_or_build


def modis_day_df_path():
    return os.path.join(years_folder_path('{}'), '{}.pkl')


def years_folder_path(year):
    LOCAL_DATA_ROOT = '../data/'
    target_path = os.path.join(LOCAL_DATA_ROOT, f'{year}')
    return target_path


@load_or_build(modis_day_df_path(), path_args=['year', 'day'])
def load_modis_day(year=2000, day=56):
    return load_modis_day_hdf(year, day)



def make_years_folder(year):
    path = Path(days_folder_path(year))
    path.mkdir(exist_ok=True)




def load_modis_day_hdf(year=2000, day=56):
    """ Append all the DF's for a single day """
    df = pd.DataFrame()
    files = glob.glob(r'../data/src/{}/{}/*.hdf'.format(year, day))
    for filepath in files:
        print(filepath)
        hdf = load_hdf(filepath)
        this_df = hdf_to_df(hdf)
        this_df = this_df[this_df['aod'] > -9999].copy()
        df = df.append(this_df)
        del hdf, this_df

    # TODO: add time variables to `df`

    return df


def hdf_to_df(hdf):
    table_lon = hdf.select('Longitude')
    table_lat = hdf.select('Latitude')
    table_depth = hdf.select('Optical_Depth_Land_And_Ocean')

    lat = _flatten_tables_data(table_lat)
    lon = _flatten_tables_data(table_lon)
    depth = _flatten_tables_data(table_depth)

    df = pd.DataFrame(
        np.hstack((lon, lat, depth)),
        columns=['x', 'y', 'aod']
    )
    # df = df.set_index(['x', 'y'])
    
    return df

def _flatten_tables_data(hdf_table):
    """
    Take an `hdf_table` and make its data a 2D vector (2D for use with
    `np.hstack`)
    """
    arr = hdf_table[:, :]
    flat_arr = arr.reshape(-1, 1)
    return flat_arr


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
    df = load_modis_day()
    # df = df.append(load_modis_day(day=55))
    # df = df.append(load_modis_day(day=57))
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    ax.scatter(df['x'], df['y'])
    plt.show()
