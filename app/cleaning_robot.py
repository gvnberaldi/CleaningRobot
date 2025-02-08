import csv
import io
import json
from typing import List, Dict
from datetime import datetime
from pydantic import Field, BaseModel
from abc import ABC, abstractmethod
from app.database import Database, CleaningSession
from app.map import Map
from app.robot_path import RobotPath


class CleaningRobot(ABC):
    """
    Abstract class tha define the interface of the cleaning robot.
    """
    map: Map = Field(..., description="The map the robot will move on.")
    path: RobotPath = Field(..., description="The robot's starting position and movement actions.")
    database_conn: Database = Field(..., description="Connection to the database for storing "
                                                     "and retrieve cleaning sessions.")
    cleaned_tiles: List[tuple] = Field(default_factory=list, description="List of cleaned tiles.")

    def __init__(self, map: Map, path: RobotPath, database_conn: Database):
        self.map = map
        self.path = path
        self.database_conn = database_conn
        self.cleaned_tiles = []

    def set_map(self, map: Map):
        """
        Sets the map the robot will move on.
        """
        self.map = map

    def set_path(self, path: RobotPath):
        """
        Sets the robot's starting position and movement actions.
        """
        self.path = path

    def _store_session(self, report: Dict[str, any], start_time: datetime, performed_actions: int):
        """Stores the cleaning session in the database."""
        end_time = datetime.now()
        duration = end_time - start_time

        session = CleaningSession(
            session_start_time=start_time,
            session_final_state=report["status"],
            number_of_actions=performed_actions,
            number_of_cleaned_tiles=len(self.cleaned_tiles),
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


class BaseCleaningRobot(BaseModel, CleaningRobot):
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

            self.cleaned_tiles.append((x, y))  # Mark starting position as cleaned
            for action in self.path.actions:
                for _ in range(action.steps):
                    if action.direction == "north":
                        y -= 1
                    elif action.direction == "south":
                        y += 1
                    elif action.direction == "west":
                        x -= 1
                    elif action.direction == "east":
                        x += 1
                    if not (0 <= x < self.map.cols and 0 <= y < self.map.rows):
                        raise ValueError(f"Robot moved out of map bounds at ({x}, {y}).")
                    if not self.map.is_walkable(x, y):
                        raise ValueError(f"Robot attempted to move to a non-walkable tile at ({x}, {y}).")

                    self.cleaned_tiles.append((x, y))
                    performed_actions += 1

        except ValueError as e:
            error_message = str(e)
            report = {"cleaned_tiles": self.cleaned_tiles, "status": "error", "error": error_message}
            self._store_session(report, start_time, performed_actions)
            return json.dumps(report, indent=4)

        report = {"cleaned_tiles": self.cleaned_tiles, "status": "completed", "error": None}
        self._store_session(report, start_time, performed_actions)
        return json.dumps(report, indent=4)
