import argparse

from util.download_data import download_main


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument('year', type=int)
    parser.add_argument('day', type=int, default=1)
    help_str = (
        'Download specified day only. Default behavior is '
        'to download entire year starting from `year`/`day`.'
    )
    parser.add_argument('--day-only', '-d', action='store_true', help=help_str)

    args = parser.parse_args()

    return args


if __name__ == '__main__':
    args = cli()

    download_main(args.year, start_day=args.day, day_only=args.day_only)
