import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from app.robot_path import RobotPath  # Update with the actual module name


class TestValidRobotPathData:
    """
    Test valid_data robot path data loading from TXT and JSON files.

    This class contains tests to verify that valid_data TXT and JSON robot path files
    are correctly loaded, with proper field checks and correct validation of coordinates
    and actions.
    """

    @pytest.mark.parametrize("valid_txt_files", ["actions/valid_data/txt"], indirect=True)
    def test_valid_txt_files(self, valid_txt_files: list):
        """
        Test loading of valid robot path data from TXT files.

        Verifies that the coordinates and actions in the TXT files are correctly
        parsed and loaded into the robot's attributes.

        Args: List of valid robot path data in TXT format.
        """

        for txt_data in valid_txt_files:
            robot_path = RobotPath.load_from_txt(txt_data)

            # Extract expected x, y coordinates and actions from txt_data
            lines = txt_data.splitlines()
            expected_x, expected_y = map(int, lines[0].split())
            expected_actions = []
            for line in lines[1:]:
                direction, steps = line.strip().split()
                expected_actions.append({"direction": direction.lower(), "steps": int(steps)})

            # Check that the coordinates and actions match the expected values
            assert robot_path.x == expected_x
            assert robot_path.y == expected_y
            for i, action in enumerate(robot_path.actions):
                assert action.direction == expected_actions[i]["direction"]
                assert action.steps == expected_actions[i]["steps"]

    @pytest.mark.parametrize("valid_json_files", ["actions/valid_data/json"], indirect=True)
    def test_valid_json_files(self, valid_json_files: list):
        """
        Test loading of valid robot path data from JSON files.

        Verifies that the coordinates and actions in the JSON files are correctly
        parsed and loaded into the robot's attributes.

        Args: List of valid robot path data in JSON format.
        """

        for json_data in valid_json_files:
            robot_path = RobotPath.load_from_json(json_data)

            # Extract expected coordinates and actions from the JSON data
            expected_x = json_data["x"]
            expected_y = json_data["y"]
            expected_actions = json_data["actions"]

            # Check that the coordinates and actions match the expected values
            assert robot_path.x == expected_x
            assert robot_path.y == expected_y
            for i, action in enumerate(robot_path.actions):
                assert action.direction == expected_actions[i]["direction"]
                assert action.steps == expected_actions[i]["steps"]


class TestInvalidRobotPathData:
    """
    Test handling of invalid robot path data from TXT and JSON files.

    This class contains tests to ensure that invalid TXT and JSON robot path files
    raise the appropriate errors and that robot path attributes remain None after a failed load.
    """

    @pytest.mark.parametrize("invalid_txt_files", ["actions/invalid_data/txt"], indirect=True)
    def test_invalid_txt_files(self, invalid_txt_files: list):
        """
        Test handling of invalid text robot path files, ensuring ValueError is raised
        and attributes remain None after a failed load.

        Args: invalid_txt_files (list): Invalid text robot path data for testing failure.
        """
        for txt_data in invalid_txt_files:
            with pytest.raises(ValueError) as e:
                RobotPath.load_from_txt(txt_data)

            # Assert that a ValueError was raised
            assert e.type == ValueError
            print(f"Error: {e.value}")

    @pytest.mark.parametrize("invalid_json_files", ["actions/invalid_data/json"], indirect=True)
    def test_invalid_json_files(self, invalid_json_files: list):
        """
        Test handling of invalid JSON robot path files, ensuring ValueError is raised
        and attributes remain None after a failed load.

        Args: invalid_json_files (list): Invalid JSON robot path data for testing failure.
        """

        for json_data in invalid_json_files:

            with pytest.raises(ValueError) as e:
                RobotPath.load_from_json(json_data)

            # Assert that a ValueError was raised
            assert e.type == ValueError
            print(f"Error: {e.value}")
