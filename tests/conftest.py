import os
import json
import sys
from datetime import datetime, timedelta

import pytest
from pytest_postgresql.factories import postgresql_noproc
from sqlalchemy import create_engine
from sqlalchemy.engine import url
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from app.database import Base, CleaningSession

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


@pytest.fixture(scope="function")
def db_connection():
    """Fixture to provide a temporary test database session."""
    database_url = "postgresql://test:test@localhost:5431/test"
    engine = create_engine(database_url)

    Base.metadata.create_all(engine)  # Create all tables
    session_factory = sessionmaker(bind=engine)
    session = session_factory()  # Provide the session to the test function
    yield session
    # Cleanup: Close session and drop tables
    session.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def valid_cleaning_session():
    """Returns a valid CleaningSession object."""
    return CleaningSession(
        session_start_time=datetime(2025, 2, 6, 10, 4, 2),
        session_final_state="Completed",
        number_of_actions=50,
        number_of_cleaned_tiles=30,
        duration=timedelta(minutes=15)
    )


@pytest.fixture
def invalid_cleaning_session():
    """Returns an invalid CleaningSession object (e.g., missing required fields)."""
    return CleaningSession(
        session_start_time=None,  # Missing required field
        session_final_state="",  # Empty string should be invalid
        number_of_actions=-10,  # Negative value should be invalid
        number_of_cleaned_tiles=30,
        duration="00:45:00"  # String instead of timedelta
    )
