import cartopy.crs as ccrs
import geopandas as gpd
import matplotlib.pyplot as plt


def gen_pa_ax():
    shp_path = r'd:\Data\gis\census\2016\cb_2016_us_state_5m\cb_2016_us_state_5m.shp'
    df = gpd.read_file(shp_path)
    adm_shapes = list(shpreader.Reader(shp_path).geometries())

    ax = plt.axes(projection=ccrs.PlateCarree())

    # plt.title('United States')

    # ax.coastlines(resolution='10m')

    ax.add_geometries(adm_shapes, ccrs.PlateCarree(),
                      edgecolor='white', facecolor='gray', alpha=0.9)

    ax.set_extent([-126, -66, 49.3, 24.8], ccrs.PlateCarree())
