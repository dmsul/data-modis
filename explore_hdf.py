import glob
import pandas as pd
import numpy as np
from pyhdf.SD import SD, SDC


def load_modus_day(year=2000, day=56):
    """ Append all the DF's for a single day """
    df = pd.DataFrame()
    # XXX For now, just grab the first ten files to save time
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
    df = load_modus_day()
    # df = df.append(load_modus_day(day=55))
    # df = df.append(load_modus_day(day=57))
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    ax.scatter(df['x'], df['y'])
    plt.show()
