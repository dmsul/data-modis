import os


DATA_PATH = 'd:\\Data\\modis'

HDF_SRC_PATH_WIN = 'e:\\modis\\src'
HDF_SRC_PATH_NIX = '/media/sf_modis/src'


def data_path(*args):
    return os.path.join(DATA_PATH, *args)
