import iris
from iris.coords import DimCoord
from iris.cube import Cube
import numpy as np
import matplotlib.pyplot as plt

import cartopy.crs as ccrs

# load some sample iris data
if 0:
    # Real code
    fname = iris.sample_data_path('rotated_pole.nc')
    temperature = iris.load_cube(fname)
else:
    ### This is how you create a cube from arrays (but it has to be a balanced grid)
    ys = np.arange(312, 392)
    lats = DimCoord(ys,
                    standard_name='grid_latitude',
                    units='degrees')
    xs = np.arange(-24, 26)
    lons = DimCoord(xs,
                    standard_name='grid_longitude',
                    units='degrees')
    values = np.random.rand(len(ys), len(xs))
    temperature = iris.cube.Cube(values, dim_coords_and_dims=[(lats, 0), (lons, 1)])

# iris comes complete with a method to put bounds on a simple point
# coordinate. This is very useful...
temperature.coord('grid_latitude').guess_bounds()
temperature.coord('grid_longitude').guess_bounds()

# turn the iris Cube data structure into numpy arrays
gridlons = temperature.coord('grid_longitude').contiguous_bounds()
gridlats = temperature.coord('grid_latitude').contiguous_bounds()
temperature = temperature.data

# set up a map
ax = plt.axes(projection=ccrs.PlateCarree())

# define the coordinate system that the grid lons and grid lats are on
rotated_pole = ccrs.RotatedPole(pole_longitude=177.5, pole_latitude=37.5)
plt.pcolormesh(gridlons, gridlats, temperature, transform=rotated_pole)

ax.coastlines()

plt.show()
