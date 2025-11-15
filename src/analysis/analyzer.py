"""Core time analysis logic."""

import pandas as pd
from typing import Optional, Dict, List
from ..models.time_period import TimePeriod, Week, Month, Year
from ..data.processor import DataProcessor


class TimeAnalyzer:
    """Analyze time tracking data for specific periods."""

    HOURS_PER_BLOCK = 0.5  # Each time block is 30 minutes

    def __init__(self, processor: DataProcessor):
        """
        Initialize analyzer with processed data.

        Args:
            processor: DataProcessor with loaded and processed data
        """
        self.processor = processor
        self.data = processor.get_dataframe()

    def analyze_period(self, period: TimePeriod) -> Dict:
        """
        Analyze a specific time period.

        Args:
            period: TimePeriod (Week, Month, or Year)

        Returns:
            Dictionary containing analysis results
        """
        # Filter data for the period
        if isinstance(period, Week):
            filtered = self.processor.filter_by_period(
                period.year, period.month, period.week
            )
        elif isinstance(period, Month):
            filtered = self.processor.filter_by_period(
                period.year, period.month
            )
        elif isinstance(period, Year):
            filtered = self.processor.filter_by_period(period.year)
        else:
            raise ValueError(f"Unsupported period type: {type(period)}")

        if filtered.empty:
            return {
                'period': str(period),
                'period_label': period.label,
                'total_blocks': 0,
                'total_hours': 0,
                'error': 'No data found for this period'
            }

        # Calculate statistics
        total_blocks = len(filtered)
        total_hours = total_blocks * self.HOURS_PER_BLOCK

        # Activity type distribution
        type_counts = filtered['Activity_Type'].value_counts()
        type_hours = type_counts * self.HOURS_PER_BLOCK
        type_percentages = (type_counts / total_blocks * 100).round(2)

        activity_breakdown = {
            activity_type: {
                'blocks': int(count),
                'hours': round(count * self.HOURS_PER_BLOCK, 1),
                'percentage': round(type_percentages[activity_type], 2)
            }
            for activity_type, count in type_counts.items()
        }

        # Day distribution
        day_counts = filtered.groupby('Day')['Activity_Type'].value_counts()
        daily_breakdown = {}
        for (day, activity_type), count in day_counts.items():
            if day not in daily_breakdown:
                daily_breakdown[day] = {}
            daily_breakdown[day][activity_type] = {
                'blocks': int(count),
                'hours': round(count * self.HOURS_PER_BLOCK, 1)
            }

        # Top activities
        activity_details = filtered[filtered['Activity_Detail'] != '']
        if not activity_details.empty:
            top_activities_counts = (
                activity_details
                .groupby(['Activity_Type', 'Activity_Detail'])
                .size()
                .sort_values(ascending=False)
                .head(10)
            )
            top_activities = [
                {
                    'activity': detail,
                    'type': activity_type,
                    'blocks': int(count),
                    'hours': round(count * self.HOURS_PER_BLOCK, 1)
                }
                for (activity_type, detail), count in top_activities_counts.items()
            ]
        else:
            top_activities = []

        # Time slot patterns
        time_patterns = filtered.groupby('Time')['Activity_Type'].value_counts()
        time_breakdown = {}
        for (time_slot, activity_type), count in time_patterns.items():
            if time_slot not in time_breakdown:
                time_breakdown[time_slot] = {}
            time_breakdown[time_slot][activity_type] = int(count)

        return {
            'period': str(period),
            'period_label': period.label,
            'total_blocks': total_blocks,
            'total_hours': round(total_hours, 1),
            'activity_breakdown': activity_breakdown,
            'daily_breakdown': daily_breakdown,
            'top_activities': top_activities,
            'time_slot_patterns': time_breakdown
        }

    def compare_periods(self, periods: List[TimePeriod]) -> Dict:
        """
        Compare multiple time periods.

        Args:
            periods: List of TimePeriod objects to compare

        Returns:
            Dictionary with comparison data
        """
        comparisons = {}
        for period in periods:
            analysis = self.analyze_period(period)
            comparisons[str(period)] = analysis

        return {
            'periods': [str(p) for p in periods],
            'comparisons': comparisons
        }

    def get_summary_stats(self) -> Dict:
        """
        Get overall summary statistics for all data.

        Returns:
            Dictionary with summary statistics
        """
        total_blocks = len(self.data)
        total_hours = total_blocks * self.HOURS_PER_BLOCK

        # Activity type distribution
        type_counts = self.data['Activity_Type'].value_counts()
        type_hours = type_counts * self.HOURS_PER_BLOCK

        # Date range
        years = sorted(self.data['Year'].unique())
        months = self.data.groupby('Year')['Month'].nunique().sum()
        weeks = len(self.data.groupby(['Year', 'Month', 'Week']))

        # Average hours per day
        days_tracked = len(self.data.groupby(['Year', 'Month', 'Week', 'Day']))
        avg_hours_per_day = total_hours / days_tracked if days_tracked > 0 else 0

        return {
            'total_blocks': total_blocks,
            'total_hours': round(total_hours, 1),
            'years_covered': years,
            'total_months': months,
            'total_weeks': weeks,
            'days_tracked': days_tracked,
            'avg_hours_per_day': round(avg_hours_per_day, 1),
            'activity_totals': {
                activity_type: {
                    'blocks': int(count),
                    'hours': round(hours, 1)
                }
                for (activity_type, count), hours in zip(type_counts.items(), type_hours)
            }
        }
