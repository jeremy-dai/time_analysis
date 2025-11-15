"""Command-line interface for time analysis."""

import argparse
import sys
from pathlib import Path
from typing import Optional

from .data.loader import DataLoader
from .data.processor import DataProcessor
from .models.time_period import Week, Month, Year
from .analysis.analyzer import TimeAnalyzer
from .analysis.statistics import StatisticsCalculator
from .visualization.charts import ChartGenerator
from .visualization.exporter import VisualizationExporter
from .reports.markdown import MarkdownReportGenerator


class TimeAnalysisCLI:
    """Command-line interface for time tracking analysis."""

    def __init__(self):
        self.parser = self._create_parser()

    def _create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser."""
        parser = argparse.ArgumentParser(
            description='Analyze personal time tracking data',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Analyze entire directory
  python -m src.cli analyze example_data/ --output reports/

  # Analyze specific week
  python -m src.cli analyze example_data/ --week 2023 1 1 --output reports/

  # Analyze specific month
  python -m src.cli analyze example_data/ --month 2023 1 --output reports/

  # Analyze entire year
  python -m src.cli analyze example_data/ --year 2023 --output reports/

  # Compare multiple weeks
  python -m src.cli compare example_data/ --weeks "2023-1-1,2023-1-2,2023-1-3"
            """
        )

        subparsers = parser.add_subparsers(dest='command', help='Command to run')

        # Analyze command
        analyze_parser = subparsers.add_parser('analyze', help='Analyze time tracking data')
        analyze_parser.add_argument('data_path', help='Path to data file or directory')
        analyze_parser.add_argument('--output', '-o', default='output',
                                   help='Output directory (default: output)')

        # Period selection (mutually exclusive)
        period_group = analyze_parser.add_mutually_exclusive_group()
        period_group.add_argument('--week', nargs=3, metavar=('YEAR', 'MONTH', 'WEEK'),
                                 help='Analyze specific week (e.g., --week 2023 1 1)')
        period_group.add_argument('--month', nargs=2, metavar=('YEAR', 'MONTH'),
                                 help='Analyze specific month (e.g., --month 2023 1)')
        period_group.add_argument('--year', type=int, metavar='YEAR',
                                 help='Analyze specific year (e.g., --year 2023)')

        # Export options
        analyze_parser.add_argument('--no-images', action='store_true',
                                   help='Skip image generation')
        analyze_parser.add_argument('--no-html', action='store_true',
                                   help='Skip HTML generation')
        analyze_parser.add_argument('--no-markdown', action='store_true',
                                   help='Skip markdown report generation')

        # Compare command
        compare_parser = subparsers.add_parser('compare', help='Compare multiple time periods')
        compare_parser.add_argument('data_path', help='Path to data file or directory')
        compare_parser.add_argument('--weeks', help='Comma-separated weeks (e.g., "2023-1-1,2023-1-2")')
        compare_parser.add_argument('--months', help='Comma-separated months (e.g., "2023-1,2023-2")')
        compare_parser.add_argument('--years', help='Comma-separated years (e.g., "2023,2024")')
        compare_parser.add_argument('--output', '-o', default='output',
                                   help='Output directory (default: output)')

        # Summary command
        summary_parser = subparsers.add_parser('summary', help='Generate overall summary')
        summary_parser.add_argument('data_path', help='Path to data file or directory')
        summary_parser.add_argument('--output', '-o', default='output',
                                   help='Output directory (default: output)')

        return parser

    def run(self, args=None):
        """Run the CLI."""
        parsed_args = self.parser.parse_args(args)

        if not parsed_args.command:
            self.parser.print_help()
            sys.exit(1)

        if parsed_args.command == 'analyze':
            self._run_analyze(parsed_args)
        elif parsed_args.command == 'compare':
            self._run_compare(parsed_args)
        elif parsed_args.command == 'summary':
            self._run_summary(parsed_args)

    def _load_data(self, data_path: str) -> tuple:
        """Load and process data."""
        print(f"\n📂 Loading data from: {data_path}")
        loader = DataLoader(data_path)
        raw_data = loader.load()

        print("⚙️  Processing data...")
        processor = DataProcessor(raw_data)
        processor.process()

        return processor, raw_data

    def _run_analyze(self, args):
        """Run analysis command."""
        print("\n" + "="*60)
        print("TIME TRACKING ANALYSIS")
        print("="*60)

        # Load data
        processor, raw_data = self._load_data(args.data_path)

        # Create analyzer
        analyzer = TimeAnalyzer(processor)

        # Determine period
        period = None
        period_name = "all_data"

        if args.week:
            year, month, week = map(int, args.week)
            period = Week(year=year, month=month, week=week)
            period_name = f"week_{year}_{month}_{week}"
        elif args.month:
            year, month = map(int, args.month)
            period = Month(year=year, month=month)
            period_name = f"month_{year}_{month}"
        elif args.year:
            period = Year(year=args.year)
            period_name = f"year_{args.year}"
        else:
            # Analyze all available data by year
            years = sorted(processor.get_dataframe()['Year'].unique())
            if len(years) == 1:
                period = Year(year=int(years[0]))
                period_name = f"year_{years[0]}"

        # Run analysis
        if period:
            print(f"\n🔍 Analyzing: {period.label}")
            analysis = analyzer.analyze_period(period)
        else:
            print("\n🔍 Generating overall summary")
            analysis = analyzer.get_summary_stats()

        # Create exporters
        exporter = VisualizationExporter(args.output)
        report_gen = MarkdownReportGenerator(args.output)

        # Generate visualizations
        if period and 'error' not in analysis:
            chart_gen = ChartGenerator(processor.get_dataframe())

            # Filter data for period
            if isinstance(period, Week):
                period_data = processor.filter_by_period(period.year, period.month, period.week)
            elif isinstance(period, Month):
                period_data = processor.filter_by_period(period.year, period.month)
            elif isinstance(period, Year):
                period_data = processor.filter_by_period(period.year)
            else:
                period_data = processor.get_dataframe()

            if not period_data.empty:
                print("\n📊 Generating visualizations...")

                # Distribution chart
                fig = chart_gen.create_period_distribution(
                    period_data, period.label, type(period).__name__
                )
                if not args.no_html:
                    exporter.export_html(fig, f"{period_name}_distribution")
                if not args.no_images:
                    exporter.export_image(fig, f"{period_name}_distribution")

                # Daily breakdown
                if len(period_data['Day'].unique()) > 1:
                    fig = chart_gen.create_daily_breakdown(period_data, period.label)
                    if not args.no_html:
                        exporter.export_html(fig, f"{period_name}_daily")
                    if not args.no_images:
                        exporter.export_image(fig, f"{period_name}_daily")

                # Pie chart
                fig = chart_gen.create_pie_chart(period_data, period.label)
                if not args.no_html:
                    exporter.export_html(fig, f"{period_name}_pie")
                if not args.no_images:
                    exporter.export_image(fig, f"{period_name}_pie")

                # Top activities
                if analysis.get('top_activities'):
                    fig = chart_gen.create_top_activities_chart(analysis['top_activities'])
                    if not args.no_html:
                        exporter.export_html(fig, f"{period_name}_top_activities")
                    if not args.no_images:
                        exporter.export_image(fig, f"{period_name}_top_activities")

                # Time heatmap
                fig = chart_gen.create_time_heatmap(period_data, period.label)
                if not args.no_html:
                    exporter.export_html(fig, f"{period_name}_heatmap")
                if not args.no_images:
                    exporter.export_image(fig, f"{period_name}_heatmap")

        # Generate markdown report
        if not args.no_markdown and period:
            print("\n📝 Generating markdown report...")
            report_gen.generate_period_report(analysis, f"{period_name}_report.md")

        # Export analysis data as JSON
        exporter.export_data(analysis, f"{period_name}_data")

        print(f"\n✅ Analysis complete! Output saved to: {args.output}/")
        print("\n" + "="*60)

    def _run_compare(self, args):
        """Run comparison command."""
        print("\n" + "="*60)
        print("TIME TRACKING COMPARISON")
        print("="*60)

        # Load data
        processor, _ = self._load_data(args.data_path)

        # Parse periods
        periods = []

        if args.weeks:
            for week_str in args.weeks.split(','):
                year, month, week = map(int, week_str.strip().split('-'))
                periods.append(Week(year=year, month=month, week=week))

        if args.months:
            for month_str in args.months.split(','):
                year, month = map(int, month_str.strip().split('-'))
                periods.append(Month(year=year, month=month))

        if args.years:
            for year_str in args.years.split(','):
                periods.append(Year(year=int(year_str.strip())))

        if not periods:
            print("Error: No periods specified for comparison")
            sys.exit(1)

        # Run comparison
        analyzer = TimeAnalyzer(processor)
        print(f"\n🔍 Comparing {len(periods)} periods...")
        comparison = analyzer.compare_periods(periods)

        # Generate reports
        exporter = VisualizationExporter(args.output)
        report_gen = MarkdownReportGenerator(args.output)

        print("\n📊 Generating comparison visualizations...")

        # Create comparison data for charts
        periods_data = {}
        for period in periods:
            if isinstance(period, Week):
                period_data = processor.filter_by_period(period.year, period.month, period.week)
            elif isinstance(period, Month):
                period_data = processor.filter_by_period(period.year, period.month)
            elif isinstance(period, Year):
                period_data = processor.filter_by_period(period.year)

            if not period_data.empty:
                periods_data[period.label] = period_data

        if periods_data:
            chart_gen = ChartGenerator(processor.get_dataframe())
            fig = chart_gen.create_comparison_chart(periods_data)
            exporter.export_html(fig, "comparison_chart")
            exporter.export_image(fig, "comparison_chart")

        print("\n📝 Generating comparison report...")
        report_gen.generate_comparison_report(comparison, "comparison_report.md")

        exporter.export_data(comparison, "comparison_data")

        print(f"\n✅ Comparison complete! Output saved to: {args.output}/")
        print("\n" + "="*60)

    def _run_summary(self, args):
        """Run summary command."""
        print("\n" + "="*60)
        print("TIME TRACKING SUMMARY")
        print("="*60)

        # Load data
        processor, _ = self._load_data(args.data_path)

        # Generate summary
        analyzer = TimeAnalyzer(processor)
        print("\n🔍 Generating summary statistics...")
        summary = analyzer.get_summary_stats()

        # Create exporters
        exporter = VisualizationExporter(args.output)
        report_gen = MarkdownReportGenerator(args.output)

        # Generate overall visualizations
        print("\n📊 Generating summary visualizations...")
        chart_gen = ChartGenerator(processor.get_dataframe())
        stats_calc = StatisticsCalculator(processor.get_dataframe())

        # Overall pie chart
        fig = chart_gen.create_pie_chart(processor.get_dataframe(), "Overall Distribution")
        exporter.export_html(fig, "summary_overall_pie")
        exporter.export_image(fig, "summary_overall_pie")

        # Daily patterns
        daily_patterns = stats_calc.calculate_daily_patterns()
        print(f"\n📅 Daily patterns calculated: {len(daily_patterns)} records")

        # Generate markdown report
        print("\n📝 Generating summary report...")
        report_gen.generate_summary_report(summary, "summary_report.md")

        exporter.export_data(summary, "summary_data")

        print(f"\n✅ Summary complete! Output saved to: {args.output}/")
        print("\n" + "="*60)


def main():
    """Main entry point."""
    cli = TimeAnalysisCLI()
    cli.run()


if __name__ == '__main__':
    main()
