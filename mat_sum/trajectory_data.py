# %%
import pandas as pd
import geopandas as gpd
import sys
import argparse
import os, glob
import json
from map_segmentation import segmentation
from map_enrichment import enrichment
from trajectory_summarization import summarization
from configs.read_config import read_config_file
# %%
config_data = read_config_file()

trajs_path = config_data.input_path
df = pd.read_csv(trajs_path)
gdf = gpd.GeoDataFrame(df,geometry=gpd.points_from_xy(df.lon,df.lat),crs="EPSG:4326")
# %%
def execute_exp(filename,name):
    '''
    Execute experiment passed in input
    '''
    print(f'EXPERIMENT n. {name[-3:]}')

    f = open(filename)
    data = json.load(f)

    locations = segmentation.tessellation(gdf,data)
    #print('Locations created!')
    # %%
    poi = gpd.GeoDataFrame()
    landuse = gpd.GeoDataFrame()
    public_transport = gpd.GeoDataFrame()
    
    if data['semantic_aspects']['POIs'] != '':
        poi = gpd.read_parquet(data['semantic_aspects']['POIs'])
    if data['semantic_aspects']['landuse'] != '':
        landuse = gpd.read_parquet(data['semantic_aspects']['landuse'])
    if data['semantic_aspects']['public_transport'] != '':
        public_transport = gpd.read_parquet(data['semantic_aspects']['public_transport'])
    # %%
    areas_unified = enrichment.enrich_areas(locations,poi,landuse,public_transport)
    #print('Locations enriched!')
    # %%
    sem_trajs = summarization.semantic_enrichment(gdf,areas_unified,config_data)
    #print('Semantic trajectories created!')
    # %%
    summ_trajs1 = summarization.summarize_trajectories1(sem_trajs,config_data)
    #print('Summarization 1')
    # %%
    summ_trajs2 = summarization.summarization2(sem_trajs,data['threshold'],areas_unified,config_data)
    #print('Summarization 2')
    
    sem_trajs.to_parquet(config_data.output_path+f'semantic_trajs_{name[-3:]}.parquet')
    summ_trajs1.to_parquet(config_data.output_path+f'summarized1_{name[-3:]}.parquet')
    summ_trajs2.to_parquet(config_data.output_path+f'summarized2_{name[-3:]}.parquet')

    print(f'EXPERIMENT n. {name[-3:]} COMPLETED!')
    
if config_data.experiment_num == 'all':
        for filename in glob.glob(config_data.experiment_path+'*.json'):
            name = os.path.splitext(filename)[0]
            print(f'EXPERIMENT n. {name[-3:]}')
            execute_exp(filename,name)
else:
    filename = config_data.experiment_path + 'experiment_' + config_data.experiment_num + '.json'
    execute_exp(filename,config_data.experiment_num)

        
  