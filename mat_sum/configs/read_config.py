import json

def read_config_file():
    """
    Read the config file and return the config dictionary
    """
    data = json.load(open('config.json'))
    input_path = data['input_path']
    output_path = data['output_path']
    experiment_path = data['experiment_path']
    input_file_columns = data['input_file_columns']
    input_lat_column = data['input_lat_column']
    input_lon_column = data['input_lon_column']
    place = data['place']
    
    config = {}
    config['input_path'] = input_path
    config['output_path'] = output_path
    config['experiment_path'] = experiment_path
    config['input_file_columns'] = input_file_columns
    config['input_lat_column'] = input_lat_column
    config['input_lon_column'] = input_lon_column
    config['place'] = place
    
    return config
