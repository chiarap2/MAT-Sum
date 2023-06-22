# %%
import geopandas as gpd
import tesspy
import pandas as pd
from shapely.geometry import Polygon
# %%
def set_polygon(gdf):
    '''
    Compute the bounding polygon starting from the GeoDataFrame of trajectories
    Return a GeoDataFrame with polygon geometry

    gdf: a trajectory GeoDataFrame or a polygon GeoDataFrame
    '''

    if 'lat' in gdf.columns:

        gdf_poly = gpd.GeoDataFrame(
        [Polygon([[max(gdf.lon), max(gdf.lat)],
            [max(gdf.lon), min(gdf.lat)],
            [min(gdf.lon), min(gdf.lat)],
            [min(gdf.lon), max(gdf.lat)]
            ])],
        columns = ['geometry'],
        geometry='geometry',
        crs="EPSG:4326")

    else:

        gdf_poly = gdf    

    # add 'osm_id' column because is required from tesspy library
    gdf_poly['osm_id'] = 0

    return gdf_poly
# %%
def tessellation(gdf,method):
    '''
    Tessallate polygon of interest based on the method passed in input

    polygon: a GeoDataFrame with the polygon to tessellate
    method: a dict in which there are the info about the method used to tessellate polygon

    return a GeoDataFrame containing areas obtained from the tessellation 
    '''
    polygon = set_polygon(gdf)
    city = tesspy.Tessellation(polygon)
    
    if method['tessellation']['type'] == 'squares':
        locations = city.squares(resolution=method['tessellation']['resolution'])
        locations.rename(columns={'quadkey':'locationID'},inplace=True)

    if method['tessellation']['type'] == 'adaptive_squares':
        locations = city.adaptive_squares(resolution=method['tessellation']['resolution'])
        locations.rename(columns={'quadkey':'locationID'},inplace=True)

    if method['tessellation']['type'] == 'voronoi':
        locations = city.voronoi(method['tessellation']['cluster_algo'], poi_categories='all')
        locations.rename(columns={'voronoi_id':'locationID'},inplace=True)

    if method['tessellation']['type'] == 'city_blocks':
        locations = city.city_blocks()
        locations.rename(columns={'cityblock_id':'locationID'},inplace=True)

    if method['tessellation']['type'] == 'hexagons':
        locations = city.hexagons(resolution=method['tessellation']['resolution'])
        locations.rename(columns={'hex_id':'locationID'},inplace=True)

    return locations