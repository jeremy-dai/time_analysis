# Time Analysis Tool

A comprehensive Python application for analyzing personal time tracking data with a web-based UI, AI-powered insights, week/month/year analysis, visualizations, and AI-ready markdown reports.

## 🚀 Features

- **Web-based UI**: Simple and intuitive Streamlit interface for interactive analysis
- **File Upload & Management**: Upload and manage your time tracking Excel/CSV files
- **Flexible Data Loading**: Support for both CSV and Excel files
- **Period-Based Analysis**: Analyze specific weeks, months, or entire years
- **Rich Visualizations**: Interactive charts with HTML and image export
- **AI-Powered Insights**: Get personalized recommendations using OpenAI GPT-4 or Anthropic Claude
- **AI-Ready Reports**: Detailed markdown reports optimized for LLM analysis
- **Modular Architecture**: Clean, maintainable code structure
- **Comparison Tools**: Compare multiple time periods side-by-side
- **Command-line Tool**: Also available as a CLI for batch processing

## ⚡ Quick Start

Using the included Makefile (recommended with [uv](https://github.com/astral-sh/uv)):

```bash
# Setup project with uv (fast!)
make setup

# Start the web UI
make start

# Or run CLI analysis
make analyze
```

Without Make:
```bash
# Install dependencies
pip install -r requirements.txt

# Start web UI
streamlit run app.py
```

Run `make help` to see all available commands.

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
├── app.py                # Streamlit web UI
├── analyze.py            # Main CLI entry point
├── time_analysis.py      # Legacy CLI tool
├── example data/         # Sample data files
├── .env.example          # Environment variables template
├── Makefile              # Build automation
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

### Option 1: Using Make + uv (Recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package installer. Install it first:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then setup the project:
```bash
git clone <repository-url>
cd time_analysis
make setup
source .venv/bin/activate  # Activate virtual environment
```

### Option 2: Using pip

```bash
git clone <repository-url>
cd time_analysis
pip install -r requirements.txt
```

### Option 3: Development Setup

Includes creating .env file and data directory:
```bash
make dev
```

**Dependencies:**
- pandas >= 2.0.0
- plotly >= 5.14.0
- numpy >= 1.24.0
- openpyxl >= 3.1.0
- kaleido >= 0.2.1 (optional, for image export)
- streamlit >= 1.28.0 (for web UI)
- python-dotenv >= 1.0.0 (for environment variables)
- openai >= 1.0.0 (optional, for AI insights)
- anthropic >= 0.7.0 (optional, for AI insights)

## 📖 Usage

### Web UI (Recommended)

Launch the interactive dashboard:

```bash
streamlit run app.py
```

Then open your browser to `http://localhost:8501`

**Features:**
1. **Upload Files**: Drag and drop your Excel/CSV files to save them to the `data/` folder
2. **Select & Analyze**: Choose a file from the dropdown and click "Analyze"
3. **Configure LLM**: Add your OpenAI or Anthropic API key for AI-powered insights
4. **Visualize**: View interactive charts and detailed statistics in tabbed interface
5. **Export**: Download reports and detailed CSV statistics

The web UI provides four main tabs:
- **Overview**: Key metrics and summary statistics
- **Visualizations**: Interactive charts (monthly, weekly, daily, overall distribution)
- **Statistics**: Detailed breakdown and downloadable reports
- **AI Insights**: AI-powered analysis and recommendations (requires API keys)

### Command Line Interface

The tool provides three main commands via `analyze.py`: `analyze`, `compare`, and `summary`.

#### 1. Analyze Command

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

#### 2. Compare Command

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

#### 3. Summary Command

Generate an overall summary of all tracked time.

```bash
python analyze.py summary "example data/" --output reports/
```

#### Legacy CLI Tool

The original CLI tool is still available:

```bash
python time_analysis.py your_data.xlsx --year 2024
```

This will create a `time_analysis_output/` directory with interactive HTML charts, detailed statistics in CSV format, and a text report.

## 🔑 LLM Configuration (Optional)

To enable AI-powered insights in the web UI:

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```

3. Restart the Streamlit app

Alternatively, you can enter API keys directly in the web UI sidebar.

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

Or use the built-in **AI Insights** tab in the web UI for instant analysis!

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

### Web UI (`app.py`)

- **Streamlit Interface**: Interactive dashboard with file management, visualization, and AI integration

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

## 🛠️ Makefile Commands

The project includes a comprehensive Makefile for common tasks:

### Setup & Installation
```bash
make install          # Install dependencies using uv
make setup            # Full project setup (create venv + install)
make dev              # Setup dev environment (includes .env file creation)
```

### Running the Application
```bash
make start            # Start the Streamlit web UI
make frontend         # Alias for 'make start'
```

### Git & Branch Management
```bash
make fetch            # Fetch latest changes from remote
make clean-branches   # Remove local branches that no longer exist on remote
make status           # Show git status
```

### Cleanup
```bash
make clean            # Clean all output and cache files
make clean-output     # Clean analysis output directories only
make clean-cache      # Clean Python cache files only
```

### Analysis (CLI)
```bash
make analyze          # Run CLI analysis on example data
make summary          # Generate summary of example data
```

### Development
```bash
make lint             # Run linting checks (requires ruff)
make format           # Format code (requires ruff)
make check-deps       # Check if required tools are installed
make update-deps      # Update all dependencies
```

Run `make help` to see all available commands with descriptions.

## 📈 Example Workflow

### Option 1: Web UI Workflow (with Makefile)

1. **Setup**: `make setup`
2. **Start the web UI**: `make start`
3. **Upload your time tracking files** via the sidebar
4. **Select a file** and click "Analyze"
5. **Explore visualizations** in the tabs
6. **Get AI insights** by entering your API key and clicking "Generate AI Insights"

### Option 2: Web UI Workflow (without Makefile)

1. **Run the web UI**: `streamlit run app.py`
2. **Upload your time tracking files** via the sidebar
3. **Select a file** and click "Analyze"
4. **Explore visualizations** in the tabs
5. **Get AI insights** by entering your API key and clicking "Generate AI Insights"

### Option 3: CLI Workflow

1. **Track time** in your preferred format (CSV or Excel)
2. **Run weekly analysis** to review the past week:
   ```bash
   python analyze.py analyze data/ --week 2024 1 1 -o reports/week1/
   # Or with make: make analyze
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

- [x] Web dashboard interface
- [x] Integration with AI/LLM for insights
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
3. **Review weekly** to catch patterns early (use the web UI for quick reviews!)
4. **Compare periods** to track long-term trends
5. **Share reports with AI** for personalized coaching (or use the built-in AI Insights tab!)
6. **Set goals** based on the balance score suggestions

## 🙏 Acknowledgments

This tool is designed to help you understand and optimize how you spend your time, enabling data-driven decisions for better work-life balance and personal growth.

---

**Happy Time Tracking! 📊✨**
