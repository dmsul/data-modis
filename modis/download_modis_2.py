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

from util.env import data_path


def _main():
    source = (
        r'https://ladsweb.modaps.eosdis.nasa.gov/archive'
        r'/allData/6/MOD04_3K/2017/002'
    )
    token = 'F1957080-3CE3-11E8-B246-FFF9569DBFBA'

    destination = data_path('tmp')

    if not os.path.exists(destination):
        os.makedirs(destination)

    return sync(source, destination, token)


def sync(src, dest, tok):
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

    # use os.path since python 2/3 both support it while pathlib is 3.4+
    for f in files:
        # currently we use filesize of 0 to indicate directory
        filesize = int(f['size'])
        path = os.path.join(dest, f['name'])
        url = src + '/' + f['name']
        if filesize == 0:
            try:
                print('creating dir:', path)
                os.mkdir(path)
                sync(src + '/' + f['name'], path, tok)
            except IOError as e:
                print("mkdir `%s': %s" % (e.filename, e.strerror),
                      file=sys.stderr)
                sys.exit(-1)
        else:
            try:
                if not os.path.exists(path):
                    print('downloading: ', path)
                    with open(path, 'w+b') as fh:
                        geturl(url, tok, fh)
                else:
                    print('skipping: ', path)
            except IOError as e:
                print("open `%s': %s" % (e.filename, e.strerror),
                      file=sys.stderr)
                sys.exit(-1)
    return 0


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


if __name__ == '__main__':
    try:
        sys.exit(_main())
    except KeyboardInterrupt:
        sys.exit(-1)
