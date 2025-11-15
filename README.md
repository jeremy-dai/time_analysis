# Time Analysis Tool

A comprehensive Python application for analyzing personal time tracking data with support for week/month/year analysis, visualizations, and AI-ready markdown reports.

## 🚀 Features

- **Flexible Data Loading**: Support for both CSV and Excel files
- **Period-Based Analysis**: Analyze specific weeks, months, or entire years
- **Rich Visualizations**: Interactive charts with HTML and image export
- **AI-Ready Reports**: Detailed markdown reports optimized for LLM analysis
- **Modular Architecture**: Clean, maintainable code structure
- **Comparison Tools**: Compare multiple time periods side-by-side

## 📁 Project Structure

```
time_analysis/
├── src/
│   ├── models/           # Data models (Activity, TimePeriod, etc.)
│   ├── data/             # Data loading and processing
│   ├── analysis/         # Core analysis logic
│   ├── visualization/    # Chart generation and export
│   ├── reports/          # Markdown report generation
│   └── cli.py            # Command-line interface
├── example data/         # Sample data files
├── analyze.py            # Main entry point
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## 📊 Data Format

### CSV Format

CSV files should follow this naming convention:
```
YYYY Time-M.W.csv
```

Example: `2023 Time-1.1.csv` (Year 2023, Month 1, Week 1)

**File Structure:**
- Row 1: Header (optional text)
- Row 2: Column headers (Time, Day1, Day2, ..., Day7)
- Rows 3+: Time slots (08:00-23:30) with activities

**Activity Format:**
```
CODE: Description
```

Where CODE is one of:
- `R`: Rest
- `P`: Procrastination
- `G`: Guilt-free Play
- `M`: Mandatory Work
- `W`: Productive Work

Example activities:
- `R: Sleep`
- `W: Project work`
- `G: Gaming`

### Excel Format

Excel files can contain multiple sheets, where each sheet name is `M.W` (Month.Week).

## 🛠️ Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd time_analysis
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

**Dependencies:**
- pandas >= 2.0.0
- plotly >= 5.14.0
- numpy >= 1.24.0
- openpyxl >= 3.1.0
- kaleido >= 0.2.1 (optional, for image export)

## 📖 Usage

### Basic Commands

The tool provides three main commands: `analyze`, `compare`, and `summary`.

### 1. Analyze Command

Analyze a specific time period or all available data.

**Analyze a specific week:**
```bash
python analyze.py analyze "example data/" --week 2023 1 1 --output reports/
```

**Analyze a specific month:**
```bash
python analyze.py analyze "example data/" --month 2023 1 --output reports/
```

**Analyze an entire year:**
```bash
python analyze.py analyze "example data/" --year 2023 --output reports/
```

**Analyze all data:**
```bash
python analyze.py analyze "example data/" --output reports/
```

**Options:**
- `--output, -o`: Output directory (default: `output/`)
- `--no-images`: Skip image generation (only HTML)
- `--no-html`: Skip HTML generation
- `--no-markdown`: Skip markdown report generation

### 2. Compare Command

Compare multiple time periods side-by-side.

**Compare weeks:**
```bash
python analyze.py compare "example data/" --weeks "2023-1-1,2023-1-2,2023-1-3" --output reports/
```

**Compare months:**
```bash
python analyze.py compare "example data/" --months "2023-1,2023-2,2023-3" --output reports/
```

**Compare years:**
```bash
python analyze.py compare "example data/" --years "2023,2024" --output reports/
```

### 3. Summary Command

Generate an overall summary of all tracked time.

```bash
python analyze.py summary "example data/" --output reports/
```

## 📄 Output Files

The tool generates several types of output files:

### Visualizations

1. **Distribution Chart**: Stacked bar showing activity type distribution
2. **Daily Breakdown**: Activities broken down by day of week
3. **Pie Chart**: Overall time allocation
4. **Top Activities**: Horizontal bar chart of most common activities
5. **Heatmap**: Activity patterns by time and day

Formats:
- `.html`: Interactive Plotly charts
- `.png`: Static images (requires kaleido)

### Reports

**Markdown Reports** (`.md`):
- Executive summary with key metrics
- Activity type distribution table
- Daily breakdown by day of week
- Top 10 specific activities
- Time slot patterns
- Insights section with JSON data for LLM analysis
- Suggested analysis questions

**JSON Data** (`.json`):
- Raw analysis data for programmatic use
- All statistics and breakdowns in structured format

### Example Output Structure

```
output/
├── week_2023_1_1_report.md
├── week_2023_1_1_data.json
├── week_2023_1_1_distribution.html
├── week_2023_1_1_daily.html
├── week_2023_1_1_pie.html
├── week_2023_1_1_top_activities.html
├── week_2023_1_1_heatmap.html
└── ...
```

## 🤖 AI Life Coach Integration

The markdown reports are specifically designed for AI analysis. They include:

1. **Structured Data**: JSON-formatted data for easy parsing
2. **Context Section**: All relevant metrics and distributions
3. **Guided Questions**: Prompts for meaningful analysis:
   - Work-Life Balance assessment
   - Productivity pattern identification
   - Improvement area suggestions
   - Positive habit recognition
   - Actionable recommendations

### Using with LLMs

Simply provide the generated markdown report to your preferred LLM with a prompt like:

```
Based on the time tracking data in this report, please:
1. Analyze my work-life balance
2. Identify productivity patterns
3. Suggest areas for improvement
4. Provide specific, actionable recommendations
```

## 🏗️ Architecture

### Models (`src/models/`)

- **ActivityType**: Enum for activity categories (R, P, G, M, W)
- **Activity**: Data class representing a single time block
- **TimePeriod**: Base class for time periods (Week, Month, Year)

### Data Layer (`src/data/`)

- **DataLoader**: Load CSV and Excel files
- **DataProcessor**: Process raw data into structured activities

### Analysis (`src/analysis/`)

- **TimeAnalyzer**: Core analysis engine for periods
- **StatisticsCalculator**: Calculate trends, patterns, and metrics

### Visualization (`src/visualization/`)

- **ChartGenerator**: Create Plotly charts
- **VisualizationExporter**: Export to HTML, PNG, SVG, PDF

### Reports (`src/reports/`)

- **MarkdownReportGenerator**: Generate detailed markdown reports

## 🔧 Advanced Usage

### Python API

You can also use the components directly in Python:

```python
from src.data.loader import DataLoader
from src.data.processor import DataProcessor
from src.models.time_period import Week
from src.analysis.analyzer import TimeAnalyzer

# Load data
loader = DataLoader("example data/")
raw_data = loader.load()

# Process data
processor = DataProcessor(raw_data)
processor.process()

# Analyze a specific week
analyzer = TimeAnalyzer(processor)
week = Week(year=2023, month=1, week=1)
analysis = analyzer.analyze_period(week)

print(analysis)
```

### Custom Analysis

```python
from src.analysis.statistics import StatisticsCalculator

# Calculate statistics
stats = StatisticsCalculator(processor.get_dataframe())

# Get daily patterns
daily_patterns = stats.calculate_daily_patterns()

# Find productive times
productive_times = stats.get_most_productive_times()

# Calculate balance score
balance = stats.calculate_balance_score()
```

## 📈 Example Workflow

1. **Track time** in your preferred format (CSV or Excel)
2. **Run weekly analysis** to review the past week:
   ```bash
   python analyze.py analyze data/ --week 2024 1 1 -o reports/week1/
   ```
3. **Generate markdown report** for LLM analysis
4. **Get AI insights** by sharing the report with your AI life coach
5. **Compare periods** to track progress:
   ```bash
   python analyze.py compare data/ --weeks "2024-1-1,2024-1-2,2024-1-3"
   ```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues.

## 📝 License

This project is open source and available under the MIT License.

## 🎯 Future Enhancements

Potential features for future development:

- [ ] Web dashboard interface
- [ ] Automatic goal tracking and progress
- [ ] Integration with calendar apps
- [ ] Custom activity categories
- [ ] Weekly/monthly email reports
- [ ] Mobile app for time tracking input
- [ ] Advanced ML-based insights
- [ ] Habit formation tracking
- [ ] Correlation analysis (mood, productivity, etc.)

## 💡 Tips

1. **Be consistent** with time tracking for better insights
2. **Use descriptive names** for activities to get meaningful top activities
3. **Review weekly** to catch patterns early
4. **Compare periods** to track long-term trends
5. **Share reports with AI** for personalized coaching
6. **Set goals** based on the balance score suggestions

## 🙏 Acknowledgments

This tool is designed to help you understand and optimize how you spend your time, enabling data-driven decisions for better work-life balance and personal growth.

---

**Happy Time Tracking! 📊✨**
