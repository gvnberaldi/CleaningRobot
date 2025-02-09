import csv
import io
import json
from typing import List, Dict, Optional
from datetime import datetime
from pydantic import Field, BaseModel
from abc import ABC, abstractmethod
from app.database import Database, CleaningSession
from app.map import Map
from app.robot_path import RobotPath


class CleaningRobot(BaseModel, ABC):
    """
    Abstract class tha define the interface of the cleaning robot.
    """
    _map: Optional[Map] = None
    _path: Optional[RobotPath] = None
    _database_conn: Optional[Database] = None
    _cleaned_tiles: List[tuple] = []

    def __init__(self, map: Optional[Map] = None, path: Optional[RobotPath] = None,
                 database_conn: Optional[Database] = None):
        super().__init__(map=map, path=path, database_conn=database_conn)
        if map is not None:
            self.map = map
        if path is not None:
            self.path = path
        if database_conn is not None:
            self.database_conn = database_conn

    @property
    def map(self) -> Optional[Map]:
        return self._map

    @map.setter
    def map(self, map: Map):
        if not isinstance(map, Map):
            raise ValueError('The map must be of type Map.')
        self._map = map

    @property
    def path(self) -> Optional[RobotPath]:
        return self._path

    @path.setter
    def path(self, path: RobotPath):
        if not isinstance(path, RobotPath):
            raise ValueError('The path must be of type RobotPath.')
        self._path = path

    @property
    def database_conn(self) -> Optional[Database]:
        return self._database_conn

    @database_conn.setter
    def database_conn(self, database_conn: Database):
        if not isinstance(database_conn, Database):
            raise ValueError('The database_conn must be of type Database.')
        self._database_conn = database_conn

    def move(self, x, y, action):
        """Moves the robot according to the given action and returns the new coordinates.
        Raises exceptions if the move is out of bounds or if the tile is not walkable."""
        # Move the robot based on the action direction
        if action.direction == "north":
            y -= 1
        elif action.direction == "south":
            y += 1
        elif action.direction == "west":
            x -= 1
        elif action.direction == "east":
            x += 1

        # Check if the new position is within bounds
        if not (0 <= x < self.map.cols and 0 <= y < self.map.rows):
            raise ValueError(f"Robot moved out of map bounds at ({x}, {y}).")

        # Check if the new position is walkable
        if not self.map.is_walkable(x, y):
            raise ValueError(f"Robot attempted to move to a non-walkable tile at ({x}, {y}).")

        return x, y

    def _store_session(self, report: Dict[str, any], start_time: datetime, performed_actions: int):
        """Stores the cleaning session in the database."""
        end_time = datetime.now()
        duration = end_time - start_time

        session = CleaningSession(
            session_start_time=start_time,
            session_final_state=report["status"],
            number_of_actions=performed_actions,
            number_of_cleaned_tiles=len(self._cleaned_tiles),
            duration=duration
        )
        self.database_conn.create_table()
        self.database_conn.save_session(session)

    @abstractmethod
    def clean(self):
        """
        Executes the cleaning session by following the defined path, generates a cleaning report in JSON format,
        and stores the session in the database.
        """
        pass


class BaseCleaningRobot(CleaningRobot):
    """
    Concrete class that implements the base cleaning robot interface.
    """

    def clean(self):
        """Executes the cleaning session by following the defined path, generates a cleaning report in JSON format,
        and stores the session in the database."""
        start_time = datetime.now()
        x, y = self.path.x, self.path.y
        performed_actions = 0
        try:
            # Check if the starting position is valid
            if not (0 <= x < self.map.cols and 0 <= y < self.map.rows) or not self.map.is_walkable(x, y):
                raise ValueError(f"Invalid starting position ({x}, {y}).")

            self._cleaned_tiles.append((x, y))  # Mark starting position as cleaned
            for action in self.path.actions:
                for _ in range(action.steps):
                    # Update the robot's position
                    x, y = self.move(x, y, action)
                    self._cleaned_tiles.append((x, y))
                    performed_actions += 1

        except ValueError as e:
            error_message = str(e)
            report = {"cleaned_tiles": self._cleaned_tiles, "status": "error", "error": error_message}
            self._store_session(report, start_time, performed_actions)
            self._cleaned_tiles = []
            return json.dumps(report, indent=4)

        report = {"cleaned_tiles": self._cleaned_tiles, "status": "completed", "error": None}
        self._store_session(report, start_time, performed_actions)
        self._cleaned_tiles = []
        return json.dumps(report, indent=4)


class PremiumCleaningRobot(CleaningRobot):
    """
    Concrete class that implements the premium cleaning robot interface.
    """

    def clean(self):
        """Executes the cleaning session by following the defined path, generates a cleaning report in JSON format,
        and stores the session in the database. Do not clean the tile cleaned in the previous session."""
        start_time = datetime.now()
        x, y = self.path.x, self.path.y
        performed_actions = 0

        # Make a copy of the cleaned tiles from the previous session to avoid cleaning them again
        previous_cleaned_tiles = set(self._cleaned_tiles)
        # Clear the current session cleaned tiles list
        self._cleaned_tiles = []

        try:
            # Check if the starting position is valid
            if not (0 <= x < self.map.cols and 0 <= y < self.map.rows) or not self.map.is_walkable(x, y):
                raise ValueError(f"Invalid starting position ({x}, {y}).")

            # Mark starting position as cleaned if it hasn't been cleaned in the previous session
            if (x, y) not in previous_cleaned_tiles:
                self._cleaned_tiles.append((x, y))

            for action in self.path.actions:
                for _ in range(action.steps):
                    # Update the robot's position
                    x, y = self.move(x, y, action)

                    # Only clean the tile if it hasn't been cleaned in the previous session
                    if (x, y) not in previous_cleaned_tiles and (x, y) not in self._cleaned_tiles:
                        self._cleaned_tiles.append((x, y))

                    performed_actions += 1

        except ValueError as e:
            error_message = str(e)
            report = {"cleaned_tiles": self._cleaned_tiles, "status": "error", "error": error_message}
            self._store_session(report, start_time, performed_actions)
            return json.dumps(report, indent=4)

        report = {"cleaned_tiles": self._cleaned_tiles, "status": "completed", "error": None}
        self._store_session(report, start_time, performed_actions)
        return json.dumps(report, indent=4)

    def reset_cleaned_tiles(self):
        self._cleaned_tiles = []
