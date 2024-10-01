import os
import json

def fetch_custom_columns(custom_column_config_file_path):
    with open(custom_column_config_file_path) as config_file:
        config = config_file.read().splitlines()

    custom_columns = []

    for column_name in config:
        value = input(f'Enter {column_name}: ').strip()
        if value is None or value == '':
            raise Exception(f'Value for a column name in config cannot be empty. '
                            f'Run without config if custom columns are not required.')
        custom_columns.append({column_name: value})

    return custom_columns


def return_file_name_components(file_path):
    output_data_path = os.getcwd()
    file_path_arr = file_path.split("/")
    file_name = file_path_arr[-1]
    file_name_without_extension = file_name.rsplit('.', 1)[0]

    return output_data_path, file_name, file_name_without_extension


def write_to_output_file(output_data_path, file_name_without_extension, output, index_name):
    os.makedirs(f"{output_data_path}/open_search_data", exist_ok=True)
    with open(f"{output_data_path}/open_search_data/{file_name_without_extension}.json", "w") as f:
        for content in output:
            f.write(json.dumps({"index": {"_index": index_name}}) + '\n')
            f.write(json.dumps(content) + "\n")
