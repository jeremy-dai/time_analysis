"""Tests for constants module."""

from time_analysis.constants import ACTIVITY_TYPES, DAY_ORDER, HOURS_PER_BLOCK


def test_activity_types():
    """Test that all activity types are defined."""
    assert len(ACTIVITY_TYPES) == 5
    assert "R" in ACTIVITY_TYPES
    assert "P" in ACTIVITY_TYPES
    assert "G" in ACTIVITY_TYPES
    assert "M" in ACTIVITY_TYPES
    assert "W" in ACTIVITY_TYPES


def test_activity_type_values():
    """Test that activity type values are correct."""
    assert ACTIVITY_TYPES["R"] == "Rest"
    assert ACTIVITY_TYPES["P"] == "Procrastination"
    assert ACTIVITY_TYPES["G"] == "Guilt-free Play"
    assert ACTIVITY_TYPES["M"] == "Mandatory Work"
    assert ACTIVITY_TYPES["W"] == "Productive Work"


def test_hours_per_block():
    """Test that hours per block is correctly set."""
    assert HOURS_PER_BLOCK == 0.5


def test_day_order():
    """Test that day order is correct."""
    assert len(DAY_ORDER) == 7
    assert DAY_ORDER[0] == "Sunday"
    assert DAY_ORDER[-1] == "Saturday"
