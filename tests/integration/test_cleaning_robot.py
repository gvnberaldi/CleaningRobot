import csv
import io
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
        """
        Tests the history method to ensure the returned CSV data is valid and contains the correct header.
        """
        robot.clean()
        csv_data = robot.history()

        csv_file = io.StringIO(csv_data)
        reader = csv.reader(csv_file)
        rows = list(reader)

        # Assert that there's at least one row (header + data)
        assert len(rows) > 1, "CSV data is empty or does not contain data."

        # Check the header matches the column names of CleaningSession
        header = rows[0]
        expected_header = [column.name for column in CleaningSession.__table__.columns]
        assert header == expected_header, f"Header mismatch: {header} != {expected_header}"

        # Check that the first row matches the data of the valid_cleaning_session
        row_data = rows[1]  # The first row after the header
        assert len(row_data) == len(expected_header), "Row data does not match column count."
