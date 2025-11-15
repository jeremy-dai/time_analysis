# Time Analysis Tool

A simple Python script to analyze and visualize your time tracking data from Excel files.

## What it does

- Reads time tracking data from Excel files (one sheet per week)
- Categorizes activities into 5 types: Rest (R), Procrastination (P), Guilt-free Play (G), Mandatory Work (M), Productive Work (W)
- Generates interactive visualizations showing how you spend your time
- Produces detailed statistics and reports

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python time_analysis.py your_data.xlsx --year 2024
```

This will create a `time_analysis_output/` directory with:
- Interactive HTML charts (monthly, weekly, daily distributions)
- Detailed statistics in CSV format
- A text report summarizing your time usage

## Data Format

Your Excel file should have sheets named `M.W` (e.g., `1.1` for Month 1, Week 1).

Each sheet should have:
- Column A: Time (06:00, 06:30, 07:00, etc.)
- Columns B-H: Days of the week (Sunday through Saturday)

Each cell should contain an activity in format: `X: Description`
- `R: Sleep` (Rest)
- `P: Social media` (Procrastination)
- `G: Gaming` (Guilt-free Play)
- `M: Email` (Mandatory Work)
- `W: Coding` (Productive Work)

## Requirements

- Python 3.8+
- pandas
- plotly
- numpy
- openpyxl

## License

MIT
