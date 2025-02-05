import os
import json
import pytest

# Get the directory of the synthetic data for the tests
current_file_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(current_file_dir, 'synthetic_data')


@pytest.fixture
def valid_txt_files():
    valid_txt_path = os.path.join(data_dir, 'valid_data/txt')
    txt_files = []
    for file_name in os.listdir(valid_txt_path):
        if file_name.endswith('.txt'):
            with open(os.path.join(valid_txt_path, file_name), 'r') as file:
                txt_files.append(file.read())
    return txt_files


@pytest.fixture
def valid_json_files():
    valid_json_path = os.path.join(data_dir, 'valid_data/json')
    json_files = []
    for file_name in os.listdir(valid_json_path):
        if file_name.endswith('.json'):
            with open(os.path.join(valid_json_path, file_name), 'r') as file:
                json_files.append(json.load(file))
    return json_files


@pytest.fixture
def invalid_txt_files():
    invalid_txt_path = os.path.join(data_dir, 'invalid_data/txt')
    txt_files = []
    for file_name in os.listdir(invalid_txt_path):
        with open(os.path.join(invalid_txt_path, file_name), 'r') as file:
            txt_files.append(file.read())
    return txt_files


@pytest.fixture
def invalid_json_files():
    invalid_json_path = os.path.join(data_dir, 'invalid_data/json')
    json_files = []
    for file_name in os.listdir(invalid_json_path):
        with open(os.path.join(invalid_json_path, file_name), 'r') as file:
            json_files.append(file.read())
    return json_files
