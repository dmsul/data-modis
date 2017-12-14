import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
from shapely.geometry import Point
import geopandas as gpd
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from scipy.spatial import Voronoi

from explore_hdf import load_modis_day


def main_grid():
    pass


def main_voronoi():
    pass


def modis_make_month():
    # year = 2000
    year = 2012
    # df = load_modis_day(year=year, day=55)
    df = load_modis_day(year=year, day=1)
    for d in range(2, 22):
        df = df.append(load_modis_day(year=year, day=d))

    return df


def get_us_shapes():
    shp_path = r'd:\Data\gis\census\2016\cb_2016_us_state_5m\cb_2016_us_state_5m.shp'
    adm_shapes = list(shpreader.Reader(shp_path).geometries())
    return adm_shapes


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


def get_pa_modis():
    """ janky and tmp """
    df = modis_make_month()
    # Restrict to (roughly) PA
    pa_shp = get_pa_shape()
    x0, y0, x1, y1 = pa_shp.bounds.values[0]
    x0 -= .5
    y0 -= .5
    x1 += .5
    y1 += .5
    df = df[(df['x'] > x0) & (df['x'] < x1) & (df['y'] > y0) & (df['y'] < y1)]
    # Round to nearest .025 degree (roughly 10 km)
    factor = .05
    df[['x', 'y']] = np.around(df[['x', 'y']] / factor).astype(int) * factor

    df = df.groupby(['x', 'y'])['aod'].mean()

    return df.reset_index().sort_values(['x', 'y'])


if __name__ == '__main__':
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.add_geometries(get_us_shapes(), ccrs.PlateCarree(),
                      edgecolor='white', facecolor='gray', alpha=0.3, zorder=1)

    pa_shp = get_pa_shape()
    x0, y0, x1, y1 = pa_shp.bounds.values[0]
    x0 -= .5
    y0 -= .5
    x1 += .5
    y1 += .5

    ax.set_extent([x0, x1, y0, y1], ccrs.PlateCarree())


    # load data
    # df = pd.read_pickle('./tmp.pkl')
    df = get_pa_modis()

    # compute Voronoi tesselation
    points = df[['x', 'y']].values
    vor = Voronoi(points)

    # plot
    pa_shp = pa_shp.squeeze()

    if 0:
        regions, vertices = voronoi_finite_polygons_2d(vor)
    else:
        regions, vertices = vor.regions, vor.vertices
    # colorize
    shapes = []
    for idx, region in enumerate(regions):
        if not region:
            continue
        polygon = vertices[region]
        if min([pa_shp.contains(Point(p)) for p in polygon]):
            try:
                shapes.append((polygon, df.iat[idx, 2]))
            except IndexError:
                pass

        else:
            continue

    gdf = pd.DataFrame(shapes)
    # cut = pd.qcut(gdf[1], 10, labels=False)
    num_bins = 20
    cut = pd.qcut(gdf[1], q=[x / num_bins for x in range(num_bins)] + [.99, 1], labels=False)
    # cut = gdf[1]
    gdf[2] = cut / cut.max()

    for idx, (polygon, __, val) in gdf.iterrows():
        ax.fill(*zip(*polygon), facecolor=cm.YlOrBr(val), edgecolor=None,
                alpha=.8, zorder=10)

    # plt.plot(points[:,0], points[:,1], 'ko')
    if 0:
        sm = plt.cm.ScalarMappable(cprintmap=cm.YlOrBr, norm=plt.Normalize(0, 1))
        sm._A = []
        plt.colorbar(sm, ax=ax)
    # plt.show()
    plt.savefig('../MODIS_PM_rough.jpg', dpi=600, bbox_inches='tight')
