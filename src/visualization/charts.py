"""Chart generation for time tracking data."""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, Optional, List
from ..models.time_period import TimePeriod, Week, Month, Year


class ChartGenerator:
    """Generate visualizations for time tracking analysis."""

    # Color scheme for activity types
    ACTIVITY_COLORS = {
        'Rest': '#4ECDC4',
        'Procrastination': '#FF6B6B',
        'Guilt-free Play': '#95E1D3',
        'Mandatory Work': '#F38181',
        'Productive Work': '#AA96DA'
    }

    def __init__(self, data: pd.DataFrame):
        """
        Initialize chart generator.

        Args:
            data: Processed DataFrame with activity data
        """
        self.data = data

    def create_period_distribution(self, period_data: pd.DataFrame,
                                   title: str, period_type: str = 'Week') -> go.Figure:
        """
        Create a stacked bar chart for period distribution.

        Args:
            period_data: Filtered data for specific period
            title: Chart title
            period_type: Type of period (Week, Month, Year)

        Returns:
            Plotly Figure object
        """
        # Calculate hours by activity type
        activity_counts = period_data.groupby('Activity_Type').size()
        activity_hours = activity_counts * 0.5

        # Create stacked bar chart
        fig = go.Figure()

        for activity_type in sorted(activity_hours.index):
            fig.add_trace(go.Bar(
                name=activity_type,
                x=[title],
                y=[activity_hours[activity_type]],
                marker_color=self.ACTIVITY_COLORS.get(activity_type, '#CCCCCC'),
                text=f"{activity_hours[activity_type]:.1f}h",
                textposition='inside'
            ))

        fig.update_layout(
            title=f"{title} - Time Distribution",
            xaxis_title=period_type,
            yaxis_title='Hours',
            barmode='stack',
            showlegend=True,
            height=500,
            template='plotly_white'
        )

        return fig

    def create_daily_breakdown(self, period_data: pd.DataFrame, title: str) -> go.Figure:
        """
        Create daily breakdown chart for a period.

        Args:
            period_data: Filtered data for specific period
            title: Chart title

        Returns:
            Plotly Figure object
        """
        # Group by day and activity type
        daily_counts = period_data.groupby(['Day', 'Activity_Type']).size().unstack(fill_value=0)
        daily_hours = daily_counts * 0.5

        # Reorder days
        day_order = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        daily_hours = daily_hours.reindex([d for d in day_order if d in daily_hours.index])

        fig = go.Figure()

        for activity_type in daily_hours.columns:
            fig.add_trace(go.Bar(
                name=activity_type,
                x=daily_hours.index,
                y=daily_hours[activity_type],
                marker_color=self.ACTIVITY_COLORS.get(activity_type, '#CCCCCC'),
                text=daily_hours[activity_type].round(1),
                textposition='auto'
            ))

        fig.update_layout(
            title=f"{title} - Daily Breakdown",
            xaxis_title='Day of Week',
            yaxis_title='Hours',
            barmode='stack',
            showlegend=True,
            height=500,
            template='plotly_white'
        )

        return fig

    def create_pie_chart(self, period_data: pd.DataFrame, title: str) -> go.Figure:
        """
        Create pie chart showing activity distribution.

        Args:
            period_data: Filtered data for specific period
            title: Chart title

        Returns:
            Plotly Figure object
        """
        activity_counts = period_data['Activity_Type'].value_counts()
        activity_hours = activity_counts * 0.5

        colors = [self.ACTIVITY_COLORS.get(at, '#CCCCCC') for at in activity_hours.index]

        fig = go.Figure(data=[go.Pie(
            labels=activity_hours.index,
            values=activity_hours.values,
            marker=dict(colors=colors),
            textinfo='label+percent',
            hovertemplate='%{label}<br>%{value:.1f} hours<br>%{percent}<extra></extra>'
        )])

        fig.update_layout(
            title=f"{title} - Activity Distribution",
            height=500,
            template='plotly_white'
        )

        return fig

    def create_time_heatmap(self, period_data: pd.DataFrame, title: str) -> go.Figure:
        """
        Create heatmap showing activity patterns by time and day.

        Args:
            period_data: Filtered data for specific period
            title: Chart title

        Returns:
            Plotly Figure object
        """
        # Create pivot table with time slots and days
        day_order = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

        # Count activities by time and day
        heatmap_data = period_data.groupby(['Time', 'Day']).size().unstack(fill_value=0)

        # Reorder columns
        heatmap_data = heatmap_data.reindex(columns=[d for d in day_order if d in heatmap_data.columns])

        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data.values,
            x=heatmap_data.columns,
            y=heatmap_data.index,
            colorscale='Blues',
            hovertemplate='%{y}<br>%{x}<br>Activity blocks: %{z}<extra></extra>'
        ))

        fig.update_layout(
            title=f"{title} - Activity Heatmap",
            xaxis_title='Day of Week',
            yaxis_title='Time of Day',
            height=600,
            template='plotly_white'
        )

        return fig

    def create_comparison_chart(self, periods_data: Dict[str, pd.DataFrame]) -> go.Figure:
        """
        Create comparison chart for multiple periods.

        Args:
            periods_data: Dictionary of {period_label: period_dataframe}

        Returns:
            Plotly Figure object
        """
        fig = go.Figure()

        # Calculate hours for each period and activity type
        for period_label, period_data in periods_data.items():
            activity_counts = period_data.groupby('Activity_Type').size()
            activity_hours = activity_counts * 0.5

            for activity_type in activity_hours.index:
                fig.add_trace(go.Bar(
                    name=activity_type,
                    x=[period_label],
                    y=[activity_hours[activity_type]],
                    marker_color=self.ACTIVITY_COLORS.get(activity_type, '#CCCCCC'),
                    legendgroup=activity_type,
                    showlegend=period_label == list(periods_data.keys())[0]
                ))

        fig.update_layout(
            title='Period Comparison',
            xaxis_title='Time Period',
            yaxis_title='Hours',
            barmode='group',
            height=500,
            template='plotly_white'
        )

        return fig

    def create_trend_chart(self, trend_data: pd.DataFrame, activity_type: Optional[str] = None) -> go.Figure:
        """
        Create trend line chart over time.

        Args:
            trend_data: DataFrame with trend data (must have 'Period' and 'Hours' columns)
            activity_type: Optional activity type for title

        Returns:
            Plotly Figure object
        """
        title = f"Trend Over Time"
        if activity_type:
            title += f" - {activity_type}"

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=trend_data['Period'],
            y=trend_data['Hours'],
            mode='lines+markers',
            name='Hours',
            line=dict(color='#AA96DA', width=2),
            marker=dict(size=8)
        ))

        fig.update_layout(
            title=title,
            xaxis_title='Period',
            yaxis_title='Hours',
            height=400,
            template='plotly_white',
            showlegend=False
        )

        return fig

    def create_top_activities_chart(self, top_activities: List[Dict]) -> go.Figure:
        """
        Create horizontal bar chart for top activities.

        Args:
            top_activities: List of activity dictionaries with 'activity', 'type', 'hours'

        Returns:
            Plotly Figure object
        """
        if not top_activities:
            # Return empty figure
            fig = go.Figure()
            fig.update_layout(
                title="Top Activities - No Data",
                template='plotly_white'
            )
            return fig

        activities = [f"{a['activity'][:30]}..." if len(a['activity']) > 30 else a['activity']
                     for a in top_activities]
        hours = [a['hours'] for a in top_activities]
        colors = [self.ACTIVITY_COLORS.get(a['type'], '#CCCCCC') for a in top_activities]

        fig = go.Figure(data=[go.Bar(
            y=activities[::-1],  # Reverse for top-to-bottom display
            x=hours[::-1],
            orientation='h',
            marker=dict(color=colors[::-1]),
            text=[f"{h:.1f}h" for h in hours[::-1]],
            textposition='auto'
        )])

        fig.update_layout(
            title='Top 10 Activities by Time Spent',
            xaxis_title='Hours',
            yaxis_title='Activity',
            height=500,
            template='plotly_white',
            showlegend=False
        )

        return fig
