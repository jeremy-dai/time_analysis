"""Time period models for analyzing specific weeks, months, or years."""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime, timedelta
import calendar


@dataclass
class TimePeriod:
    """Base class for time periods."""
    year: int

    def matches(self, activity_year: int, activity_month: int, activity_week: int) -> bool:
        """Check if an activity matches this time period."""
        raise NotImplementedError


@dataclass
class Week(TimePeriod):
    """Represents a specific week in a specific month and year."""
    month: int
    week: int

    def matches(self, activity_year: int, activity_month: int, activity_week: int) -> bool:
        """Check if activity is in this specific week."""
        return (self.year == activity_year and
                self.month == activity_month and
                self.week == activity_week)

    def __str__(self) -> str:
        return f"{self.year}-M{self.month}W{self.week}"

    @property
    def label(self) -> str:
        """Human-readable label."""
        month_name = calendar.month_name[self.month] if 1 <= self.month <= 12 else f"Month{self.month}"
        return f"{month_name} {self.year}, Week {self.week}"


@dataclass
class Month(TimePeriod):
    """Represents a specific month in a year."""
    month: int

    def matches(self, activity_year: int, activity_month: int, activity_week: int) -> bool:
        """Check if activity is in this specific month."""
        return self.year == activity_year and self.month == activity_month

    def __str__(self) -> str:
        return f"{self.year}-M{self.month}"

    @property
    def label(self) -> str:
        """Human-readable label."""
        month_name = calendar.month_name[self.month] if 1 <= self.month <= 12 else f"Month{self.month}"
        return f"{month_name} {self.year}"


@dataclass
class Year(TimePeriod):
    """Represents a specific year."""

    def matches(self, activity_year: int, activity_month: int, activity_week: int) -> bool:
        """Check if activity is in this specific year."""
        return self.year == activity_year

    def __str__(self) -> str:
        return f"{self.year}"

    @property
    def label(self) -> str:
        """Human-readable label."""
        return f"Year {self.year}"
