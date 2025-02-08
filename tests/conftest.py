import io
import os
import json
import sys
from datetime import datetime, timedelta
import pytest
from werkzeug.datastructures import FileStorage

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
from app.database import Base, CleaningSession, Database
from app.cleaning_robot import BaseCleaningRobot
from app.map import Map
from app.robot_path import RobotPath
from app.app import my_app

# Get the directory of the synthetic data for the tests
current_file_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(current_file_dir, 'synthetic_data')


@pytest.fixture
def files(request) -> list:
    """
    Fixture that provides valid TXT files for testing.
    Reads and returns a list of valid_data .txt files.
    """

    path = os.path.join(data_dir, request.param)
    files = []
    for file_name in os.listdir(path):
        file_path = os.path.join(path, file_name)
        with open(file_path, 'rb') as file:
            # Create a FileStorage object for each file to simulate HTTP file request
            file_stream = io.BytesIO(file.read())
            file_storage = FileStorage(
                stream=file_stream,
                filename=file_name,
                content_type='application/octet-stream'
            )
            files.append(file_storage)
    return files


@pytest.fixture
def map_actions_files(request) -> tuple:
    """
    Fixture providing a tuple of TXT map and action file.
    """
    map_path, actions_path = request.param
    map_file = os.path.join(data_dir, map_path)
    actions_file = os.path.join(data_dir, actions_path)
    with open(map_file, 'rb') as map_file:
        map_file_stream = io.BytesIO(map_file.read())
        map_data = FileStorage(
            stream=map_file_stream,
            filename=map_path,
            content_type='application/octet-stream'
        )
    with open(actions_file, 'rb') as actions_file:
        actions_file_stream = io.BytesIO(actions_file.read())
        actions_data = FileStorage(
            stream=actions_file_stream,
            filename=actions_path,
            content_type='application/octet-stream'
        )
    return map_data, actions_data


@pytest.fixture
def robot(db_connection, map_actions_files):
    """
    Fixture that returns an instantiated BaseCleaningRobot object.
    """
    map_file, action_file = map_actions_files
    map_instance = Map.load(map_file)
    path_instance = RobotPath.load(action_file)
    robot_instance = BaseCleaningRobot(map=map_instance, path=path_instance, database_conn=db_connection)
    return robot_instance


@pytest.fixture(scope="function")
def db_connection():
    db_instance = Database.connect()
    yield db_instance  # Provide the database instance to the test function
    # Cleanup: Close session and drop tables
    db_instance.close()
    Base.metadata.drop_all(db_instance.session.bind)


@pytest.fixture
def valid_cleaning_session():
    """Returns a valid CleaningSession object."""
    return CleaningSession(
        session_start_time=datetime(2025, 2, 6, 10, 4, 2),
        session_final_state="completed",
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


@pytest.fixture
def app(db_connection):
    """Fixture to provide the Flask app context."""
    original_config = my_app.config.copy()
    my_app.config.update({"TESTING": True})
    my_app.config.update({"DATABASE": db_connection})
    yield my_app
    my_app.config.clear()
    my_app.config.update(original_config)


@pytest.fixture
def client(app):
    """Fixture to provide a Flask test client."""
    return app.test_client()
