# %%
from hashlib import new
import pandas as pd
import os
import glob
# %%
results = pd.DataFrame(columns=['experiment_num','summarization_rate1','summarization_rate2'])

df = pd.read_csv('/home/chiarap/foursquare/geolife/geolife_cleaned.csv')

for filename in glob.glob('../config-gps/*.json'):

    name = os.path.splitext(filename)[0]
    
    new_row = {}

    experiment_number = name[-3:]

    #sem_trajs = pd.read_parquet(f'../output-gps/semantic_trajs_{experiment_number}.parquet')
    summ1 = pd.read_parquet(f'../output-gps/summarized1_{experiment_number}.parquet')
    summ2 = pd.read_parquet(f'../output-gps/summarized2_{experiment_number}.parquet')

    new_row['experiment_num'] = experiment_number

    new_df = df[df['traj_id'].isin(summ1.tid)]

    sem_unique = new_df.groupby('traj_id').size()
    summ1_unique = summ1.groupby('tid')['category'].nunique()
    summ2_unique = summ2.groupby('tid')['category'].nunique()

    new_row['summarization_rate1'] = (1 - summ1_unique/sem_unique).mean()    
    new_row['summarization_rate2'] = (1 - summ2_unique/sem_unique).mean()
    results.loc[len(results)] = new_row
# %%
results.sort_values('experiment_num',inplace=True)
results.to_csv('summarization_rate_geolife.csv')
