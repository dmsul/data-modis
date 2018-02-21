import os


DATA_PATH = 'd:\\Data\\modis'


def data_path(*args):
    return os.path.join(DATA_PATH, *args)
