"""Visualization functionality for time tracking data."""

import logging
from pathlib import Path
from typing import Optional

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from .constants import ACTIVITY_TYPES, DAY_ORDER, HOURS_PER_BLOCK

logger = logging.getLogger(__name__)


class Visualizer:
    """Creates visualizations for time tracking data."""

    def __init__(self, processed_data: pd.DataFrame) -> None:
        """Initialize the visualizer.

        Args:
            processed_data: Processed time tracking data
        """
        self.data = processed_data

    def plot_monthly_distribution(self) -> go.Figure:
        """Create a stacked bar chart showing monthly time distribution.

        Returns:
            Plotly Figure object
        """
        monthly_counts = (
            self.data.groupby(["Month", "Activity_Type"]).size().unstack(fill_value=0)
        )
        monthly_hours = monthly_counts * HOURS_PER_BLOCK

        fig = go.Figure()
        for activity in ACTIVITY_TYPES.values():
            if activity in monthly_hours.columns:
                fig.add_trace(
                    go.Bar(
                        name=activity,
                        x=[f"Month {m}" for m in monthly_hours.index],
                        y=monthly_hours[activity],
                        text=monthly_hours[activity].round(1),
                        textposition="auto",
                    )
                )

        fig.update_layout(
            title="Monthly Time Distribution",
            xaxis_title="Month",
            yaxis_title="Hours",
            barmode="stack",
            showlegend=True,
            height=600,
        )

        return fig

    def plot_daily_distribution(self) -> go.Figure:
        """Create a stacked bar chart showing daily time distribution by day of week.

        Returns:
            Plotly Figure object
        """
        daily_counts = self.data.groupby(["Day", "Activity_Type"]).size().unstack(fill_value=0)
        daily_hours = daily_counts * HOURS_PER_BLOCK

        # Reorder days to start with Sunday
        daily_hours = daily_hours.reindex(DAY_ORDER)

        fig = go.Figure()
        for activity in ACTIVITY_TYPES.values():
            if activity in daily_hours.columns:
                fig.add_trace(
                    go.Bar(
                        name=activity,
                        x=daily_hours.index,
                        y=daily_hours[activity],
                        text=daily_hours[activity].round(1),
                        textposition="auto",
                    )
                )

        fig.update_layout(
            title="Time Distribution by Day of Week",
            xaxis_title="Day",
            yaxis_title="Hours",
            barmode="stack",
            showlegend=True,
            height=600,
        )

        return fig

    def plot_weekly_distribution(self) -> go.Figure:
        """Create a stacked bar chart showing weekly time distribution.

        Returns:
            Plotly Figure object
        """
        weekly_counts = (
            self.data.groupby(["Month", "Week", "Activity_Type"]).size().unstack(fill_value=0)
        )
        weekly_hours = weekly_counts * HOURS_PER_BLOCK

        # Create week labels
        week_labels = [f"M{m}W{w}" for m, w in weekly_hours.index]

        fig = go.Figure()
        for activity in ACTIVITY_TYPES.values():
            if activity in weekly_hours.columns:
                fig.add_trace(
                    go.Bar(
                        name=activity,
                        x=week_labels,
                        y=weekly_hours[activity],
                        text=weekly_hours[activity].round(1),
                        textposition="auto",
                    )
                )

        fig.update_layout(
            title="Weekly Time Distribution",
            xaxis_title="Week",
            yaxis_title="Hours",
            barmode="stack",
            showlegend=True,
            height=600,
        )

        return fig

    def plot_overall_distribution(self) -> go.Figure:
        """Create a pie chart showing overall time distribution.

        Returns:
            Plotly Figure object
        """
        activity_counts = self.data["Activity_Type"].value_counts()
        activity_hours = activity_counts * HOURS_PER_BLOCK

        fig = px.pie(
            values=activity_hours.values,
            names=activity_hours.index,
            title="Overall Time Distribution",
            hole=0.3,
        )
        fig.update_traces(textinfo="percent+label")
        return fig

    def plot_time_of_day_heatmap(self) -> go.Figure:
        """Create a heatmap showing activity patterns by time of day and day of week.

        Returns:
            Plotly Figure object
        """
        # Create pivot table for heatmap
        heatmap_data = (
            self.data.groupby(["Day", "Time", "Activity_Type"]).size().reset_index(name="Count")
        )

        # For each day and time, find the most common activity
        pivot = heatmap_data.pivot_table(
            index="Time", columns="Day", values="Count", aggfunc="sum", fill_value=0
        )

        # Reorder columns by day of week
        pivot = pivot.reindex(columns=DAY_ORDER, fill_value=0)

        fig = go.Figure(
            data=go.Heatmap(
                z=pivot.values,
                x=pivot.columns,
                y=pivot.index,
                colorscale="YlOrRd",
                hoverongaps=False,
            )
        )

        fig.update_layout(
            title="Activity Intensity by Time and Day",
            xaxis_title="Day of Week",
            yaxis_title="Time of Day",
            height=800,
        )

        return fig

    def plot_productivity_trend(self) -> go.Figure:
        """Create a line chart showing productivity trends over time.

        Productivity is defined as Productive Work + Mandatory Work hours.

        Returns:
            Plotly Figure object
        """
        # Calculate productive hours per week
        weekly_data = (
            self.data.groupby(["Month", "Week", "Activity_Type"]).size().unstack(fill_value=0)
            * HOURS_PER_BLOCK
        )

        # Calculate productivity (W + M)
        productive_types = ["Productive Work", "Mandatory Work"]
        productivity = weekly_data[
            [col for col in productive_types if col in weekly_data.columns]
        ].sum(axis=1)

        # Create week labels
        week_labels = [f"M{m}W{w}" for m, w in productivity.index]

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=week_labels,
                y=productivity.values,
                mode="lines+markers",
                name="Total Productive Hours",
                line=dict(color="green", width=3),
                marker=dict(size=8),
            )
        )

        # Add individual components if available
        if "Productive Work" in weekly_data.columns:
            fig.add_trace(
                go.Scatter(
                    x=week_labels,
                    y=weekly_data["Productive Work"],
                    mode="lines",
                    name="Productive Work",
                    line=dict(dash="dash"),
                )
            )

        if "Mandatory Work" in weekly_data.columns:
            fig.add_trace(
                go.Scatter(
                    x=week_labels,
                    y=weekly_data["Mandatory Work"],
                    mode="lines",
                    name="Mandatory Work",
                    line=dict(dash="dash"),
                )
            )

        fig.update_layout(
            title="Productivity Trend Over Time",
            xaxis_title="Week",
            yaxis_title="Hours",
            showlegend=True,
            height=500,
        )

        return fig

    def save_all_plots(self, output_dir: str) -> None:
        """Save all plots to the specified directory.

        Args:
            output_dir: Directory to save plots to
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        plots = {
            "monthly_distribution.html": self.plot_monthly_distribution(),
            "weekly_distribution.html": self.plot_weekly_distribution(),
            "daily_distribution.html": self.plot_daily_distribution(),
            "overall_distribution.html": self.plot_overall_distribution(),
            "time_of_day_heatmap.html": self.plot_time_of_day_heatmap(),
            "productivity_trend.html": self.plot_productivity_trend(),
        }

        for filename, fig in plots.items():
            file_path = output_path / filename
            fig.write_html(file_path)
            logger.info(f"Saved {filename}")

        logger.info(f"All plots saved to {output_dir}")
