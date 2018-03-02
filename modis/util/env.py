import os
import socket

# Check which machine we're on
HOST = socket.gethostname()
if HOST == 'sullivan-7d':
    data_root = "D:\\"
elif HOST == 'DESKTOP-HOME':
    data_root = "D:\\"
elif HOST == 'nepf-7d':
    data_root = "M:\\EPA_AirPollution\\"
else:
    data_root = r'\\Sullivan-7d\d'

DATA_PATH = os.path.join(data_root, 'Data', 'modis')

HDF_SRC_PATH_WIN = 'e:\\modis\\src'
HDF_SRC_PATH_NIX = '/media/sf_modis/src'


def data_path(*args):
    return os.path.join(DATA_PATH, *args)
