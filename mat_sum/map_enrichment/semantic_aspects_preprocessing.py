# %%
import pandas as pd
import geopandas as gpd
from shapely.geometry import Polygon
import tesspy
import re
import osmnx as ox
from gensim.test.utils import common_texts
from gensim.models import FastText
# %%

# turn response caching off
ox.settings.use_cache = False
# set timeout
ox.settings.timeout = 10800
# %%
def read_categories(path):
    # read POI categories from the file

    tags = {}

    with open(path) as f:

        lines = f.readlines()

        tag = ""

        for line in lines:

            super_category = re.findall(r".*=",line)
            super_category = super_category[0][0:-1]

            category = re.findall(r"=.*;",line)
            category = category[0][1:-1]

            if tag == super_category:

                tags[tag].append(category)

            else:
                
                tag = super_category
                tags[tag] = []
                tags[tag].append(category)

    return tags
# %%
def download_poi_osm(gdf_pois,tags):
    '''
    Download semantic aspects from OSM
    
    gdf_pois: geodataframe of POIs (with geometry)
    tags: dictionary of POIs categories
    
    Return: geodataframe of POIs with semantic aspects
    '''
    macro_categories = [c for c in list(tags.keys()) if c in gdf_pois.columns]
    poi = gdf_pois[macro_categories].stack()

    poi = pd.DataFrame(poi)
    poi.reset_index(inplace=True)
    poi.set_index('level_0',inplace=True)
    poi.loc[poi.index.isin(gdf_pois.index),'geometry'] = gdf_pois.loc[gdf_pois.index.isin(poi.index),'geometry']
    poi.rename(columns={'level_1':'OSM category',0:'POI category'},inplace=True)
    
    poi['OSM category'] = poi['OSM category'].str.replace('_',' ')
    poi['POI category'] = poi['POI category'].str.replace('_',' ')
    poi = poi[~poi['POI category'].str.contains('yes')]
    poi = poi[~poi['POI category'].str.contains(';')]
    poi = gpd.GeoDataFrame(poi)
    
    return poi
# %%
def labeling_aspects(path):
    '''
    Label POI categories with the label of the most similar category
    
    path: path of the file containing the POI categories
    
    Return: geodataframe of POIs with labeled categories
    '''
    poi = gpd.read_parquet(path)
    labels = pd.read_csv('../data/labeled_OSM_category.csv',delimiter=';')
    labels['poi_category'] = labels['poi_category'].str.replace('_',' ')
    labels_dict = dict(zip(labels.poi_category, labels.label))
    
    poi['label'] = poi['POI category'].map(labels_dict,na_action='ignore')
    words = poi['POI category'].unique()
    words_without_label = poi[poi['label'].isna()]['POI category'].unique()
    words_with_label = poi[~poi['label'].isna()]['POI category'].unique()

    labels_dict = {}

    model = FastText(sentences=[list(words_with_label)], min_count=1, workers=4)

    for w in words_without_label:

        word_similar = model.wv.most_similar(w,topn=1)
        labels_dict[w] = labels_dict[word_similar[0][0]]

    poi['label'] = poi['POI category'].map(labels_dict,na_action='ignore')

    landuse = poi[poi['label']=='landuse']
    public_transport = poi[poi['label']=='public transport']
    poi = poi[poi['label']!='landuse']
    poi = poi[poi['label']!='public transport']

    #poi.to_parquet('data/labeled_POIs.parquet')
    #landuse.to_parquet('data/labeled_landuse.parquet')
    #public_transport.to_parquet('data/labeled_public_transport_NYC.parquet')

    return poi, landuse, public_transport
# %%
tags = read_categories('../data/pois_categories_OSM.txt')
poly = gpd.read_parquet('/home/chiarap/foursquare/geolife/beijing.parquet')
poly = poly[['osm_id','geometry']]
gdf_pois = ox.geometries_from_place('Beijing, China',tags=tags)

# %%
gdf_pois.reset_index(inplace=True)
# %%
gdf_pois.to_csv('/home/chiarap/foursquare/geolife/poi_beijing.csv')
# %% 

poi = download_poi_osm(gdf_pois, tags=tags)
poi.to_parquet('/home/chiarap/foursquare/geolife/poi_beijing_cleaned.parquet')
pois, landuse, public_transport = labeling_aspects('/home/chiarap/foursquare/geolife/poi_beijing_cleaned.parquet')

pois.to_parquet('/home/chiarap/foursquare/geolife/labeled_pois.parquet')
landuse.to_parquet('/home/chiarap/foursquare/geolife/labeled_landuse.parquet')
public_transport.to_parquet('/home/chiarap/foursquare/geolife/labeled_public_transport.parquet')

# %%
