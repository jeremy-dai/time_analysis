"""Tests for processor module."""

import pytest
import pandas as pd

from time_analysis.processor import DataProcessor
from time_analysis.constants import ACTIVITY_TYPES


def test_processor_init(sample_raw_data):
    """Test DataProcessor initialization."""
    processor = DataProcessor(sample_raw_data)
    assert processor.raw_data is not None
    assert processor.processed_data is None


def test_process_data(sample_raw_data):
    """Test data processing."""
    processor = DataProcessor(sample_raw_data)
    processed = processor.process()

    assert isinstance(processed, pd.DataFrame)
    assert not processed.empty
    assert "Activity_Type" in processed.columns
    assert "Activity_Detail" in processed.columns

    # Check that all activity types are valid
    for activity_type in processed["Activity_Type"].unique():
        assert activity_type in ACTIVITY_TYPES.values()


def test_get_summary_stats(sample_raw_data):
    """Test summary statistics generation."""
    processor = DataProcessor(sample_raw_data)
    processor.process()

    stats = processor.get_summary_stats()

    assert "total_hours" in stats
    assert "daily_hours" in stats
    assert "monthly_averages" in stats
    assert isinstance(stats["total_hours"], dict)


def test_get_daily_stats(sample_raw_data):
    """Test daily statistics."""
    processor = DataProcessor(sample_raw_data)
    processor.process()

    daily_stats = processor.get_daily_stats()

    assert isinstance(daily_stats, pd.DataFrame)
    assert "Hours" in daily_stats.columns
    assert "Blocks" in daily_stats.columns


def test_get_specific_activity_stats(sample_raw_data):
    """Test specific activity statistics."""
    processor = DataProcessor(sample_raw_data)
    processor.process()

    activity_stats = processor.get_specific_activity_stats()

    assert isinstance(activity_stats, pd.DataFrame)
    assert "Activity_Detail" in activity_stats.columns
    assert "Hours" in activity_stats.columns


def test_validate_data_success(sample_raw_data):
    """Test data validation with valid data."""
    processor = DataProcessor(sample_raw_data)
    processor.process()

    assert processor.validate_data() is True


def test_validate_data_no_data():
    """Test validation with no processed data."""
    processor = DataProcessor(pd.DataFrame())

    with pytest.raises(ValueError):
        processor.validate_data()


def test_process_empty_data():
    """Test processing empty data."""
    processor = DataProcessor(pd.DataFrame(columns=["Month", "Week", "Day", "Time", "Activity"]))
    processed = processor.process()

    assert processed.empty
