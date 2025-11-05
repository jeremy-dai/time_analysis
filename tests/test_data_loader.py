"""Tests for data_loader module."""

import pytest
import pandas as pd
from pathlib import Path

from time_analysis.data_loader import DataLoader


def test_data_loader_init_valid_file(sample_csv_file):
    """Test DataLoader initialization with valid file."""
    loader = DataLoader(str(sample_csv_file))
    assert loader.file_path.exists()


def test_data_loader_init_invalid_file():
    """Test DataLoader initialization with invalid file."""
    with pytest.raises(FileNotFoundError):
        DataLoader("nonexistent_file.csv")


def test_parse_filename_valid():
    """Test parsing valid filenames."""
    loader = DataLoader(__file__)  # Use this file as dummy

    year, month, week = loader._parse_filename("2024_01_01")
    assert year == 2024
    assert month == 1
    assert week == 1

    year, month, week = loader._parse_filename("2023-12-05")
    assert year == 2023
    assert month == 12
    assert week == 5


def test_parse_filename_invalid():
    """Test parsing invalid filenames."""
    loader = DataLoader(__file__)

    with pytest.raises(ValueError):
        loader._parse_filename("invalid")

    with pytest.raises(ValueError):
        loader._parse_filename("2024_13_01")  # Invalid month

    with pytest.raises(ValueError):
        loader._parse_filename("2024_01_06")  # Invalid week


def test_load_csv_files(sample_csv_directory):
    """Test loading multiple CSV files from directory."""
    loader = DataLoader(str(sample_csv_directory / "dummy.csv"))
    df = loader.load_csv_files(str(sample_csv_directory))

    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "Month" in df.columns
    assert "Week" in df.columns
    assert "Day" in df.columns
    assert "Activity" in df.columns


def test_load_csv_files_nonexistent_directory():
    """Test loading from nonexistent directory."""
    loader = DataLoader(__file__)

    with pytest.raises(FileNotFoundError):
        loader.load_csv_files("/nonexistent/directory")


def test_load_single_csv(sample_csv_file):
    """Test loading a single CSV file."""
    loader = DataLoader(str(sample_csv_file))
    df = loader.load()

    assert isinstance(df, pd.DataFrame)
    assert not df.empty
    assert "Day" in df.columns
    assert "Activity" in df.columns


def test_standardize_columns(sample_csv_file):
    """Test column standardization."""
    loader = DataLoader(str(sample_csv_file))
    df = pd.read_csv(sample_csv_file)

    standardized = loader._standardize_columns(df)

    expected_columns = ["Time", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    assert list(standardized.columns) == expected_columns
