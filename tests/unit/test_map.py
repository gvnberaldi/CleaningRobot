import sys
import os
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from app.map import Map


class TestValidMapData:
    def test_valid_txt_files(self, valid_txt_files):
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

    def test_valid_json_files(self, valid_json_files):
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

    def test_invalid_txt_files(self, invalid_txt_files):
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

    def test_invalid_json_files(self, invalid_json_files):
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
