from pydantic import BaseModel, Field, ValidationError
from typing import List, Literal
import json


class _Action(BaseModel):
    """
    Represents a single action taken by the robot, including the direction and number of steps.
    """
    direction: Literal["north", "east", "south", "west"]
    steps: int = Field(..., ge=0, description="Number of steps must be greater than zero")


class RobotPath(BaseModel):
    """
    Represents the robot's path, starting from coordinates (x, y) and a list of actions to follow.
    """
    x: int = Field(..., ge=0, description="X coordinate must be greater than zero", frozen=True)
    y: int = Field(..., ge=0, description="Y coordinate must be greater than zero", frozen=True)
    actions: List[_Action] = Field(..., description="List of actions to follow", frozen=True)

    @classmethod
    def load_from_json(cls, data):
        """
        Loads the robot's path from a JSON file, validating the format and data.
        Args: A file-like object containing the JSON data.
        """
        try:
            if isinstance(data, str):
                data = json.loads(data)
            return cls(**data)
        except (json.JSONDecodeError, ValidationError, KeyError) as e:
            raise ValueError(f"Failed to load actions from JSON: {e}")

    @classmethod
    def load_from_txt(cls, file):
        """
        Loads the robot's path from a TXT file, parsing the coordinates and actions.
        Args: A file-like object containing the TXT data.
        """
        try:
            lines = file.splitlines()
            print(lines)
            # Parse starting position (first line contains x, y)
            x, y = map(int, lines[0].strip().split())
            actions = []

            # Parse action lines
            for line in lines[1:]:
                direction, steps = line.strip().split()
                actions.append(_Action(direction=direction.lower(), steps=int(steps)))

            return cls(x=x, y=y, actions=actions)
        except (ValueError, IndexError, ValidationError) as e:
            raise ValueError(f"Failed to load actions from JSON: {e}")
