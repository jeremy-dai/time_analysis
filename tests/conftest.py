"""Pytest configuration and shared fixtures."""

import pandas as pd
import pytest
from pathlib import Path


@pytest.fixture
def sample_raw_data():
    """Create sample raw data for testing."""
    data = {
        "Month": [1, 1, 1, 1, 1, 1],
        "Week": [1, 1, 1, 1, 1, 1],
        "Day": ["Monday", "Monday", "Tuesday", "Tuesday", "Wednesday", "Wednesday"],
        "Time": ["08:00", "08:30", "09:00", "09:30", "10:00", "10:30"],
        "Activity": ["W: Coding", "W: Meeting", "R: Sleep", "P: Social Media", "G: Gaming", "M: Email"],
    }
    return pd.DataFrame(data)


@pytest.fixture
def sample_processed_data():
    """Create sample processed data for testing."""
    data = {
        "Month": [1, 1, 1, 1, 1, 1],
        "Week": [1, 1, 1, 1, 1, 1],
        "Day": ["Monday", "Monday", "Tuesday", "Tuesday", "Wednesday", "Wednesday"],
        "Time": ["08:00", "08:30", "09:00", "09:30", "10:00", "10:30"],
        "Activity_Type": [
            "Productive Work",
            "Productive Work",
            "Rest",
            "Procrastination",
            "Guilt-free Play",
            "Mandatory Work",
        ],
        "Activity_Detail": ["Coding", "Meeting", "Sleep", "Social Media", "Gaming", "Email"],
    }
    return pd.DataFrame(data)


@pytest.fixture
def sample_csv_file(tmp_path):
    """Create a sample CSV file for testing."""
    csv_content = """Time,Sunday,Monday,Tuesday,Wednesday,Thursday,Friday,Saturday
08:00,R: Sleep,W: Coding,W: Coding,W: Coding,W: Coding,W: Coding,R: Sleep
08:30,R: Sleep,W: Meeting,W: Coding,W: Meeting,W: Coding,W: Meeting,R: Sleep
09:00,R: Sleep,M: Email,W: Coding,M: Email,W: Coding,M: Email,G: Gaming
09:30,G: Gaming,P: Social Media,W: Coding,W: Coding,P: Break,W: Coding,G: Gaming
"""
    csv_file = tmp_path / "2024_01_01.csv"
    csv_file.write_text(csv_content)
    return csv_file


@pytest.fixture
def sample_csv_directory(tmp_path):
    """Create a directory with multiple sample CSV files."""
    csv_dir = tmp_path / "csv_data"
    csv_dir.mkdir()

    csv_content = """Time,Sunday,Monday,Tuesday,Wednesday,Thursday,Friday,Saturday
08:00,R: Sleep,W: Coding,W: Coding,W: Coding,W: Coding,W: Coding,R: Sleep
08:30,R: Sleep,W: Meeting,W: Coding,W: Meeting,W: Coding,W: Meeting,R: Sleep
"""

    # Create multiple CSV files
    for month in [1, 2]:
        for week in [1, 2]:
            csv_file = csv_dir / f"2024_{month:02d}_{week:02d}.csv"
            csv_file.write_text(csv_content)

    return csv_dir
