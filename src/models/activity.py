"""Activity type definitions and parsing."""

from enum import Enum
from dataclasses import dataclass
from typing import Optional


class ActivityType(Enum):
    """Activity type categories."""
    REST = ('R', 'Rest')
    PROCRASTINATION = ('P', 'Procrastination')
    GUILT_FREE_PLAY = ('G', 'Guilt-free Play')
    MANDATORY_WORK = ('M', 'Mandatory Work')
    PRODUCTIVE_WORK = ('W', 'Productive Work')

    def __init__(self, code: str, label: str):
        self.code = code
        self.label = label

    @classmethod
    def from_code(cls, code: str) -> Optional['ActivityType']:
        """Get ActivityType from code letter."""
        code = code.upper()
        for activity_type in cls:
            if activity_type.code == code:
                return activity_type
        return None

    @classmethod
    def get_all_labels(cls) -> dict:
        """Get mapping of codes to labels."""
        return {at.code: at.label for at in cls}


@dataclass
class Activity:
    """Represents a single time tracking activity."""
    time_slot: str
    day: str
    activity_type: ActivityType
    description: str
    month: int
    week: int
    year: int

    @property
    def type_label(self) -> str:
        """Get the activity type label."""
        return self.activity_type.label

    @property
    def type_code(self) -> str:
        """Get the activity type code."""
        return self.activity_type.code

    @classmethod
    def parse_from_string(cls, activity_str: str, time_slot: str, day: str,
                         month: int, week: int, year: int) -> Optional['Activity']:
        """Parse an activity from a string like 'R: Rise&Shine'."""
        if not activity_str or not isinstance(activity_str, str):
            return None

        activity_str = activity_str.strip()
        if not activity_str:
            return None

        # Parse activity type code
        type_code = activity_str[0].upper() if activity_str else ''
        activity_type = ActivityType.from_code(type_code)

        if not activity_type:
            return None

        # Parse description (everything after 'X: ')
        description = activity_str[2:].strip() if len(activity_str) > 2 else ''

        return cls(
            time_slot=time_slot,
            day=day,
            activity_type=activity_type,
            description=description,
            month=month,
            week=week,
            year=year
        )

    def __str__(self) -> str:
        return f"{self.type_code}: {self.description}" if self.description else self.type_code
