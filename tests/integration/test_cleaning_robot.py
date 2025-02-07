import csv
import os

import pytest
import json

from app.database import CleaningSession


class TestCleaningRobot:
    """
    Test suite for the CleaningRobot's clean method.
    Covers successful cleaning, out-of-bounds errors, and non-walkable tile errors.
    """

    @pytest.mark.parametrize("map_actions_files", [("maps/valid_data/txt/map_1.txt",
                                                    "actions/valid_data/txt/actions_1.txt")], indirect=True)
    def test_clean_completed(self, robot):
        """
        Test that the clean method completes successfully with a valid map and path.
        """
        report = json.loads(robot.clean())
        assert report["status"] == "completed"
        assert "error" in report and report["error"] is None

    @pytest.mark.parametrize("map_actions_files", [("maps/valid_data/txt/map_2.txt",
                                                    "actions/valid_data/txt/actions_2.txt")], indirect=True)
    def test_clean_out_of_bounds(self, robot):
        """
        Test that the clean method returns an error when the robot moves out of bounds.
        """
        report = json.loads(robot.clean())
        assert report["status"] == "error"
        assert "out of map bounds" in report["error"]

    @pytest.mark.parametrize("map_actions_files", [("maps/valid_data/txt/map_3.txt",
                                                    "actions/valid_data/txt/actions_3.txt")], indirect=True)
    def test_clean_non_walkable_tile(self, robot):
        """
        Test that the clean method returns an error when the robot moves to a non-walkable tile.
        """
        report = json.loads(robot.clean())
        print(report)
        assert report["status"] == "error"
        assert "non-walkable tile" in report["error"]

    @pytest.mark.parametrize("map_actions_files", [("maps/valid_data/txt/map_3.txt",
                                                    "actions/valid_data/txt/actions_3.txt")], indirect=True)
    def test_history(self, robot):
        robot.clean()
        robot.history()
        # Check if the CSV file was created
        file_path = os.path.join(os.getcwd(), "cleaning_sessions.csv")
        assert os.path.exists(file_path), "CSV file was not created."

        # Read the content of the CSV file and validate the data
        with open(file_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            rows = list(reader)
            # Assert that there's at least one row (header + data)
            assert len(rows) > 1, "CSV file is empty or does not contain data."
            # Check the header matches the column names of CleaningSession
            header = rows[0]
            expected_header = [column.name for column in CleaningSession.__table__.columns]
            assert header == expected_header, f"Header mismatch: {header} != {expected_header}"
            # Check that the first row matches the data of the valid_cleaning_session
            row_data = rows[1]  # The first row after the header
            assert len(row_data) == len(expected_header), "Row data does not match column count."

        # Delete the created CSV file after the test is complete
        if os.path.exists(file_path):
            os.remove(file_path)
            assert not os.path.exists(file_path), "CSV file was not deleted."
