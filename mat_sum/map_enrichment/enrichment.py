# %%
import geopandas as gpd
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
# %%
def enrich_areas(locations,pois,landuse,public_transport):
    '''
    Adds the semantic aspects to the tessellation areas.
    locations: tessellation areas
    pois: GeoDataFrame with POIs
    landuse: GeoDataFrame with landuse
    public_transport: GeoDataFrame with public transport
    
    Returns a GeoDataFrame with the tessellation areas and the semantic aspects.
    '''
    if len(pois) != 0:
        poi_with_areas = pois.sjoin(locations)
    #poi_with_areas = pois.sjoin(locations)
    if len(landuse) != 0:
        landuse_with_areas = landuse.sjoin(locations)
    if len(public_transport) != 0:
        public_transport_with_areas = public_transport.sjoin(locations)

    locations.set_index('locationID',inplace=True)
    
    if len(pois) != 0: 
        poi_with_areas.set_index('locationID',inplace=True)

    if len(landuse) != 0:
        landuse_with_areas.set_index('locationID',inplace=True)
        landuse_with_areas['label'] = landuse_with_areas['POI category']

    if len(public_transport) != 0:
        public_transport_with_areas.set_index('locationID',inplace=True)
        public_transport_with_areas['label'] = public_transport_with_areas['POI category']

    if len(landuse) != 0 and len(public_transport) != 0 and len(pois) != 0:
        semantic_aspect_areas = pd.concat([poi_with_areas,landuse_with_areas,public_transport_with_areas])
    elif len(landuse) == 0 and len(public_transport) != 0 and len(pois) != 0:
        semantic_aspect_areas = pd.concat([poi_with_areas,public_transport_with_areas])
    elif len(landuse) != 0 and len(public_transport) == 0 and len(pois) != 0:
        semantic_aspect_areas = pd.concat([poi_with_areas,landuse_with_areas])
    elif len(landuse) != 0 and len(public_transport) != 0 and len(pois) == 0:
        semantic_aspect_areas = pd.concat([public_transport_with_areas,landuse_with_areas])
    elif len(landuse) != 0 and len(public_transport) == 0 and len(pois) == 0:
        semantic_aspect_areas = landuse_with_areas.copy()
    elif len(landuse) == 0 and len(public_transport) != 0 and len(pois) == 0:
        semantic_aspect_areas = public_transport_with_areas.copy()
    elif len(landuse) == 0 and len(public_transport) == 0 and len(pois) != 0:
        semantic_aspect_areas = poi_with_areas.copy()
        
    areas = pd.DataFrame(semantic_aspect_areas.groupby('locationID')['label'].apply(lambda x: str(sorted(set(x)))))
    mapping = dict(zip(areas['label'].unique(),range(0,len(areas['label'].unique()))))
    areas['category'] = areas['label'].map(mapping)
    areas['geometry'] = locations.loc[areas.index,'geometry']
    areas = gpd.GeoDataFrame(areas)
    areas.to_parquet('data/original_areas.parquet')

    areas_as_docs = pd.DataFrame(semantic_aspect_areas[['label']])
    areas_as_docs['label'] = areas_as_docs['label'].str.replace(",","")
    areas_as_docs['label'] = areas_as_docs['label'].str.replace(" ","_")
    areas_as_docs = pd.DataFrame(areas_as_docs.groupby('locationID')['label'].apply(lambda x: " ".join(x)))

    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(areas_as_docs['label'].values.tolist())
    feature_names = vectorizer.get_feature_names_out()
    dense = vectors.todense()
    denselist = dense.tolist()
    tfidf = pd.DataFrame(denselist, columns=feature_names)

    tfidf.to_csv('data/areas_as_doc.csv')

    tfidf = pd.DataFrame(tfidf.stack())
    tfidf = tfidf[tfidf[0]!=0]
    tfidf.reset_index(inplace=True)
    tfidf = tfidf.groupby('level_0', group_keys=False).apply(lambda x: x.sort_values(0,ascending=False))

    areas['label_tfidf'] = ''
    areas_tfidf = pd.DataFrame(tfidf.groupby('level_0')['level_1'].apply(list))
    areas_tfidf['locationID'] = areas.index

    areas_tfidf.set_index('locationID',inplace=True)
    areas['label_tfidf'] = areas_tfidf['level_1']
    areas_unified = areas.dissolve(by='category', aggfunc='first', as_index=False, level=None, sort=True, observed=False, dropna=False)

    areas_unified.to_parquet('data/unified_areas.parquet')

    return areas_unified