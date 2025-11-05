"""Data processing functionality for time tracking data."""

import logging
from typing import Dict, List

import pandas as pd

from .constants import ACTIVITY_TYPES, HOURS_PER_BLOCK

logger = logging.getLogger(__name__)


class DataProcessor:
    """Processes raw time tracking data into analyzable format."""

    def __init__(self, data: pd.DataFrame) -> None:
        """Initialize the data processor.

        Args:
            data: Raw time tracking data
        """
        self.raw_data = data
        self.processed_data: pd.DataFrame | None = None

    def process(self) -> pd.DataFrame:
        """Process the raw data into a format suitable for analysis.

        Returns:
            Processed DataFrame with activity types and details
        """
        logger.info("Processing data...")
        processed_rows: List[Dict[str, str | int]] = []

        for _, row in self.raw_data.iterrows():
            activity = str(row["Activity"])

            if pd.notna(activity) and activity.strip():
                activity_type_code = activity[0].upper() if activity else ""

                if activity_type_code in ACTIVITY_TYPES:
                    processed_row = {
                        "Month": row["Month"],
                        "Week": row["Week"],
                        "Day": row["Day"],
                        "Time": row["Time"],
                        "Activity_Type": ACTIVITY_TYPES[activity_type_code],
                        "Activity_Detail": activity[2:].strip() if len(activity) > 2 else "",
                    }

                    # Add Year if present
                    if "Year" in row and pd.notna(row["Year"]):
                        processed_row["Year"] = row["Year"]

                    processed_rows.append(processed_row)

        self.processed_data = pd.DataFrame(processed_rows)
        logger.info(f"Processed {len(processed_rows)} activities")
        logger.info(f"Processed data shape: {self.processed_data.shape}")

        return self.processed_data

    def get_summary_stats(self) -> Dict[str, any]:
        """Generate summary statistics for the processed data.

        Returns:
            Dictionary containing various statistics
        """
        if self.processed_data is None or self.processed_data.empty:
            raise ValueError("No processed data available. Call process() first.")

        stats = {}

        # Total hours per activity type
        total_hours = self.processed_data["Activity_Type"].value_counts() * HOURS_PER_BLOCK
        stats["total_hours"] = total_hours.to_dict()

        # Hours by day of week
        daily_hours = (
            self.processed_data.groupby(["Day", "Activity_Type"]).size() * HOURS_PER_BLOCK
        )
        stats["daily_hours"] = daily_hours.to_dict()

        # Monthly averages
        monthly_hours = (
            self.processed_data.groupby(["Month", "Activity_Type"]).size() * HOURS_PER_BLOCK
        )
        monthly_avg = monthly_hours.groupby("Activity_Type").mean()
        stats["monthly_averages"] = monthly_avg.to_dict()

        # Most common specific activities
        activity_details = self.processed_data[
            self.processed_data["Activity_Detail"] != ""
        ].copy()

        if not activity_details.empty:
            # Clean activity details
            activity_details["Activity_Detail"] = (
                activity_details["Activity_Detail"]
                .str.strip()
                .str.replace(r"\s+", " ", regex=True)
                .str.replace(r"[/\\]", "-", regex=True)
            )

            # Group by both type and detail
            activity_counts = (
                activity_details.groupby(["Activity_Type", "Activity_Detail"]).size()
                * HOURS_PER_BLOCK
            )

            # Get top 10 activities with their types
            top_activities = {}
            for (activity_type, activity_detail), hours in activity_counts.nlargest(10).items():
                key = f"{activity_detail} ({activity_type})"
                top_activities[key] = hours

            stats["top_activities"] = top_activities
        else:
            stats["top_activities"] = {}

        return stats

    def get_daily_stats(self) -> pd.DataFrame:
        """Get daily statistics by activity type.

        Returns:
            DataFrame with daily statistics
        """
        if self.processed_data is None or self.processed_data.empty:
            raise ValueError("No processed data available. Call process() first.")

        daily_stats = (
            self.processed_data.groupby(["Month", "Week", "Day", "Activity_Type"])
            .agg({"Activity_Detail": "count"})
            .reset_index()
        )

        daily_stats["Hours"] = daily_stats["Activity_Detail"] * HOURS_PER_BLOCK
        daily_stats = daily_stats.rename(columns={"Activity_Detail": "Blocks"})

        return daily_stats

    def get_specific_activity_stats(self) -> pd.DataFrame:
        """Get statistics for specific activities with details.

        Returns:
            DataFrame with specific activity statistics
        """
        if self.processed_data is None or self.processed_data.empty:
            raise ValueError("No processed data available. Call process() first.")

        activity_stats = (
            self.processed_data[self.processed_data["Activity_Detail"] != ""]
            .groupby(["Month", "Week", "Day", "Activity_Type", "Activity_Detail"])
            .size()
            .reset_index(name="Blocks")
        )

        activity_stats["Hours"] = activity_stats["Blocks"] * HOURS_PER_BLOCK

        return activity_stats

    def get_time_slot_patterns(self) -> pd.DataFrame:
        """Get activity patterns by time of day.

        Returns:
            DataFrame with time slot patterns
        """
        if self.processed_data is None or self.processed_data.empty:
            raise ValueError("No processed data available. Call process() first.")

        time_stats = (
            self.processed_data.groupby(["Time", "Activity_Type"])
            .size()
            .reset_index(name="Frequency")
        )

        return time_stats

    def validate_data(self) -> bool:
        """Validate that the processed data is complete and consistent.

        Returns:
            True if data is valid, raises exception otherwise
        """
        if self.processed_data is None or self.processed_data.empty:
            raise ValueError("No processed data available")

        required_columns = ["Month", "Week", "Day", "Time", "Activity_Type"]
        missing_columns = [col for col in required_columns if col not in self.processed_data.columns]

        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        # Check for valid activity types
        valid_types = set(ACTIVITY_TYPES.values())
        invalid_types = set(self.processed_data["Activity_Type"].unique()) - valid_types

        if invalid_types:
            raise ValueError(f"Invalid activity types found: {invalid_types}")

        logger.info("Data validation passed")
        return True
