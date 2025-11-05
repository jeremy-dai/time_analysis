"""Main TimeAnalyzer class that orchestrates all components."""

import logging
from pathlib import Path
from typing import Optional

import pandas as pd

from .constants import DEFAULT_OUTPUT_DIR, DEFAULT_YEAR
from .data_loader import DataLoader
from .processor import DataProcessor
from .stats import StatsGenerator
from .visualizer import Visualizer

logger = logging.getLogger(__name__)


class TimeAnalyzer:
    """Main class for analyzing time tracking data."""

    def __init__(self, data_path: str, year: int = DEFAULT_YEAR) -> None:
        """Initialize the time analyzer.

        Args:
            data_path: Path to data file or directory containing CSV files
            year: Year of the time tracking data
        """
        self.data_path = Path(data_path)
        self.year = year
        self.loader: Optional[DataLoader] = None
        self.processor: Optional[DataProcessor] = None
        self.visualizer: Optional[Visualizer] = None
        self.stats_generator: Optional[StatsGenerator] = None
        self.raw_data: Optional[pd.DataFrame] = None
        self.processed_data: Optional[pd.DataFrame] = None

    def load_data(self) -> "TimeAnalyzer":
        """Load data from files.

        Returns:
            Self for method chaining
        """
        if self.data_path.is_dir():
            # Load multiple CSV files from directory
            self.loader = DataLoader(str(self.data_path / "dummy.csv"))
            self.raw_data = self.loader.load_csv_files(str(self.data_path))
        else:
            # Load single file
            self.loader = DataLoader(str(self.data_path))
            self.raw_data = self.loader.load()

        logger.info(f"Loaded {len(self.raw_data)} records")
        return self

    def process_data(self) -> "TimeAnalyzer":
        """Process the loaded data.

        Returns:
            Self for method chaining
        """
        if self.raw_data is None:
            self.load_data()

        self.processor = DataProcessor(self.raw_data)
        self.processed_data = self.processor.process()
        self.processor.validate_data()

        logger.info(f"Processed {len(self.processed_data)} activities")
        return self

    def generate_visualizations(self, output_dir: str = DEFAULT_OUTPUT_DIR) -> "TimeAnalyzer":
        """Generate all visualizations.

        Args:
            output_dir: Directory to save visualizations

        Returns:
            Self for method chaining
        """
        if self.processed_data is None:
            self.process_data()

        self.visualizer = Visualizer(self.processed_data)
        self.visualizer.save_all_plots(output_dir)

        return self

    def generate_report(self) -> str:
        """Generate text report.

        Returns:
            Formatted text report
        """
        if self.processor is None:
            self.process_data()

        self.stats_generator = StatsGenerator(self.processor)
        return self.stats_generator.generate_text_report(self.year)

    def save_detailed_stats(self, output_dir: str = DEFAULT_OUTPUT_DIR) -> "TimeAnalyzer":
        """Save detailed statistics to files.

        Args:
            output_dir: Directory to save statistics

        Returns:
            Self for method chaining
        """
        if self.processor is None:
            self.process_data()

        if self.stats_generator is None:
            self.stats_generator = StatsGenerator(self.processor)

        self.stats_generator.save_detailed_stats(output_dir)

        return self

    def run_full_analysis(self, output_dir: str = DEFAULT_OUTPUT_DIR) -> str:
        """Run complete analysis pipeline.

        Args:
            output_dir: Directory to save all outputs

        Returns:
            Text report
        """
        logger.info("Starting full analysis...")

        # Load and process data
        self.load_data()
        self.process_data()

        # Generate outputs
        self.generate_visualizations(output_dir)
        self.save_detailed_stats(output_dir)
        report = self.generate_report()

        # Save report
        report_path = Path(output_dir) / "report.txt"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report)
        logger.info(f"Report saved to {report_path}")

        logger.info("Full analysis complete!")
        return report
