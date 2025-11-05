# 34枚金币法每周分析

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive Python-based tool for analyzing and visualizing time tracking data from CSV and Excel files. This tool helps you understand how you spend your time by categorizing activities and generating insightful visualizations and detailed statistics.

## Features

- 📊 **Multiple Data Formats**: Load data from CSV files (one per week) or Excel files with multiple sheets
- 📈 **Rich Visualizations**: Generate interactive Plotly charts including:
  - Monthly time distribution
  - Weekly time distribution
  - Daily time distribution by day of week
  - Overall time distribution (pie chart)
  - Time-of-day heatmaps
  - Productivity trend analysis
- 📉 **Detailed Statistics**: Export comprehensive statistics to CSV and JSON
- 🎯 **Activity Categorization**: Track 5 types of activities:
  - **R**: Rest
  - **P**: Procrastination
  - **G**: Guilt-free Play
  - **M**: Mandatory Work
  - **W**: Productive Work
- 🔧 **Modular Design**: Clean, maintainable code with full type hints
- ✅ **Well-Tested**: Comprehensive test suite with pytest
- 📝 **Detailed Reports**: Generate text and JSON reports of your time usage

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/yourusername/time_analysis.git
cd time_analysis

# Install in development mode
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

### Using pip

```bash
pip install -r requirements.txt
```

## Quick Start

### Command Line Usage

```bash
# Analyze a directory of CSV files
time-analysis data/weekly_csvs/ --year 2024

# Analyze a single Excel file (legacy format)
time-analysis data.xlsx --year 2024 --output results/

# Get help
time-analysis --help
```

### Python API Usage

```python
from time_analysis import TimeAnalyzer

# Initialize analyzer
analyzer = TimeAnalyzer("data/weekly_csvs/", year=2024)

# Run full analysis
report = analyzer.run_full_analysis(output_dir="my_results/")
print(report)

# Or run step by step
analyzer.load_data()
analyzer.process_data()
analyzer.generate_visualizations("output/")
analyzer.save_detailed_stats("output/")
```

## Data Format

### CSV Format (Recommended)

Create one CSV file per week with the following format:

**Filename**: `YYYY_MM_WW.csv` or `YYYY-MM-WW.csv`
- `YYYY`: Year (e.g., 2024)
- `MM`: Month (01-12)
- `WW`: Week number within the month (01-05)

**Example**: `2024_01_01.csv` (January 2024, Week 1)

**CSV Structure**:
```csv
Time,Sunday,Monday,Tuesday,Wednesday,Thursday,Friday,Saturday
06:00,R: Sleep,R: Sleep,R: Sleep,R: Sleep,R: Sleep,R: Sleep,R: Sleep
06:30,R: Sleep,R: Sleep,R: Sleep,R: Sleep,R: Sleep,R: Sleep,R: Sleep
07:00,R: Morning routine,M: Morning routine,M: Morning routine,M: Morning routine,M: Morning routine,M: Morning routine,G: Sleeping in
07:30,M: Breakfast,M: Breakfast,M: Breakfast,M: Breakfast,M: Breakfast,M: Breakfast,G: Breakfast
08:00,G: Reading,W: Coding,W: Coding,W: Coding,W: Coding,W: Coding,G: Hobbies
08:30,G: Gaming,W: Code review,W: Development,W: Meetings,W: Deep work,W: Planning,G: Gaming
...
```

### Excel Format (Legacy)

**Sheet Names**: `M.W` format (e.g., `1.1` for Month 1, Week 1)

**Excel Structure**: Same as CSV (Time column + 7 day columns)

### Activity Format

Each cell should contain an activity in the format: `X: Description`
- `X`: Activity type code (R, P, G, M, or W)
- `: `: Colon and space separator
- `Description`: Brief description of the activity (optional)

**Examples**:
- `W: Coding Python script`
- `R: Sleep`
- `G: Playing video games`
- `M: Email management`
- `P: Social media scrolling`

## Output

The tool generates the following outputs in the specified output directory:

### Visualizations (HTML)
- `monthly_distribution.html` - Stacked bar chart of monthly time usage
- `weekly_distribution.html` - Stacked bar chart of weekly time usage
- `daily_distribution.html` - Time distribution by day of week
- `overall_distribution.html` - Pie chart of overall time distribution
- `time_of_day_heatmap.html` - Heatmap showing activity patterns
- `productivity_trend.html` - Line chart showing productivity over time

### Statistics (CSV/JSON)
- `detailed_stats/daily_activity_summary.csv` - Daily statistics by activity type
- `detailed_stats/specific_activities.csv` - Detailed breakdown of specific activities
- `detailed_stats/time_slot_patterns.csv` - Activity patterns by time of day
- `detailed_stats/summary_statistics.json` - Overall statistics and metrics

### Reports
- `report.txt` - Human-readable text report with key insights

## Requirements

- Python 3.8+
- pandas >= 2.0.0
- plotly >= 5.14.0
- numpy >= 1.24.0
- openpyxl >= 3.1.0 (for Excel support)

## Development

### Setup Development Environment

```bash
# Install with development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=time_analysis --cov-report=html

# Run specific test file
pytest tests/test_analyzer.py
```

### Code Quality

```bash
# Format code with black
black src/ tests/

# Lint with ruff
ruff check src/ tests/

# Type check with mypy
mypy src/
```

## Project Structure

```
time_analysis/
├── src/
│   └── time_analysis/
│       ├── __init__.py          # Package initialization
│       ├── analyzer.py          # Main TimeAnalyzer class
│       ├── cli.py               # Command-line interface
│       ├── constants.py         # Constants and configurations
│       ├── data_loader.py       # Data loading from CSV/Excel
│       ├── processor.py         # Data processing logic
│       ├── stats.py             # Statistics generation
│       └── visualizer.py        # Visualization creation
├── tests/
│   ├── conftest.py              # Pytest fixtures
│   ├── test_analyzer.py         # Analyzer tests
│   ├── test_constants.py        # Constants tests
│   ├── test_data_loader.py      # Data loader tests
│   └── test_processor.py        # Processor tests
├── requirements.txt             # Production dependencies
├── setup.py                     # Package setup
├── pyproject.toml              # Build system and tool configs
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## Troubleshooting

### Common Issues

**Issue**: `FileNotFoundError: File not found`
- **Solution**: Ensure the file path is correct and the file exists

**Issue**: `ValueError: Invalid filename format`
- **Solution**: Check that CSV filenames follow the `YYYY_MM_WW.csv` format

**Issue**: `ValueError: Unexpected number of columns`
- **Solution**: Ensure CSV has exactly 8 columns (Time + 7 days)

**Issue**: `ValueError: Invalid activity types found`
- **Solution**: Check that all activities start with a valid code (R, P, G, M, or W)

## License

This project is licensed under the MIT License.

## Acknowledgments

- Built with [Pandas](https://pandas.pydata.org/) for data processing
- Visualizations powered by [Plotly](https://plotly.com/)
- Inspired by time management and productivity tracking methodologies
