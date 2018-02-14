import matplotlib.pyplot as plt
import numpy as np

from clean.raw import filenames_modis_day_hdf, load_hdf


def calc_midpoints(arr):
    I, J = arr.shape
    midpoints = np.zeros((I + 1, J + 1)) - 1

    # Interior points
    for i in range(1, I):
        for j in range(1, J):
            midpoints[i, j] = (arr[i - 1, j - 1] + arr[i, j]) / 2

    # top row; NOTE: this won't work if J < 5 or 6 (ish)
    i = 0
    for j in range(0, J - 2):
        point_a = midpoints[i + 1, j + 1]
        midpoints[i, j] = point_a - (midpoints[i + 2, j + 2] - point_a)
    for j in range(J, J - 3, -1):
        point_a = midpoints[i + 1, j - 1]
        midpoints[i, j] = point_a - (midpoints[i + 2, j - 2] - point_a)

    # Left column
    j = 0
    for i in range(1, I - 2):
        point_a = midpoints[i + 1, j + 1]
        midpoints[i, j] = point_a - (midpoints[i + 2, j + 2] - point_a)

    for i in range(I, I - 3, -1):
        point_a = midpoints[i - 1, j + 1]
        midpoints[i, j] = point_a - (midpoints[i - 2, j + 2] - point_a)

    # Bottom row
    i = I
    for j in range(1, J - 2):
        point_a = midpoints[i - 1, j + 1]
        midpoints[i, j] = point_a - (midpoints[i - 2, j + 2] - point_a)
    for j in range(J, J - 3, - 1):
        point_a = midpoints[i - 1, j - 1]
        midpoints[i, j] = point_a - (midpoints[i - 2, j - 2] - point_a)

    # Right column
    j = J
    for i in range(1, I - 2):
        point_a = midpoints[i + 1, j - 1]
        midpoints[i, j] = point_a - (midpoints[i + 2, j - 2] - point_a)
    for i in range(I, I - 3, -1):
        point_a = midpoints[i - 1, j - 1]
        midpoints[i, j] = point_a - (midpoints[i - 2, j - 2] - point_a)

    return midpoints


if __name__ == '__main__':
    if 0:
        files = filenames_modis_day_hdf(2010, 290)
        hdf = load_hdf(files[0])

        table_lon = hdf.select('Longitude')
        table_lat = hdf.select('Latitude')
        table_depth = hdf.select('Optical_Depth_Land_And_Ocean')

        lon = table_lon[:]
        lat = table_lat[:]
        aod = table_depth[:]
    else:
        lon = np.array([
            [1.9, 2.9, 4.9, 6.9, 8.9, 12.9],
            [1.6, 2.6, 4.6, 6.6, 8.6, 12.6],
            [1.3, 2.3, 4.3, 6.3, 8.3, 12.3],
            [1.1, 2.1, 4.1, 6.1, 8.1, 12.1],
            [1.0, 2.0, 4.0, 6.0, 8.0, 12.0],
        ])
        lat = np.array([
            [5, 5, 5, 5, 5, 5],
            [4, 4, 4, 4, 4, 4],
            [3, 3, 3, 3, 3, 3],
            [2, 2, 2, 2, 2, 2],
            [1, 1, 1, 1, 1, 1],
        ])

    I, J = lon.shape

    corner_lat = np.zeros((I + 1, J + 1)) - 1
    corner_lon = calc_midpoints(lon)
    corner_lat = calc_midpoints(lat)
    print(corner_lon)
    print(corner_lat)
    fig, ax = plt.subplots()
    for i, x in enumerate(lon):
        y = lat[i]
        ax.scatter(x, y, marker='o', color='black')
    for i, x in enumerate(corner_lon):
        y = corner_lat[i]
        ax.scatter(x, y, marker='x', color='red')
    plt.show()
