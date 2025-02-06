import os
import json
import pytest

# Get the directory of the synthetic data for the tests
current_file_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(current_file_dir, 'synthetic_data')


@pytest.fixture
def valid_txt_files(request) -> list:
    """
    Fixture that provides valid TXT files for testing.
    Reads and returns a list of valid_data .txt files.
    """

    valid_txt_path = os.path.join(data_dir, request.param)
    txt_files = []
    for file_name in os.listdir(valid_txt_path):
        if file_name.endswith('.txt'):
            with open(os.path.join(valid_txt_path, file_name), 'r') as file:
                txt_files.append(file.read())
    return txt_files


@pytest.fixture
def valid_json_files(request) -> list:
    """
    Fixture that provides valid JSON files for testing.
    Reads and returns a list of valid_data .json files.
    """
    valid_json_path = os.path.join(data_dir, request.param)
    json_files = []
    for file_name in os.listdir(valid_json_path):
        if file_name.endswith('.json'):
            with open(os.path.join(valid_json_path, file_name), 'r') as file:
                json_files.append(json.load(file))
    return json_files


@pytest.fixture
def invalid_txt_files(request) -> list:
    """
    Fixture that provides invalid TXT files for testing.
    Reads and returns a list of invalid .txt files.
    """
    invalid_txt_path = os.path.join(data_dir, request.param)
    txt_files = []
    for file_name in os.listdir(invalid_txt_path):
        with open(os.path.join(invalid_txt_path, file_name), 'r') as file:
            txt_files.append(file.read())
    return txt_files


@pytest.fixture
def invalid_json_files(request) -> list:
    """
    Fixture that provides invalid JSON files for testing.
    Reads and returns a list of invalid .json files.
    """
    invalid_json_path = os.path.join(data_dir, request.param)
    json_files = []
    for file_name in os.listdir(invalid_json_path):
        with open(os.path.join(invalid_json_path, file_name), 'r') as file:
            json_files.append(file.read())
    return json_files
