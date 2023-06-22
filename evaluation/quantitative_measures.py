# %%
import pandas as pd
import os
import glob
# %%
results = pd.DataFrame(columns=['experiment_num','sem_mean','sem_median','sem_std','summ1_mean','summ1_median','summ1_std','summ2_mean','summ2_median','summ2_std'])

for filename in glob.glob('../config-gps/*.json'):

    name = os.path.splitext(filename)[0]
    
    new_row = {}

    experiment_number = name[-3:]

    sem_trajs = pd.read_parquet(f'../output-gps/semantic_trajs_{experiment_number}.parquet')
    summ1 = pd.read_parquet(f'../output-gps/summarized1_{experiment_number}.parquet')
    summ2 = pd.read_parquet(f'../output-gps/summarized2_{experiment_number}.parquet')

    new_row['experiment_num'] = experiment_number

    new_row['sem_mean'] = sem_trajs.groupby('tid').size().mean()
    new_row['sem_median'] = sem_trajs.groupby('tid').size().median()
    new_row['sem_std'] = sem_trajs.groupby('tid').size().std()

    new_row['summ1_mean'] = summ1.groupby('tid').size().mean()
    new_row['summ1_median'] = summ1.groupby('tid').size().median()
    new_row['summ1_std'] = summ1.groupby('tid').size().std()

    new_row['summ2_mean'] = summ2.groupby('tid').size().mean()
    new_row['summ2_median'] = summ2.groupby('tid').size().median()
    new_row['summ2_std'] = summ2.groupby('tid').size().std()
    
    results.loc[len(results)] = new_row
# %%
results.sort_values('experiment_num',inplace=True)
results.to_csv('quantitative_results_geolife.csv')
# %%
