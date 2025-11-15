"""Data processor for converting raw data to structured activities."""

import pandas as pd
from typing import List, Optional
from ..models.activity import Activity


class DataProcessor:
    """Process raw time tracking data into structured Activity objects."""

    def __init__(self, raw_data: pd.DataFrame):
        """
        Initialize processor with raw data.

        Args:
            raw_data: DataFrame with columns: Time, Day, Activity, Month, Week, Year
        """
        self.raw_data = raw_data
        self.activities: List[Activity] = []
        self.processed_df: Optional[pd.DataFrame] = None

    def process(self) -> pd.DataFrame:
        """
        Process raw data into structured format.

        Returns:
            DataFrame with processed activity data
        """
        processed_rows = []

        for _, row in self.raw_data.iterrows():
            activity = Activity.parse_from_string(
                activity_str=row['Activity'],
                time_slot=str(row['Time']),
                day=row['Day'],
                month=int(row['Month']),
                week=int(row['Week']),
                year=int(row['Year'])
            )

            if activity:
                self.activities.append(activity)
                processed_rows.append({
                    'Year': activity.year,
                    'Month': activity.month,
                    'Week': activity.week,
                    'Day': activity.day,
                    'Time': activity.time_slot,
                    'Activity_Type': activity.type_label,
                    'Activity_Code': activity.type_code,
                    'Activity_Detail': activity.description
                })

        self.processed_df = pd.DataFrame(processed_rows)
        print(f"Processed {len(processed_rows)} activity records")

        return self.processed_df

    def get_activities(self) -> List[Activity]:
        """Get list of all processed Activity objects."""
        if not self.activities:
            self.process()
        return self.activities

    def get_dataframe(self) -> pd.DataFrame:
        """Get processed data as DataFrame."""
        if self.processed_df is None:
            self.process()
        return self.processed_df

    def filter_by_period(self, year: int, month: Optional[int] = None,
                        week: Optional[int] = None) -> pd.DataFrame:
        """
        Filter activities by time period.

        Args:
            year: Year to filter
            month: Optional month to filter
            week: Optional week to filter (requires month)

        Returns:
            Filtered DataFrame
        """
        if self.processed_df is None:
            self.process()

        filtered = self.processed_df[self.processed_df['Year'] == year]

        if month is not None:
            filtered = filtered[filtered['Month'] == month]

        if week is not None and month is not None:
            filtered = filtered[filtered['Week'] == week]

        return filtered
