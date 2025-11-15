"""Statistical calculations for time tracking data."""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from ..models.time_period import TimePeriod


class StatisticsCalculator:
    """Calculate statistical metrics for time tracking data."""

    HOURS_PER_BLOCK = 0.5

    def __init__(self, data: pd.DataFrame):
        """
        Initialize calculator with processed data.

        Args:
            data: Processed DataFrame with activity data
        """
        self.data = data

    def calculate_averages(self, group_by: str = 'Week') -> pd.DataFrame:
        """
        Calculate average hours per activity type grouped by period.

        Args:
            group_by: Grouping level ('Week', 'Month', 'Year')

        Returns:
            DataFrame with average hours
        """
        if group_by == 'Week':
            grouped = self.data.groupby(['Year', 'Month', 'Week', 'Activity_Type'])
        elif group_by == 'Month':
            grouped = self.data.groupby(['Year', 'Month', 'Activity_Type'])
        elif group_by == 'Year':
            grouped = self.data.groupby(['Year', 'Activity_Type'])
        else:
            raise ValueError(f"Invalid group_by: {group_by}")

        counts = grouped.size().reset_index(name='Blocks')
        counts['Hours'] = counts['Blocks'] * self.HOURS_PER_BLOCK

        return counts

    def calculate_trends(self, activity_type: Optional[str] = None) -> pd.DataFrame:
        """
        Calculate trends over time for activity types.

        Args:
            activity_type: Optional specific activity type to analyze

        Returns:
            DataFrame with trend data
        """
        data = self.data
        if activity_type:
            data = data[data['Activity_Type'] == activity_type]

        # Group by week and count
        weekly = data.groupby(['Year', 'Month', 'Week']).size().reset_index(name='Blocks')
        weekly['Hours'] = weekly['Blocks'] * self.HOURS_PER_BLOCK
        weekly['Period'] = weekly.apply(
            lambda x: f"{x['Year']}-M{x['Month']}W{x['Week']}", axis=1
        )

        return weekly

    def calculate_daily_patterns(self) -> pd.DataFrame:
        """
        Calculate patterns by day of week.

        Returns:
            DataFrame with daily patterns
        """
        daily = self.data.groupby(['Day', 'Activity_Type']).size().reset_index(name='Blocks')
        daily['Hours'] = daily['Blocks'] * self.HOURS_PER_BLOCK

        # Calculate percentages
        total_by_day = daily.groupby('Day')['Blocks'].sum()
        daily['Percentage'] = daily.apply(
            lambda x: round(x['Blocks'] / total_by_day[x['Day']] * 100, 2),
            axis=1
        )

        return daily

    def calculate_time_slot_patterns(self) -> pd.DataFrame:
        """
        Calculate patterns by time of day.

        Returns:
            DataFrame with time slot patterns
        """
        time_patterns = self.data.groupby(['Time', 'Activity_Type']).size().reset_index(name='Frequency')

        return time_patterns

    def get_most_productive_times(self, productive_types: List[str] = None) -> pd.DataFrame:
        """
        Find most productive time slots.

        Args:
            productive_types: List of activity types considered productive
                            (defaults to ['Productive Work', 'Mandatory Work'])

        Returns:
            DataFrame with productive time slots
        """
        if productive_types is None:
            productive_types = ['Productive Work', 'Mandatory Work']

        productive_data = self.data[self.data['Activity_Type'].isin(productive_types)]

        time_counts = productive_data.groupby('Time').size().reset_index(name='Frequency')
        time_counts = time_counts.sort_values('Frequency', ascending=False)

        return time_counts

    def calculate_balance_score(self) -> Dict:
        """
        Calculate a balance score based on activity distribution.

        Returns:
            Dictionary with balance metrics
        """
        type_counts = self.data['Activity_Type'].value_counts()
        total = len(self.data)

        # Ideal percentages (these are subjective and can be adjusted)
        ideal_distribution = {
            'Rest': 30,
            'Productive Work': 30,
            'Guilt-free Play': 20,
            'Mandatory Work': 15,
            'Procrastination': 5
        }

        # Calculate deviation from ideal
        deviations = {}
        for activity_type, ideal_pct in ideal_distribution.items():
            actual_pct = (type_counts.get(activity_type, 0) / total * 100) if total > 0 else 0
            deviations[activity_type] = {
                'actual': round(actual_pct, 2),
                'ideal': ideal_pct,
                'deviation': round(abs(actual_pct - ideal_pct), 2)
            }

        # Overall balance score (0-100, higher is better)
        total_deviation = sum(d['deviation'] for d in deviations.values())
        balance_score = max(0, 100 - total_deviation)

        return {
            'balance_score': round(balance_score, 2),
            'deviations': deviations,
            'interpretation': self._interpret_balance_score(balance_score)
        }

    def _interpret_balance_score(self, score: float) -> str:
        """Interpret balance score."""
        if score >= 90:
            return "Excellent - Very well balanced"
        elif score >= 75:
            return "Good - Reasonably balanced"
        elif score >= 60:
            return "Fair - Some room for improvement"
        elif score >= 40:
            return "Needs attention - Consider rebalancing activities"
        else:
            return "Poor - Significant imbalance detected"
