import json

from pydantic import BaseModel, Field, ValidationError, model_validator, validator, field_validator
from typing import List


class _Tile(BaseModel):
    x: int = Field(..., ge=0, description="X-coordinate of the tile (must be >= 0)")
    y: int = Field(..., ge=0, description="Y-coordinate of the tile (must be >= 0)")
    walkable: bool = Field(..., description="True if the tile is walkable, False otherwise")


class _JSONmapData(BaseModel):
    rows: int = Field(..., gt=0, description="Number of rows in the map (must be > 0)")
    cols: int = Field(..., gt=0, description="Number of columns in the map (must be > 0)")
    tiles: List[_Tile] = Field(..., description="List of tiles defining the map layout")

    @model_validator(mode="after")
    def validate_map_data(cls, model):
        """Ensure tile count matches rows * cols and coordinates are correct."""
        rows = model.rows
        cols = model.cols
        tiles = model.tiles

        # Validate tile count
        if len(tiles) != rows * cols:
            raise ValueError("Mismatch: The number of tiles must be exactly rows × cols.")

        # Validate coordinates
        expected_coords = {(x, y) for y in range(rows) for x in range(cols)}
        actual_coords = {(tile.x, tile.y) for tile in tiles}
        if actual_coords != expected_coords:
            raise ValueError("Tile list does not contain exactly one entry for each grid cell.")

        return model


class _TXTmapData(BaseModel):
    rows: int = Field(..., gt=0, description="Number of rows in the map (must be > 0)")
    cols: int = Field(..., gt=0, description="Number of columns in the map (must be > 0)")
    grid: List[str] = Field(..., description="List of strings representing the map rows")

    @field_validator("grid")
    def validate_grid(cls, grid):
        """Ensure all rows have the same length and contain only 'x' or 'o'."""
        if not grid:
            raise ValueError("Map grid cannot be empty.")

        # Check if all rows are of the same length
        if len(set(len(row) for row in grid)) != 1:
            raise ValueError("All rows must be the same length.")

        for row in grid:
            if any(c not in {'x', 'o'} for c in row):
                raise ValueError("Invalid character found. Only 'x' and 'o' are allowed.")

        return grid


class Map(BaseModel):

    map: List[List[bool]] = Field(..., description="2D matrix representing the map", frozen=True)
    rows: int = Field(..., ge=0, description="The number of map's row must be greater than zero", frozen=True)
    cols: int = Field(..., ge=0, description="The number of map's column must be greater than zero", frozen=True)

    @classmethod
    def load_from_json(cls, json_data):
        """Parses, validate and loads map data from a JSON file."""
        try:
            if isinstance(json_data, str):
                json_data = json.loads(json_data)

            # Validate the JSON structure with Pydantic
            map_data = _JSONmapData(**json_data)

            rows = map_data.rows
            cols = map_data.cols
            map = [[False] * cols for _ in range(rows)]

            for tile in map_data.tiles:
                map[tile.y][tile.x] = tile.walkable

            return cls(map=map, rows=rows, cols=cols)

        except (ValidationError, ValueError) as e:
            raise ValueError(f"Failed to load map from JSON: {e}")

    @classmethod
    def load_from_txt(cls, txt_data):
        """Parses, validate and loads map data from a TXT file."""
        try:
            lines = txt_data.strip().splitlines()

            # Early validation for empty file
            if not lines:
                raise ValueError("The file is empty.")

            # Validate the TXT structure with Pydantic
            txt_map_data = _TXTmapData(rows=len(lines), cols=len(lines[0]), grid=lines)

            rows = txt_map_data.rows
            cols = txt_map_data.cols

            map = [[char == 'o' for char in row] for row in txt_map_data.grid]

            return cls(map=map, rows=rows, cols=cols)

        except (ValidationError, ValueError) as e:
            raise ValueError(f"Failed to load map from TXT: {e}")

    def is_walkable(self, x: int, y: int) -> bool:
        """Checks if a given tile is walkable."""
        if self.map is None or self.rows is None or self.cols is None:
            raise ValueError("Map is not initialized.")

        if not (0 <= x < self.cols and 0 <= y < self.rows):
            raise ValueError("Coordinates out of bounds.")

        return self.map[y][x]
