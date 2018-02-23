import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from cartopy.io.shapereader import Reader
from cartopy.mpl.patch import geos_to_path
from matplotlib.path import Path
import matplotlib as mpl
import geopandas as gpd
from mpl_toolkits.axes_grid1 import make_axes_locatable


from clean.raw import load_modis_year

# TODO: translate aod to pm25
# TODO: pre-plot restriction as close to CONUS as possible (for automatted
# colorbar)


def map_year(year, norm=None, save=False):
    df = prep_modis(year)
    # boundary_shape = get_pa_shape()
    boundary_shape = get_conus_shape()
    if 0:
        x0 = -86.2
        x1 = -71.45
        y0 = 37.5
        y1 = 43
        df = df[
            (df['x'] > x0) & (df['x'] < x1) &
            (df['y'] > y0) & (df['y'] < y1)
        ].copy()
    elif 0:
        # x0, y0, x1, y1 = boundary_shape.bounds.values[0].tolist()
        x0, y0, x1, y1 = boundary_shape.bounds
        df = df[
            (df['x'] > x0) & (df['x'] < x1) &
            (df['y'] > y0) & (df['y'] < y1)
        ].copy()
    xy = ['x', 'y']
    df[xy] = np.around(np.around(df[xy] * 100) / 5) * 5 / 100
    df2 = df.groupby(xy)['aod'].mean()
    df3 = df2.unstack('x')
    df3 = df3 + 1

    x, y = np.meshgrid(df3.columns, df3.index)
    aod = np.ma.masked_array(df3.values, np.isnan(df3.values))

    ax = plt.axes(projection=ccrs.PlateCarree())

    # bounds = [0, .5, .75, 1, 1.1, 1.2, 1.3, 1.4, 1.5, 3, 4, 5, 6.5]
    # my_cmap = mpl.colors.ListedColormap(
        # [cm(x / len(bounds)) for x in range(1, len(bounds) + 1)]
    # )
    if not norm:
        norm = mpl.colors.LogNorm(vmin=aod.min(), vmax=aod.max())
    plot = ax.pcolormesh(
        x, y, aod, transform=ccrs.PlateCarree(),
        # cmap=my_cmap,
        norm=norm,
        # norm=mpl.colors.BoundaryNorm(bounds, my_cmap.N)
    )
    trans = ccrs.PlateCarree()._as_mpl_transform(ax)
    plot.set_clip_path(
        Path.make_compound_path(*geos_to_path(boundary_shape)),
        transform=trans
    )

    divider = make_axes_locatable(ax)
    ax_cb = divider.new_horizontal(size='2%', pad=0.1, axes_class=plt.Axes)
    fig = plt.gcf()
    fig.add_axes(ax_cb)

    ticks = [15, 20, 25, 30, 35]
    cb = fig.colorbar(plot, cax=ax_cb, ticks=ticks)
    cb.ax.set_yticklabels(ticks)

    if save:
        plt.savefig(f'../modis_pa_{year}.png', dpi=600, bbox_inches='tight')
        plt.close()
    else:
        plt.show()

    return norm


def prep_modis(year):
    df = load_modis_year(year).reset_index()
    df['aod'] = df['aod'] * 29.4 + 8.8
    return df


def get_pa_shape():
    shp_path = (
        r'd:\Data\gis\census\cb_2016_us_state_5m\cb_2016_us_state_5m.shp'
    )
    df = gpd.read_file(shp_path)
    return df.loc[df['NAME'] == 'Pennsylvania', 'geometry'].squeeze()


def get_conus_shape():
    us_shape = list(
        Reader(
            r'd:\data\gis\census\cb_2016_us_nation_5m.shp'
        ).records())[0].geometry

    return us_shape


if __name__ == '__main__':
    save = True
    norm = map_year(2002, save=save)
    # for y in range(2003, 2017):
        # map_year(y, norm=norm, save=save)
