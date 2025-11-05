"""Statistics generation and reporting functionality."""

import json
import logging
from pathlib import Path
from typing import Dict

import pandas as pd

from .constants import HOURS_PER_BLOCK
from .processor import DataProcessor

logger = logging.getLogger(__name__)


class StatsGenerator:
    """Generates various statistics and reports from processed data."""

    def __init__(self, processor: DataProcessor) -> None:
        """Initialize the stats generator.

        Args:
            processor: DataProcessor instance with processed data
        """
        self.processor = processor
        if processor.processed_data is None or processor.processed_data.empty:
            raise ValueError("Processor must have processed data")

    def generate_text_report(self, year: int = 2024) -> str:
        """Generate a text report of the analysis.

        Args:
            year: Year of the time tracking data

        Returns:
            Formatted text report
        """
        stats = self.processor.get_summary_stats()
        report = [f"Time Analysis Report ({year})", "=" * 50, ""]

        report.append("Total Hours per Activity Type:")
        report.append("-" * 40)
        for activity, hours in sorted(
            stats["total_hours"].items(), key=lambda x: x[1], reverse=True
        ):
            percentage = (hours / sum(stats["total_hours"].values())) * 100
            report.append(f"{activity:20s}: {hours:6.1f} hours ({percentage:5.1f}%)")

        report.append("\nMonthly Average Hours:")
        report.append("-" * 40)
        for activity, hours in sorted(
            stats["monthly_averages"].items(), key=lambda x: x[1], reverse=True
        ):
            report.append(f"{activity:20s}: {hours:6.1f} hours/month")

        if stats.get("top_activities"):
            report.append("\nTop 10 Specific Activities:")
            report.append("-" * 40)
            for activity, hours in list(stats["top_activities"].items())[:10]:
                report.append(f"{activity:45s}: {hours:6.1f} hours")

        # Add summary statistics
        total_hours = sum(stats["total_hours"].values())
        report.append("\n" + "=" * 50)
        report.append(f"Total Tracked Time: {total_hours:.1f} hours")

        # Calculate productivity metrics
        productive_hours = stats["total_hours"].get("Productive Work", 0)
        mandatory_hours = stats["total_hours"].get("Mandatory Work", 0)
        total_work = productive_hours + mandatory_hours

        if total_hours > 0:
            work_percentage = (total_work / total_hours) * 100
            report.append(f"Total Work Time: {total_work:.1f} hours ({work_percentage:.1f}%)")

        return "\n".join(report)

    def save_detailed_stats(self, output_dir: str) -> None:
        """Generate and save detailed statistics to CSV files.

        Args:
            output_dir: Directory to save statistics files
        """
        output_path = Path(output_dir) / "detailed_stats"
        output_path.mkdir(parents=True, exist_ok=True)

        # Save daily activity summary
        daily_stats = self.processor.get_daily_stats()
        daily_stats.to_csv(output_path / "daily_activity_summary.csv", index=False)
        logger.info("Saved daily_activity_summary.csv")

        # Save specific activities
        activity_stats = self.processor.get_specific_activity_stats()
        activity_stats.to_csv(output_path / "specific_activities.csv", index=False)
        logger.info("Saved specific_activities.csv")

        # Save time slot patterns
        time_stats = self.processor.get_time_slot_patterns()
        time_stats.to_csv(output_path / "time_slot_patterns.csv", index=False)
        logger.info("Saved time_slot_patterns.csv")

        # Generate and save summary statistics as JSON
        summary_stats = self._generate_summary_statistics()
        with open(output_path / "summary_statistics.json", "w") as f:
            json.dump(summary_stats, f, indent=2)
        logger.info("Saved summary_statistics.json")

        logger.info(f"\nDetailed statistics saved to {output_path}/")

    def _generate_summary_statistics(self) -> Dict:
        """Generate summary statistics dictionary.

        Returns:
            Dictionary containing summary statistics
        """
        data = self.processor.processed_data

        summary = {
            "total_blocks_by_type": data["Activity_Type"].value_counts().to_dict(),
            "total_hours_by_type": (
                data["Activity_Type"].value_counts() * HOURS_PER_BLOCK
            ).to_dict(),
            "days_tracked": len(data["Day"].unique()),
            "weeks_tracked": len(data.groupby(["Month", "Week"])),
            "total_activities_logged": len(data),
        }

        # Most common activities
        activity_details = data[data["Activity_Detail"] != ""]
        if not activity_details.empty:
            summary["most_common_activities"] = (
                activity_details["Activity_Detail"].value_counts().head(20).to_dict()
            )

            # Activity type by day
            summary["activity_type_by_day"] = (
                data.groupby("Day")["Activity_Type"]
                .value_counts()
                .unstack(fill_value=0)
                .to_dict()
            )

        # Productivity metrics
        productive_hours = summary["total_hours_by_type"].get("Productive Work", 0)
        mandatory_hours = summary["total_hours_by_type"].get("Mandatory Work", 0)
        total_hours = sum(summary["total_hours_by_type"].values())

        summary["productivity_metrics"] = {
            "total_work_hours": productive_hours + mandatory_hours,
            "productive_work_hours": productive_hours,
            "mandatory_work_hours": mandatory_hours,
            "work_percentage": (
                ((productive_hours + mandatory_hours) / total_hours * 100) if total_hours > 0 else 0
            ),
        }

        return summary

    def export_to_csv(self, output_file: str) -> None:
        """Export processed data to CSV file.

        Args:
            output_file: Path to output CSV file
        """
        if self.processor.processed_data is None:
            raise ValueError("No processed data available")

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        self.processor.processed_data.to_csv(output_path, index=False)
        logger.info(f"Exported processed data to {output_path}")
