import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cartopy.io.shapereader import Reader
from cartopy.mpl.patch import geos_to_path
from matplotlib.path import Path
import matplotlib as mpl
import geopandas as gpd


from clean.raw import load_modis_day

# TODO: translate aod to pm25
# TODO: pre-plot restriction as close to CONUS as possible (for automatted
# colorbar)


def get_years_modis(year):
    # TODO: make this programmatic; not all years have all days
    dfs = [load_modis_day(year, x) for x in range(1, 366)]
    df = pd.concat(dfs)
    return df


def get_pa_shape():
    shp_path = (
        r'd:\Data\gis\census\2016\cb_2016_us_state_5m\cb_2016_us_state_5m.shp'
    )
    df = gpd.read_file(shp_path)
    return df.loc[df['NAME'] == 'Pennsylvania', 'geometry']


if __name__ == '__main__':
    year = 2007
    df = get_years_modis(year)
    if 1:
        df = df[
            (df['x'] > -86.2) & (df['x'] < -71.45) &
            (df['y'] > 37.5) & (df['y'] < 43)
        ].copy()
    xy = ['x', 'y']
    df[xy] = np.around(np.around(df[xy] * 100) / 5) * 5 / 100
    df2 = df.groupby(xy)['aod'].mean()
    df3 = df2.unstack('x')
    df3 = df3 + 1

    us_shape = list(
        Reader(
            r'd:\data\gis\census\cb_2016_us_nation_5m.shp'
        ).records())[0].geometry
    x, y = np.meshgrid(df3.columns, df3.index)
    aod = np.ma.masked_array(df3.values, np.isnan(df3.values))

    ax = plt.axes(projection=ccrs.PlateCarree())

    bounds = [0, .5, .75, 1, 1.1, 1.2, 1.3, 1.4, 1.5, 3, 4, 5, 6.5]
    cm = plt.get_cmap('jet')
    my_cmap = mpl.colors.ListedColormap(
        [cm(x / len(bounds)) for x in range(1, len(bounds) + 1)]
    )
    plot = ax.pcolormesh(
        x, y, aod, transform=ccrs.PlateCarree(),
        cmap=my_cmap,
        # norm=LogNorm(vmin=aod.min(), vmax=aod.max())
        norm=mpl.colors.BoundaryNorm(bounds, my_cmap.N)
    )
    trans = ccrs.PlateCarree()._as_mpl_transform(ax)
    plot.set_clip_path(
        Path.make_compound_path(*geos_to_path(us_shape)),
        transform=trans
    )
    cb = plt.colorbar(plot)
    plt.show()
