# %%
import json

tessellations = ['squares','hexagons']
semantic_aspects = ['POIs','landuse','public_transport','all','POIs+landuse','POIs+public_transport','landuse+public_transport']
thresholds = [0.6,0.7,0.8,0.9]
resolutions_s = [16,17,18]
resolutions_h = [6,7,8]

config_dict = dict()
i = 0

for t in tessellations:

    if t == 'squares':
        resolutions = resolutions_s
    else:
        resolutions = resolutions_h

    for r in resolutions:

        for th in thresholds:

            for sa in semantic_aspects: 
                
                i += 1

                config_dict['tessellation'] = {}
                config_dict['semantic_aspects'] = {}

                config_dict['tessellation']['type'] = t
                config_dict['tessellation']['resolution'] = r

                path_pois = "/home/chiarap/foursquare/geolife/labeled_pois.parquet"
                path_landuse = "/home/chiarap/foursquare/geolife/labeled_landuse.parquet"
                path_publictransport = "/home/chiarap/foursquare/geolife/labeled_public_transport.parquet"

                if sa == 'all':
                    config_dict['semantic_aspects']['POIs'] = path_pois
                    config_dict['semantic_aspects']['landuse'] = path_landuse
                    config_dict['semantic_aspects']['public_transport'] = path_publictransport
                elif sa == 'POIs+landuse':
                    config_dict['semantic_aspects']['POIs'] = path_pois
                    config_dict['semantic_aspects']['landuse'] = path_landuse
                    config_dict['semantic_aspects']['public_transport'] = ''
                elif sa == 'POIs+public_transport':
                    config_dict['semantic_aspects']['POIs'] = path_pois
                    config_dict['semantic_aspects']['landuse'] = ''
                    config_dict['semantic_aspects']['public_transport'] = path_publictransport
                elif sa == 'landuse+public_transport':
                    config_dict['semantic_aspects']['POIs'] = ''
                    config_dict['semantic_aspects']['landuse'] = path_landuse
                    config_dict['semantic_aspects']['public_transport'] = path_publictransport
                elif sa == 'POIs':
                    config_dict['semantic_aspects']['POIs'] = path_pois
                    config_dict['semantic_aspects']['landuse'] = ''
                    config_dict['semantic_aspects']['public_transport'] = ''
                elif sa == 'landuse':
                    config_dict['semantic_aspects']['POIs'] = ''
                    config_dict['semantic_aspects']['landuse'] = path_landuse
                    config_dict['semantic_aspects']['public_transport'] = ''
                else:
                    config_dict['semantic_aspects']['POIs'] = ''
                    config_dict['semantic_aspects']['landuse'] = ''
                    config_dict['semantic_aspects']['public_transport'] = path_publictransport

                config_dict['threshold'] = th

                if i < 10:
                    with open(f'../config-gps/config00{i}.json','w') as f:
                        json.dump(config_dict,f)
                elif i < 100:
                    with open(f'../config-gps/config0{i}.json','w') as f:
                        json.dump(config_dict,f)
                else:
                    with open(f'../config-gps/config{i}.json','w') as f:
                        json.dump(config_dict,f)
# %%
