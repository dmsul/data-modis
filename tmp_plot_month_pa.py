import cartopy.crs as ccrs
from shapely.geometry import Point
import geopandas as gpd
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from scipy.spatial import Voronoi

from explore_hdf import load_modus_day


def modis_make_month():
    year = 2000
    df = load_modus_day(year=year, day=56)
    for d in range(57, 70):
        df = df.append(load_modus_day(year=year, day=d))

    return df


def get_pa_shape():
    shp_path = r'd:\Data\gis\census\2016\cb_2016_us_state_5m\cb_2016_us_state_5m.shp'
    df = gpd.read_file(shp_path)
    return df.loc[df['NAME'] == 'Pennsylvania', 'geometry']


def voronoi_finite_polygons_2d(vor, radius=None):
    """
    Reconstruct infinite voronoi regions in a 2D diagram to finite
    regions.

    Parameters
    ----------
    vor : Voronoi
        Input diagram
    radius : float, optional
        Distance to 'points at infinity'.

    Returns
    -------
    regions : list of tuples
        Indices of vertices in each revised Voronoi regions.
    vertices : list of tuples
        Coordinates for revised Voronoi vertices. Same as coordinates
        of input vertices, with 'points at infinity' appended to the
        end.

    """

    if vor.points.shape[1] != 2:
        raise ValueError("Requires 2D input")

    new_regions = []
    new_vertices = vor.vertices.tolist()

    center = vor.points.mean(axis=0)
    if radius is None:
        radius = vor.points.ptp().max()

    # Construct a map containing all ridges for a given point
    all_ridges = {}
    for (p1, p2), (v1, v2) in zip(vor.ridge_points, vor.ridge_vertices):
        all_ridges.setdefault(p1, []).append((p2, v1, v2))
        all_ridges.setdefault(p2, []).append((p1, v1, v2))

    # Reconstruct infinite regions
    for p1, region in enumerate(vor.point_region):
        vertices = vor.regions[region]

        if all(v >= 0 for v in vertices):
            # finite region
            new_regions.append(vertices)
            continue

        # reconstruct a non-finite region
        ridges = all_ridges[p1]
        new_region = [v for v in vertices if v >= 0]

        for p2, v1, v2 in ridges:
            if v2 < 0:
                v1, v2 = v2, v1
            if v1 >= 0:
                # finite ridge: already in the region
                continue

            # Compute the missing endpoint of an infinite ridge

            t = vor.points[p2] - vor.points[p1] # tangent
            t /= np.linalg.norm(t)
            n = np.array([-t[1], t[0]])  # normal

            midpoint = vor.points[[p1, p2]].mean(axis=0)
            direction = np.sign(np.dot(midpoint - center, n)) * n
            far_point = vor.vertices[v2] + direction * radius

            new_region.append(len(new_vertices))
            new_vertices.append(far_point.tolist())

        # sort region counterclockwise
        vs = np.asarray([new_vertices[v] for v in new_region])
        c = vs.mean(axis=0)
        angles = np.arctan2(vs[:,1] - c[1], vs[:,0] - c[0])
        new_region = np.array(new_region)[np.argsort(angles)]

        # finish
        new_regions.append(new_region.tolist())

    return new_regions, np.asarray(new_vertices)

if __name__ == '__main__':
    pa_shp = get_pa_shape()


    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.add_geometries(pa_shp, ccrs.PlateCarree(),
                      edgecolor='white', facecolor='gray', alpha=0.3, zorder=1)

    x0, y0, x1, y1 = pa_shp.bounds.values[0]
    x0 -= .5
    y0 -= .5
    x1 += .5
    y1 += .5

    ax.set_extent([x0, x1, y0, y1], ccrs.PlateCarree())


    # load data
    df = pd.read_pickle('./tmp.pkl')
    df['shade'] = df['aod'] / df['aod'].max()
    points = df[['x', 'y']].values

    # compute Voronoi tesselation
    vor = Voronoi(points)

    # plot
    pa_shp = pa_shp.squeeze()

    regions, vertices = voronoi_finite_polygons_2d(vor)
    # colorize
    shapes = []
    for idx, region in enumerate(regions):
        polygon = vertices[region]
        if min([pa_shp.contains(Point(p)) for p in polygon]):
            shapes.append((polygon, df.iat[idx, 2]))

        else:
            continue

    gdf = pd.DataFrame(shapes)
    gdf[1] = gdf[1]/ gdf[1].max()

    for idx, (polygon, val) in gdf.iterrows():
        ax.fill(*zip(*polygon), color=cm.YlOrBr(val), alpha=.8,
                zorder=10)

    # plt.plot(points[:,0], points[:,1], 'ko')
    plt.show()

