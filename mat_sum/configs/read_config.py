import json

def read_config_file():
    """
    Read the config file and return the config dictionary
    """
    data = json.load(open('config.json'))
    input_path = data['input_path']
    output_path = data['output_path']
    experiment_path = data['experiment_path']
    experiment_num = data['experiment_num']
    input_type = data['input_type']
    input_columns = data['input_file_columns']
    input_lat_column = data['input_lat_column']
    input_lon_column = data['input_lon_column']
    input_time_column = data['input_time_column']
    input_tid_column = data['input_tid_column']
    place = data['place']
    
    config = {}
    config['input_path'] = input_path
    config['output_path'] = output_path
    config['experiment_path'] = experiment_path
    config['experiment_num'] = experiment_num
    config['input_type'] = input_type
    config['input_columns'] = input_columns
    config['input_lat_column'] = input_lat_column
    config['input_lon_column'] = input_lon_column
    config['input_time_column'] = input_time_column
    config['input_tid_column'] = input_tid_column
    config['place'] = place
    
    return config
