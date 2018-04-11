"""
DESC = ("This script will recursively download all files if they don't exist"
        "from a LAADS URL and stores them to the specified path")
Based on example script found at

https://ladsweb.modaps.eosdis.nasa.gov/tools-and-services/data-download-scripts/#python

on 10 Apr 2018
"""
import os
import os.path
import shutil
import sys
from urllib.request import urlopen, Request, URLError, HTTPError
import ssl
from io import StringIO

from util.env import HDF_SRC_PATH_WIN, HDF_SRC_PATH_NIX
try:
    # This utility only works on Linux
    from timeout_decorator import timeout

    LOCAL_DATA_ROOT = HDF_SRC_PATH_NIX
except ImportError:
    from sys import platform
    if 'linux' in platform:
        raise ImportError

    def timeout(*args, **kwargs):
        """ Dummy decorator for 'timeout' we don't have """
        def true_decorator(f):
            return f
        return true_decorator
    LOCAL_DATA_ROOT = HDF_SRC_PATH_WIN


def download_main(year, start_day=1, day_only=False):
    source = (
        'https://ladsweb.modaps.eosdis.nasa.gov/archive'
        f'/allData/6/MOD04_3K/{year}'
    )
    token = 'F1957080-3CE3-11E8-B246-FFF9569DBFBA'

    destination = os.path.join(LOCAL_DATA_ROOT, str(year))

    if day_only:
        day_str = f'{start_day}'.zfill(3)
        source += '/' + day_str
        start_day = None
        destination = os.path.join(destination, day_str)

    if not os.path.exists(destination):
        os.makedirs(destination)

    return sync(source, destination, token, start_day=start_day)


def sync(src, dest, tok, start_day=None):
    '''synchronize src url with dest directory'''
    try:
        import csv
        files = [
            f
            for f in csv.DictReader(StringIO(geturl('%s.csv' % src, tok)),
                                    skipinitialspace=True)
        ]
    except ImportError:
        import json
        files = json.loads(geturl(src + '.json', tok))

    # Skip days to `start_day`
    if start_day is not None:
        files = files[start_day - 1:]

    for f in files:
        # currently we use filesize of 0 to indicate directory
        filesize = int(f['size'])
        path = os.path.join(dest, f['name'])
        url = src + '/' + f['name']
        if filesize == 0:
            try:
                os.mkdir(path)
            except IOError as e:
                pass
            sync(src + '/' + f['name'], path, tok)
        else:
            try:
                if not os.path.exists(path):
                    print('downloading: ', path, end='...')
                    with open(path, 'w+b') as fh:
                        geturl(url, tok, fh)
                    print('done!')
                else:
                    pass
            except StopIteration:
                print("Timeout! Trying again...")
                sync(src, dest, tok)
            except IOError as e:
                print("open `%s': %s" % (e.filename, e.strerror),
                      file=sys.stderr)
                raise
    return 0


@timeout(120, timeout_exception=StopIteration)
def geturl(url, token=None, out=None):
    USERAGENT = (
        'tis/download.py_1.0--' +
        sys.version.replace('\n', '').replace('\r', '')
    )
    headers = {'user-agent': USERAGENT}
    if token is not None:
        headers['Authorization'] = 'Bearer ' + token

    CTX = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    try:
        fh = urlopen(Request(url, headers=headers), context=CTX)
        if out is None:
            return fh.read().decode('utf-8')
        else:
            shutil.copyfileobj(fh, out)
    except HTTPError as e:
        print('HTTP GET error code: %d' % e.code(),
              file=sys.stderr)
        print('HTTP GET error message: %s' % e.message,
              file=sys.stderr)
    except URLError as e:
        print('Failed to make request: %s' % e.reason,
              file=sys.stderr)
    return None
