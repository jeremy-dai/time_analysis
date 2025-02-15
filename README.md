# Time Analysis

A Python-based tool for analyzing and visualizing time tracking data from Excel spreadsheets. This tool helps you understand how you spend your time by categorizing activities and generating insightful visualizations.

## Features

- Load and process time tracking data from Excel files
- Categorize activities into different types:
  - Rest (R)
  - Procrastination (P)
  - Guilt-free Play (G)
  - Mandatory Work (M)
  - Productive Work (W)
- Generate visualizations using Plotly
- Support for weekly and monthly data analysis

## Requirements

- Python 3.x
- pandas
- plotly
- openpyxl
- numpy

## Usage

```bash
python time_analysis.py [excel_file_path] [--year YEAR]
```

### Excel File Format

- Each sheet should be named in the format `month.week` (e.g., `1.1` for January Week 1)
- Activities should be marked with the corresponding category letter (R, P, G, M, W)

## Output

The tool generates interactive Plotly visualizations to help you understand your time usage patterns and productivity trends.
