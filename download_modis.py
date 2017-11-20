import os
from pathlib import Path
import ftplib
import time

LOCAL_DATA_ROOT = 'D:/Data/modis/src'
SLEEP = 0.5


def download_year(year):
    """ Download all MODIS_3K files for `year` """
    ftp = setup_ftp_connection()

    ftp.cwd(f'{year}')

    days = ftp.nlst()       # List all folders (days) under `year`

    for day in days:
        download_day(year, day, ftp)

    ftp.quit()


def download_day(year, day, ftp):
    """
    Download all MODIS_3K files for `year'/`day'. Requires `ftp` to already be
    in the proper directory for `year`
    """
    ftp.cwd(day)
    make_days_folder(year, day)
    files = ftp.nlst()  # List all files for this day
    for f in files:
        target_path = files_target_path(year, day, f)
        # If target file already downloaded, skip
        if os.path.exists(target_path):
            print(f"File {f} exists on disk!")
            continue
        else:
            print(f"Downloading {f}...", end='', flush=True)
            try:
                with open(target_path, 'wb') as open_f:
                    ftp.retrbinary(f"RETR {f}", open_f.write)
                print('done!')
                time.sleep(SLEEP)
            except:
                print("ERROR!")
                ftp.quit()
                os.remove(target_path)      # XXX doesn't work, file locked
                raise

    ftp.cwd('..')       # Move back up to `year` folder


def setup_ftp_connection():
    """ Establish FTP connection, navigate to MODIS 3K folder """
    FTP_DOMAIN = r'ladsweb.nascom.nasa.gov'
    ftp = ftplib.FTP(FTP_DOMAIN)
    ftp.login()
    ftp.cwd('allData/6/MOD04_3K')

    return ftp


def files_target_path(year, day, f_name):
    return os.path.join(days_folder_path(year, day), f_name)


def make_days_folder(year, day):
    path = Path(days_folder_path(year, day))
    path.mkdir(parents=True, exist_ok=True)


def days_folder_path(year, day):
    target_path = os.path.join(LOCAL_DATA_ROOT, f'{year}', f'{day}')
    return target_path


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        year = int(sys.argv[1])
        if not (2000 < year < 2018):
            raise ValueError(f"Invalid year: {year}")
    else:
        year = 2012

    download_year(year)
