import json


class Map:
    def __init__(self):
        self._map = None
        self._rows = None
        self._cols = None

    def get_map(self):
        return self._map

    def rows_num(self):
        return self._rows

    def cols_num(self):
        return self._cols

    def reset(self):
        self._map = None
        self._rows = None
        self._cols = None

    def load_from_txt(self, txt_data):
        try:
            # Strip leading/trailing whitespace and split data into lines
            lines = txt_data.strip().splitlines()

            # Check if all rows are of the same length
            if len(set(len(line) for line in lines)) != 1:
                raise ValueError("All rows must be the same length.")

            # Initialize map and set rows and columns based on the first line
            self._map = []
            self._rows = len(lines)
            self._cols = len(lines[0])

            # Check for invalid characters and convert the map into boolean values
            for line in lines:
                # Ensure the line only contains 'x' or 'o' characters, else raise error
                if not all(c in ['x', 'o'] for c in line):
                    raise ValueError("Invalid character in TXT data. Only 'x' and 'o' are allowed.")
                # Convert each row into boolean values: 'x' -> False, 'o' -> True
                row = [False if char == 'x' else True for char in line]
                self._map.append(row)

        except ValueError as e:
            # In case of any ValueError, set map, rows, and cols to None
            self.reset()
            # Propagate the error
            raise ValueError(f"Failed to load map from TXT file: {e}")

    def load_from_json(self, json_data):
        try:
            if isinstance(json_data, str):
                json_data = json.loads(json_data)

            if not all(k in json_data for k in ("rows", "cols", "tiles")):
                raise ValueError("Missing required keys: 'rows', 'cols', or 'tiles'.")

            self._rows = json_data.get("rows")
            self._cols = json_data.get("cols")
            self._map = [[False] * self._cols for _ in range(self._rows)]

            # Ensure the number of tiles matches rows × cols
            if len(json_data.get("tiles")) != self._rows * self._cols:
                raise ValueError("Mismatch between rows/cols and tile count: Expected exactly rows × cols tiles.")

            # Create expected coordinate set
            expected_coords = {(x, y) for y in range(self._rows) for x in range(self._cols)}
            actual_coords = set()

            for tile in json_data.get("tiles"):
                x, y, walkable = tile.get("x"), tile.get("y"), tile.get("walkable")
                if not isinstance(x, int) or not isinstance(y, int) or not isinstance(walkable, bool):
                    raise ValueError("Invalid tile synthetic_data")
                if x < 0 or x >= self._cols or y < 0 or y >= self._rows:
                    raise ValueError("Tile coordinates out of bounds")
                self._map[y][x] = walkable
                actual_coords.add((x, y))

            # Ensure every expected cell coordinate is present in tiles
            if actual_coords != expected_coords:
                raise ValueError("Tile list does not contain exactly one entry for each grid cell.")

        except Exception as e:
            # In case of any ValueError, set map, rows, and cols to None
            self.reset()
            # Propagate the error
            raise ValueError(f"Failed to load map from JSON file: {e}")

    def is_walkable(self, x, y):
        if self._map is None or self._rows is None or self._cols is None:
            raise ValueError("Map, rows, or cols are not initialized")

        if not (0 <= x < self._cols and 0 <= y < self._rows):
            raise ValueError("Coordinates out of bounds")
        return self._map[y][x]
