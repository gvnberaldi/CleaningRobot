import csv
import io
import json

import pytest

from app import config
from app.database import CleaningSession


class TestSetMapEndpoint:
    def test_set_map_no_file(self, client):
        """
        Test the /set-map endpoint when no file is uploaded.
        """
        response = client.post('/set-map')
        assert response.status_code == 400
        assert response.json['error'] == 'No map file uploaded'

    @pytest.mark.parametrize("files", ["maps/valid_data/txt"], indirect=True)
    def test_set_map_success_txt(self, client, files):
        """
        Test the /set-map endpoint when uploading valid map files.
        """
        for file in files:
            response = client.post('/set-map', data={'file': file})

            # Check if the upload was successful
            assert response.status_code == 200
            assert response.json['message'] == 'Map uploaded successfully!'

    @pytest.mark.parametrize("files", ["maps/valid_data/json"], indirect=True)
    def test_set_map_success_json(self, client, files):
        """
        Test the /set-map endpoint when uploading valid map files.
        """
        for file in files:
            response = client.post('/set-map', data={'file': file})

            # Check if the upload was successful
            assert response.status_code == 200
            assert response.json['message'] == 'Map uploaded successfully!'

    @pytest.mark.parametrize("files", ["maps/invalid_data/txt"], indirect=True)
    def test_set_map_error_txt(self, client, files):
        """
        Test the /set-map endpoint when uploading invalid map files.
        """
        for file in files:
            response = client.post('/set-map', data={'file': file})

            # Check if the error is handled correctly
            assert response.status_code == 500

    @pytest.mark.parametrize("files", ["maps/invalid_data/json"], indirect=True)
    def test_set_map_error_json(self, client, files):
        """
        Test the /set-map endpoint when uploading invalid map files.
        """
        for file in files:
            response = client.post('/set-map', data={'file': file})

            # Check if the error is handled correctly
            assert response.status_code == 500


class TestCleanEndpoint:
    def test_clean_no_file(self, client):
        """
        Test the /clean endpoint when no file is uploaded.
        """
        response = client.post('/clean')
        assert response.status_code == 400
        assert response.json['error'] == 'No actions file uploaded'

    @pytest.mark.parametrize("files", ["actions/valid_data/txt"], indirect=True)
    def test_clean_no_map(self, client, files):
        """
        Test the /set-map endpoint when no map is initialized.
        """
        config.map = None
        for file in files:
            response = client.post('/clean', data={'file': file})

            # Check if the upload was successful
            assert response.status_code == 400
            assert response.json['error'] == 'No map loaded: a map must be loaded before cleaning'

    @pytest.mark.parametrize("map_actions_files", [("maps/valid_data/txt/map_1.txt",
                                                    "actions/invalid_data/txt/actions_1.txt")], indirect=True)
    def test_clean_invalid_actions_txt_file(self, client, map_actions_files):
        map_file, action_file = map_actions_files
        client.post('/set-map', data={'file': map_file})
        response = client.post('/clean', data={'file': action_file})

        assert response.status_code == 500

    @pytest.mark.parametrize("map_actions_files", [("maps/valid_data/txt/map_1.txt",
                                                    "actions/invalid_data/json/actions_1.json")], indirect=True)
    def test_clean_invalid_actions_json_file(self, client, map_actions_files):
        map_file, action_file = map_actions_files
        client.post('/set-map', data={'file': map_file})
        response = client.post('/clean', data={'file': action_file})

        assert response.status_code == 500

    @pytest.mark.parametrize("map_actions_files", [("maps/valid_data/txt/map_1.txt",
                                                    "actions/valid_data/txt/actions_1.txt")], indirect=True)
    def test_clean_completed(self, client, map_actions_files):
        map_file, action_file = map_actions_files
        client.post('/set-map', data={'file': map_file})
        response = client.post('/clean', data={'file': action_file})
        # Extract the cleaning report from the response
        report = response.get_json().get('report')
        print(response)
        # Check if the clean session was successful
        assert response.status_code == 200
        assert report is not None
        assert report['status'] == 'completed'

    @pytest.mark.parametrize("map_actions_files", [("maps/valid_data/txt/map_2.txt",
                                                    "actions/valid_data/txt/actions_2.txt")], indirect=True)
    def test_clean_out_of_bounds_error(self, client, map_actions_files):
        map_file, action_file = map_actions_files
        client.post('/set-map', data={'file': map_file})
        response = client.post('/clean', data={'file': action_file})
        # Extract the cleaning report from the response
        report = response.get_json().get('report')

        # Check if the clean session status
        assert response.status_code == 200
        assert report is not None
        assert report['status'] == 'error'
        assert "out of map bounds" in report['error']

    @pytest.mark.parametrize("map_actions_files", [("maps/valid_data/txt/map_3.txt",
                                                    "actions/valid_data/txt/actions_3.txt")], indirect=True)
    def test_clean_non_walkable_error(self, client, map_actions_files):
        map_file, action_file = map_actions_files
        client.post('/set-map', data={'file': map_file})
        response = client.post('/clean', data={'file': action_file})
        # Extract the cleaning report from the response
        report = response.get_json().get('report')

        # Check if the clean session status
        assert response.status_code == 200
        assert report is not None
        assert report['status'] == 'error'
        assert "non-walkable tile" in report['error']


class TestHistoryEndpoint:
    def test_history_endpoint_success(self, client, db_connection, valid_cleaning_session):
        """Test the /history endpoint for returning a valid CSV response."""
        # Insert the valid session into the database
        db_connection.create_table()
        db_connection.save_session(valid_cleaning_session)

        response = client.get('/history')
        # Check that the response is successful
        assert response.status_code == 200
        assert 'text/csv' in response.content_type

        csv_content = io.StringIO(response.data.decode())
        reader = csv.reader(csv_content)
        rows = list(reader)

        # Verify that the CSV has the expected structure and data
        assert len(rows) > 1, "CSV data is empty or does not contain data."

        # Check the header matches the column names of CleaningSession
        header = rows[0]
        expected_header = [column.name for column in CleaningSession.__table__.columns]
        assert header == expected_header, f"Header mismatch: {header} != {expected_header}"

        # Extract the expected values from valid_cleaning_session
        expected_values = [
            str(getattr(valid_cleaning_session, column.name)) for column in CleaningSession.__table__.columns
        ]

        # Compare the retrieved data row with the expected values
        data_row = rows[1]
        assert data_row == expected_values, f"Data mismatch: {data_row} != {expected_values}"

    def test_history_endpoint_error_no_table(self, client, db_connection, valid_cleaning_session):
        response = client.get('/history')
        assert response.status_code == 500

    def test_history_endpoint_error_no_value(self, client, db_connection, valid_cleaning_session):
        db_connection.create_table()
        response = client.get('/history')
        assert response.status_code == 500
