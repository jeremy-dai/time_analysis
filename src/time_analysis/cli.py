"""Command-line interface for time analysis tool."""

import argparse
import logging
import sys
from pathlib import Path

from .analyzer import TimeAnalyzer
from .constants import DEFAULT_OUTPUT_DIR, DEFAULT_YEAR

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


def setup_argparse() -> argparse.ArgumentParser:
    """Set up command-line argument parser.

    Returns:
        Configured ArgumentParser
    """
    parser = argparse.ArgumentParser(
        description="Analyze time tracking data from CSV or Excel files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze a single Excel file
  time-analysis data.xlsx

  # Analyze multiple CSV files in a directory
  time-analysis data/weekly_csvs/ --year 2024

  # Specify custom output directory
  time-analysis data.xlsx -o my_analysis_results/

CSV File Format:
  - Filename format: YYYY_MM_WW.csv (e.g., 2024_01_01.csv for Year 2024, Month 01, Week 01)
  - Columns: Time, Sunday, Monday, Tuesday, Wednesday, Thursday, Friday, Saturday
  - Activity codes: R (Rest), P (Procrastination), G (Guilt-free Play),
                    M (Mandatory Work), W (Productive Work)
  - Format: "X: Description" where X is the activity code

Excel File Format (Legacy):
  - Sheet names: M.W format (e.g., "1.1" for Month 1, Week 1)
  - Same column and activity code format as CSV
        """,
    )

    parser.add_argument(
        "data_path",
        help="Path to Excel file or directory containing weekly CSV files",
    )

    parser.add_argument(
        "--year",
        "-y",
        type=int,
        default=DEFAULT_YEAR,
        help=f"Year of the time tracking data (default: {DEFAULT_YEAR})",
    )

    parser.add_argument(
        "--output",
        "-o",
        default=DEFAULT_OUTPUT_DIR,
        help=f"Directory to save output files (default: {DEFAULT_OUTPUT_DIR})",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress non-error messages",
    )

    parser.add_argument(
        "--no-plots",
        action="store_true",
        help="Skip generating visualization plots",
    )

    parser.add_argument(
        "--no-stats",
        action="store_true",
        help="Skip generating detailed statistics",
    )

    return parser


def validate_args(args: argparse.Namespace) -> None:
    """Validate command-line arguments.

    Args:
        args: Parsed command-line arguments

    Raises:
        SystemExit: If validation fails
    """
    data_path = Path(args.data_path)

    if not data_path.exists():
        logger.error(f"Error: Path does not exist: {args.data_path}")
        sys.exit(1)

    if data_path.is_dir():
        # Check for CSV files in directory
        csv_files = list(data_path.glob("*.csv"))
        if not csv_files:
            logger.error(f"Error: No CSV files found in directory: {args.data_path}")
            sys.exit(1)
    elif data_path.is_file():
        # Check file extension
        if data_path.suffix.lower() not in [".csv", ".xlsx", ".xls"]:
            logger.error(
                f"Error: Unsupported file format: {data_path.suffix}. "
                "Expected .csv, .xlsx, or .xls"
            )
            sys.exit(1)
    else:
        logger.error(f"Error: Invalid path: {args.data_path}")
        sys.exit(1)

    if args.year < 2000 or args.year > 2100:
        logger.error(f"Error: Invalid year: {args.year}. Expected value between 2000 and 2100")
        sys.exit(1)


def main() -> None:
    """Main entry point for the CLI."""
    parser = setup_argparse()
    args = parser.parse_args()

    # Configure logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    elif args.quiet:
        logging.getLogger().setLevel(logging.ERROR)

    # Validate arguments
    validate_args(args)

    try:
        # Initialize analyzer
        analyzer = TimeAnalyzer(args.data_path, args.year)

        # Load and process data
        logger.info("Loading data...")
        analyzer.load_data()

        logger.info("Processing data...")
        analyzer.process_data()

        # Generate visualizations
        if not args.no_plots:
            logger.info("Generating visualizations...")
            analyzer.generate_visualizations(args.output)

        # Generate detailed statistics
        if not args.no_stats:
            logger.info("Generating detailed statistics...")
            analyzer.save_detailed_stats(args.output)

        # Generate and display report
        logger.info("Generating report...")
        report = analyzer.generate_report()
        print("\n" + report)

        # Save report
        report_path = Path(args.output) / "report.txt"
        report_path.write_text(report)
        logger.info(f"\nReport saved to {report_path}")

        # Summary
        print("\n" + "=" * 50)
        print("Analysis complete!")
        print(f"Output directory: {Path(args.output).absolute()}")
        print("=" * 50)

    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        sys.exit(1)
    except ValueError as e:
        logger.error(f"Invalid data: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
