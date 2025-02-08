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
