import os
import socket

PROJECT_NAME = 'data-modis'

# Check which machine we're on
HOST = socket.gethostname()
if HOST in ('sullivan-10d', 'sullivan-7d', 'DESKTOP-HOME'):
    data_root = "D:\\"
else:
    data_root = r'\\Sullivan-10d\d'

DATA_PATH = os.path.join(data_root, 'Data', PROJECT_NAME)

HDF_SRC_PATH_WIN = 'e:\\modis\\src'
HDF_SRC_PATH_NIX = '/media/sf_modis/src'


def data_path(*args):
    return os.path.join(DATA_PATH, *args)
