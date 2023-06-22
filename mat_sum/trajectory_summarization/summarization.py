# %%
import pandas as pd 
import geopandas as gpd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import pairwise_distances
# %%
def semantic_enrichment(gdf,areas,config):
    '''
    Semantic enrichment of trajectories.
    Return GeoDataFrame of semantic trajectories.

    gdf: GeoDataFrame containing trajectories

    areas: GeoDataFrame containing areas
    '''

    sem_trajs = gdf.sjoin(areas)
    sem_trajs = sem_trajs[~sem_trajs.index.duplicated(keep='first')]
    if config['input_type'] == 'check-in':
        if 'category' in sem_trajs.columns:
            sem_trajs['count'] = sem_trajs.groupby([config['input_tid_column'],'category_right'])[config['input_tid_column']].transform('count')
        else:
            sem_trajs['count'] = sem_trajs.groupby([config['input_tid_column'],'category'])[config['input_tid_column']].transform('count')
        sem_trajs.sort_index(inplace=True)
    elif config['input_type'] == 'gps':
        sem_trajs['end_date'] = sem_trajs.groupby(config['input_tid_column'],as_index=False)[config['input_time_column']].shift(-1)
        sem_trajs['duration'] = sem_trajs['end_date'] - sem_trajs[config['input_time_column']]

    return sem_trajs
# %%
def summarize_trajectories1(sem_trajs,config):
    '''
    Summarize semantic trajectories (attempt 1 -> put together only areas with exactly the same aspects)
    Return a GeoDataFrame of summary trajectories.

    sem_trajs: GeoDataFrame containing semantic trajecories
    '''

    df = sem_trajs.copy()
    if config['input_type'] == 'check-in':
        df['count'] = df.groupby([config['input_tid_column'],'category_right'])[config['input_tid_column']].transform('count')
    if 'category_right' in df.columns:
        df.set_index([config['input_tid_column'],'category_right'],inplace=True)
        for col in config['input_columns']:
            df[col] = df.groupby([config['input_tid_column'],'category_right'])[col].apply(set)
        df.reset_index(inplace=True)
        summ_trajs = df.drop_duplicates([config['input_tid_column'],'category_right'])
    else:
        df.set_index([config['input_tid_column'],'category'],inplace=True)
        for col in config['input_columns']:
            df[col] = df.groupby([config['input_tid_column'],'category'])[col].apply(set)
        df.reset_index(inplace=True)
        summ_trajs = df.drop_duplicates([config['input_tid_column'],'category'])
    
    return summ_trajs
# %%
def create_similarity_matrix(areas):

    df_areas = areas[['category','label_tfidf']]
    areas_as_docs = pd.DataFrame(df_areas['label_tfidf'].apply(lambda x: " ".join(x)))
    
    vectorizer = CountVectorizer(binary=True)
    vectorizer.fit(areas_as_docs['label_tfidf'])

    X = vectorizer.transform(areas_as_docs['label_tfidf'])
    df = pd.DataFrame(X.toarray(), columns=vectorizer.get_feature_names_out())

    similarity_matrix = pd.DataFrame(1 - pairwise_distances(df.to_numpy(), metric='cosine'), index=df.index, columns=df.index)

    return similarity_matrix
# %%
def similar_locations_computation(similar_matrix,threshold):

    similar_locations = similar_matrix.gt(threshold).apply(lambda x: x.index[x].tolist(), axis=1)
    similar_locations = pd.DataFrame(similar_locations)
    return similar_locations

def summarization2(sem_trajs,threshold,areas,config):

    similarity_matrix = create_similarity_matrix(areas)
    similar_locations = similar_locations_computation(similarity_matrix,threshold)

    df_copy = sem_trajs.copy()
    if config['input_type'] == 'check-in':
        df_copy['count'] = df_copy.groupby([config['input_tid_column'],'category_right'])[config['input_tid_column']].transform('count')
    if 'category_right' in df_copy.columns:
        df_copy.set_index([config['input_tid_column'],'category_right'],inplace=True)
        for col in config['input_columns']:
            df_copy[col] = df_copy.groupby([config['input_tid_column'],'category_right'])[col].apply(lambda x: set([x]))
        df_copy.reset_index(inplace=True)
    else:
        df_copy.set_index([config['input_tid_column'],'category'],inplace=True)
        for col in config['input_columns']:
            df_copy[col] = df_copy.groupby([config['input_tid_column'],'category'])[col].apply(lambda x: set([x]))
        df_copy.reset_index(inplace=True)
        
    df_copy['label_right'] = df_copy['label_tfidf'].apply(lambda x: set(x))
    sem_trajs['aspects'] = sem_trajs['label_tfidf'].apply(lambda x: set(x))
    groups = df_copy.groupby(config['input_tid_column'])

    if config['input_type'] == 'check-in':
        category_col = 'category_right'
    else:
        category_col = 'category'

    for group_name,group in groups:
        
        for row_index,row in group.iterrows():

            if row_index in df_copy.index:
             
                aspects = row['label_right']
                
                for i,r in group.iterrows():
                    
                    if i > row_index:
        
                        if (r[category_col] in similar_locations.loc[row[category_col],0]) and (i in df_copy.index):
                            if config['input_type'] == 'check-in':
                                df_copy.loc[row_index,'count'] += 1
                            else:
                                df_copy.loc[row_index,'duration'] += r['duration']
                            aspects = aspects.intersection(r['label_right'])
                            for col in config['input_columns']:
                                df_copy.loc[row_index,col].update(r[col])
                                
                            df_copy = df_copy.drop(i)

                df_copy.loc[row_index,'label_right'] = str(aspects)

    df_copy['label_right'] = df_copy['label_right'].apply(eval)
   
    return df_copy
