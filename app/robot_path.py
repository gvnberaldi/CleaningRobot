from pydantic import BaseModel, Field, ValidationError
from typing import List, Literal
import json


class RobotPath(BaseModel):
    """
    Represents the robot's path, starting from coordinates (x, y) and a list of actions to follow.
    """
    class Action(BaseModel):
        """
        Represents a single action taken by the robot, including the direction and number of steps.
        """
        direction: Literal["north", "east", "south", "west"] = Field(..., description="Direction of the robot movement.")
        steps: int = Field(..., ge=0, description="Number of steps in a specific direction. Must be greater than or equal to zero")

    x: int = Field(..., ge=0, description="Starting x coordinate of the path. Must be greater than or equal to zero", frozen=True)
    y: int = Field(..., ge=0, description="Starting y coordinate of the path. Must be greater than or equal to zero", frozen=True)
    actions: List[Action] = Field(..., description="Ordered list of actions to follow", frozen=True)

    @classmethod
    def load(cls, file):
        """Parses, validate and loads map data from a TXT or JSON file."""
        if file.filename.endswith('.txt'):
            return cls.__load_from_txt(file)
        elif file.filename.endswith('.json'):
            return cls.__load_from_json(file)
        else:
            raise ValueError(f"Unsupported file format: {file.filename}. Only .txt and .json files are supported.")

    @classmethod
    def __load_from_json(cls, file):
        """
        Loads the robot's path from a JSON file, validating the format and data.
        Args: A file-like object containing the JSON data.
        """
        try:
            data = json.load(file)
            return cls(**data)
        except (json.JSONDecodeError, ValidationError, KeyError) as e:
            raise ValueError(f"Failed to load actions from JSON: {e}")

    @classmethod
    def __load_from_txt(cls, file):
        """
        Loads the robot's path from a TXT file, parsing the coordinates and actions.
        Args: A file-like object containing the TXT data.
        """
        try:
            txt_data = file.read().decode('utf-8')
            lines = txt_data.splitlines()
            # Parse starting position (first line contains x, y)
            x, y = map(int, lines[0].strip().split())
            actions = []

            # Parse action lines
            for line in lines[1:]:
                direction, steps = line.strip().split()
                actions.append(cls.Action(direction=direction.lower(), steps=int(steps)))

            return cls(x=x, y=y, actions=actions)
        except (ValueError, IndexError, ValidationError) as e:
            raise ValueError(f"Failed to load actions from JSON: {e}")
