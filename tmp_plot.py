import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import matplotlib.pyplot as plt


shp_path = r'd:\Data\gis\census\2016\cb_2016_us_state_5m\cb_2016_us_state_5m.shp'

adm_shapes = list(shpreader.Reader(shp_path).geometries())

ax = plt.axes(projection=ccrs.PlateCarree())

# plt.title('United States')

# ax.coastlines(resolution='10m')

ax.add_geometries(adm_shapes, ccrs.PlateCarree(),
                  edgecolor='white', facecolor='gray', alpha=0.9)

ax.set_extent([-126, -66, 49.3, 24.8], ccrs.PlateCarree())

plt.show()
