import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from app.map import Map


class TestValidMapData:
    """
    Test valid map data loading from TXT and JSON files.

    This class contains tests to verify that valid TXT and JSON map files
    are correctly loaded, with proper row/column counts and correct walkability
    of tiles.
    """

    def test_valid_txt_files(self, valid_txt_files: list):
        """
        Test loading of valid text map files, ensuring correct row/column count
        and proper walkability of tiles based on the text file's content.

        Args: valid_txt_files (list): Valid text map data for testing.
        """

        for txt_data in valid_txt_files:
            map = Map()
            map.load_from_txt(txt_data)

            # Check that rows and columns are correctly set
            assert map.rows_num() > 0
            assert map.cols_num() > 0

            # Check if the map is correctly loaded (walkable and non-walkable tiles)
            for y in range(map.rows_num()):
                for x in range(map.cols_num()):
                    is_walkable = map.is_walkable(x, y)
                    char = txt_data.splitlines()[y][x]
                    expected_walkable = char == 'o'
                    assert is_walkable == expected_walkable

    def test_valid_json_files(self, valid_json_files: list):
        """
        Test loading of valid JSON map files, ensuring correct row/column count
        and correct walkability of tiles as specified in the JSON data.

        Args: valid_json_files (list): Valid JSON map data for testing.
        """
        for json_data in valid_json_files:
            map = Map()
            map.load_from_json(json_data)

            # Check that rows and columns are correctly set
            assert map.rows_num() == json_data["rows"]
            assert map.cols_num() == json_data["cols"]

            # Check if the map is correctly loaded (walkable and non-walkable tiles)
            for tile in json_data.get("tiles"):
                x, y, walkable = tile.get("x"), tile.get("y"), tile.get("walkable")
                assert map.is_walkable(x, y) == walkable


class TestInvalidMapData:
    """
    Test handling of invalid map data from TXT and JSON files.

    This class contains tests to ensure that invalid TXT and JSON map files
    raise the appropriate errors and that map attributes remain None after a failed load.
    """

    def test_invalid_txt_files(self, invalid_txt_files: list):
        """
        Test handling of invalid text map files, ensuring ValueError is raised
        and attributes remain None after a failed load.

        Args: invalid_txt_files (list): Invalid text map data for testing failure.
        """
        for txt_data in invalid_txt_files:
            map = Map()
            with pytest.raises(ValueError) as e:
                map.load_from_txt(txt_data)

            # Assert that a ValueError was raised
            assert e.type == ValueError
            print(f"Error: {e.value}")

            # Check that the map, rows, and cols are None since loading failed
            assert map.get_map() is None
            assert map.rows_num() is None
            assert map.cols_num() is None

    def test_invalid_json_files(self, invalid_json_files: list):
        """
        Test handling of invalid JSON map files, ensuring ValueError is raised
        and attributes remain None after a failed load.

        Args: invalid_json_files (list): Invalid JSON map data for testing failure.
        """

        for json_data in invalid_json_files:
            map = Map()
            with pytest.raises(ValueError) as e:
                map.load_from_json(json_data)

            # Assert that a ValueError was raised
            assert e.type == ValueError
            print(f"Error: {e.value}")

            # Check that the map, rows, and cols are None since loading failed
            assert map.get_map() is None
            assert map.rows_num() is None
            assert map.cols_num() is None
