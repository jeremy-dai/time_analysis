"""Tests for analyzer module."""

import pytest
from pathlib import Path

from time_analysis.analyzer import TimeAnalyzer


def test_analyzer_init():
    """Test TimeAnalyzer initialization."""
    analyzer = TimeAnalyzer(__file__, year=2024)
    assert analyzer.year == 2024
    assert analyzer.data_path is not None


def test_load_single_file(sample_csv_file):
    """Test loading data from single file."""
    analyzer = TimeAnalyzer(str(sample_csv_file))
    analyzer.load_data()

    assert analyzer.raw_data is not None
    assert not analyzer.raw_data.empty


def test_load_directory(sample_csv_directory):
    """Test loading data from directory."""
    analyzer = TimeAnalyzer(str(sample_csv_directory))
    analyzer.load_data()

    assert analyzer.raw_data is not None
    assert not analyzer.raw_data.empty


def test_process_data(sample_csv_file):
    """Test data processing."""
    analyzer = TimeAnalyzer(str(sample_csv_file))
    analyzer.load_data()
    analyzer.process_data()

    assert analyzer.processed_data is not None
    assert not analyzer.processed_data.empty


def test_generate_report(sample_csv_file):
    """Test report generation."""
    analyzer = TimeAnalyzer(str(sample_csv_file))
    analyzer.load_data()
    analyzer.process_data()

    report = analyzer.generate_report()

    assert isinstance(report, str)
    assert "Time Analysis Report" in report
    assert "Total Hours per Activity Type" in report


def test_method_chaining(sample_csv_file):
    """Test method chaining functionality."""
    analyzer = TimeAnalyzer(str(sample_csv_file))
    result = analyzer.load_data().process_data()

    assert result is analyzer
    assert analyzer.processed_data is not None


def test_full_analysis(sample_csv_file, tmp_path):
    """Test running full analysis."""
    analyzer = TimeAnalyzer(str(sample_csv_file))
    output_dir = str(tmp_path / "output")

    report = analyzer.run_full_analysis(output_dir)

    assert isinstance(report, str)
    assert Path(output_dir).exists()
    assert (Path(output_dir) / "report.txt").exists()
