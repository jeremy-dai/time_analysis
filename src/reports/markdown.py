"""Generate detailed markdown reports for LLM analysis."""

from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime
import json


class MarkdownReportGenerator:
    """Generate comprehensive markdown reports optimized for LLM consumption."""

    def __init__(self, output_dir: str = "output"):
        """
        Initialize report generator.

        Args:
            output_dir: Directory to save reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_period_report(self, analysis: Dict, filename: str = "report.md") -> str:
        """
        Generate a detailed markdown report for a time period analysis.

        Args:
            analysis: Analysis dictionary from TimeAnalyzer
            filename: Output filename

        Returns:
            Path to generated report
        """
        report_lines = []

        # Header
        report_lines.append(f"# Time Analysis Report: {analysis['period_label']}")
        report_lines.append(f"\n*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")

        # Check for errors
        if 'error' in analysis:
            report_lines.append(f"## ⚠️ Error\n\n{analysis['error']}\n")
            report_path = self.output_dir / filename
            report_path.write_text('\n'.join(report_lines), encoding='utf-8')
            return str(report_path)

        # Executive Summary
        report_lines.append("## 📊 Executive Summary\n")
        report_lines.append(f"- **Period:** {analysis['period_label']}")
        report_lines.append(f"- **Total Time Tracked:** {analysis['total_hours']} hours ({analysis['total_blocks']} blocks)")

        # Quick stats
        if analysis.get('activity_breakdown'):
            top_activity = max(analysis['activity_breakdown'].items(),
                             key=lambda x: x[1]['hours'])
            report_lines.append(f"- **Most Common Activity:** {top_activity[0]} ({top_activity[1]['hours']} hours, {top_activity[1]['percentage']}%)")

        report_lines.append("")

        # Activity Breakdown
        report_lines.append("## 🎯 Activity Type Distribution\n")

        if analysis.get('activity_breakdown'):
            report_lines.append("| Activity Type | Hours | Blocks | Percentage |")
            report_lines.append("|--------------|-------|--------|------------|")

            # Sort by hours descending
            sorted_activities = sorted(
                analysis['activity_breakdown'].items(),
                key=lambda x: x[1]['hours'],
                reverse=True
            )

            for activity_type, stats in sorted_activities:
                report_lines.append(
                    f"| {activity_type} | {stats['hours']} | {stats['blocks']} | {stats['percentage']}% |"
                )

            report_lines.append("")

        # Daily Breakdown
        if analysis.get('daily_breakdown'):
            report_lines.append("## 📅 Daily Breakdown\n")

            day_order = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
            daily_data = analysis['daily_breakdown']

            for day in day_order:
                if day in daily_data:
                    total_hours = sum(stats['hours'] for stats in daily_data[day].values())
                    report_lines.append(f"### {day} ({total_hours} hours)\n")

                    sorted_day_activities = sorted(
                        daily_data[day].items(),
                        key=lambda x: x[1]['hours'],
                        reverse=True
                    )

                    for activity_type, stats in sorted_day_activities:
                        report_lines.append(f"- {activity_type}: {stats['hours']} hours")

                    report_lines.append("")

        # Top Activities
        if analysis.get('top_activities'):
            report_lines.append("## ⭐ Top 10 Specific Activities\n")
            report_lines.append("| Rank | Activity | Type | Hours |")
            report_lines.append("|------|----------|------|-------|")

            for i, activity in enumerate(analysis['top_activities'], 1):
                activity_name = activity['activity'][:50]  # Truncate long names
                report_lines.append(
                    f"| {i} | {activity_name} | {activity['type']} | {activity['hours']} |"
                )

            report_lines.append("")

        # Time Slot Patterns
        if analysis.get('time_slot_patterns'):
            report_lines.append("## ⏰ Time Slot Patterns\n")
            report_lines.append("*Most active time periods:*\n")

            # Calculate total activity per time slot
            time_totals = {}
            for time_slot, activities in analysis['time_slot_patterns'].items():
                time_totals[time_slot] = sum(activities.values())

            # Get top 10 most active time slots
            top_times = sorted(time_totals.items(), key=lambda x: x[1], reverse=True)[:10]

            report_lines.append("| Time | Activity Count | Breakdown |")
            report_lines.append("|------|---------------|-----------|")

            for time_slot, total in top_times:
                breakdown_parts = []
                if time_slot in analysis['time_slot_patterns']:
                    for activity_type, count in analysis['time_slot_patterns'][time_slot].items():
                        breakdown_parts.append(f"{activity_type}: {count}")

                breakdown = ", ".join(breakdown_parts)
                report_lines.append(f"| {time_slot} | {total} | {breakdown} |")

            report_lines.append("")

        # Insights Section for LLM
        report_lines.append("## 💡 Insights for Life Coach Analysis\n")
        report_lines.append("### Context for AI Analysis\n")

        # Provide structured data for LLM
        insights_data = {
            'period': analysis['period_label'],
            'total_hours_tracked': analysis['total_hours'],
            'activity_distribution': analysis.get('activity_breakdown', {}),
            'top_activities': analysis.get('top_activities', [])
        }

        report_lines.append("```json")
        report_lines.append(json.dumps(insights_data, indent=2))
        report_lines.append("```\n")

        # Prompt for LLM analysis
        report_lines.append("### Suggested Analysis Questions\n")
        report_lines.append("1. **Work-Life Balance:** Is there a healthy balance between work, rest, and leisure?")
        report_lines.append("2. **Productivity Patterns:** When are the most productive hours?")
        report_lines.append("3. **Improvement Areas:** Where might time be better allocated?")
        report_lines.append("4. **Positive Habits:** What positive patterns emerge?")
        report_lines.append("5. **Recommendations:** What specific, actionable changes could improve well-being?")

        # Save report
        report_path = self.output_dir / filename
        report_path.write_text('\n'.join(report_lines), encoding='utf-8')
        print(f"Generated report: {report_path}")

        return str(report_path)

    def generate_comparison_report(self, comparison_data: Dict, filename: str = "comparison.md") -> str:
        """
        Generate a comparison report for multiple periods.

        Args:
            comparison_data: Comparison dictionary from TimeAnalyzer
            filename: Output filename

        Returns:
            Path to generated report
        """
        report_lines = []

        # Header
        report_lines.append("# Time Analysis Comparison Report\n")
        report_lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")

        periods = comparison_data.get('periods', [])
        comparisons = comparison_data.get('comparisons', {})

        report_lines.append(f"## 📊 Comparing {len(periods)} Periods\n")

        # Overview table
        report_lines.append("| Period | Total Hours | Top Activity |")
        report_lines.append("|--------|-------------|--------------|")

        for period in periods:
            if period in comparisons:
                analysis = comparisons[period]
                if 'error' not in analysis:
                    top_activity = "N/A"
                    if analysis.get('activity_breakdown'):
                        top_activity = max(
                            analysis['activity_breakdown'].items(),
                            key=lambda x: x[1]['hours']
                        )[0]

                    report_lines.append(
                        f"| {analysis['period_label']} | {analysis['total_hours']} | {top_activity} |"
                    )

        report_lines.append("")

        # Detailed comparison by activity type
        report_lines.append("## 📈 Activity Type Trends\n")

        # Collect all activity types
        all_activity_types = set()
        for period, analysis in comparisons.items():
            if 'error' not in analysis and 'activity_breakdown' in analysis:
                all_activity_types.update(analysis['activity_breakdown'].keys())

        for activity_type in sorted(all_activity_types):
            report_lines.append(f"### {activity_type}\n")
            report_lines.append("| Period | Hours | Percentage |")
            report_lines.append("|--------|-------|------------|")

            for period in periods:
                if period in comparisons:
                    analysis = comparisons[period]
                    if 'error' not in analysis:
                        breakdown = analysis.get('activity_breakdown', {})
                        if activity_type in breakdown:
                            stats = breakdown[activity_type]
                            report_lines.append(
                                f"| {analysis['period_label']} | {stats['hours']} | {stats['percentage']}% |"
                            )
                        else:
                            report_lines.append(f"| {analysis['period_label']} | 0 | 0% |")

            report_lines.append("")

        # Insights for LLM
        report_lines.append("## 💡 Comparative Insights for Life Coach Analysis\n")
        report_lines.append("### Trend Data\n")

        report_lines.append("```json")
        report_lines.append(json.dumps(comparison_data, indent=2, default=str))
        report_lines.append("```\n")

        report_lines.append("### Analysis Focus Points\n")
        report_lines.append("1. **Consistency:** How consistent is time allocation across periods?")
        report_lines.append("2. **Trends:** Are there positive or negative trends over time?")
        report_lines.append("3. **Variability:** Which activities fluctuate most?")
        report_lines.append("4. **Progress:** Is there movement toward stated goals?")

        # Save report
        report_path = self.output_dir / filename
        report_path.write_text('\n'.join(report_lines), encoding='utf-8')
        print(f"Generated comparison report: {report_path}")

        return str(report_path)

    def generate_summary_report(self, summary_stats: Dict, filename: str = "summary.md") -> str:
        """
        Generate an overall summary report.

        Args:
            summary_stats: Summary statistics dictionary
            filename: Output filename

        Returns:
            Path to generated report
        """
        report_lines = []

        # Header
        report_lines.append("# Overall Time Tracking Summary\n")
        report_lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")

        # Overview
        report_lines.append("## 📊 Overview\n")
        report_lines.append(f"- **Total Hours Tracked:** {summary_stats['total_hours']}")
        report_lines.append(f"- **Total Blocks:** {summary_stats['total_blocks']}")
        report_lines.append(f"- **Days Tracked:** {summary_stats['days_tracked']}")
        report_lines.append(f"- **Weeks Tracked:** {summary_stats['total_weeks']}")
        report_lines.append(f"- **Years Covered:** {', '.join(map(str, summary_stats['years_covered']))}")
        report_lines.append(f"- **Average Hours/Day:** {summary_stats['avg_hours_per_day']}")
        report_lines.append("")

        # Activity totals
        report_lines.append("## 🎯 Total Hours by Activity Type\n")
        report_lines.append("| Activity Type | Total Hours | Total Blocks |")
        report_lines.append("|--------------|-------------|--------------|")

        activity_totals = summary_stats.get('activity_totals', {})
        sorted_activities = sorted(
            activity_totals.items(),
            key=lambda x: x[1]['hours'],
            reverse=True
        )

        for activity_type, stats in sorted_activities:
            report_lines.append(
                f"| {activity_type} | {stats['hours']} | {stats['blocks']} |"
            )

        report_lines.append("")

        # Save report
        report_path = self.output_dir / filename
        report_path.write_text('\n'.join(report_lines), encoding='utf-8')
        print(f"Generated summary report: {report_path}")

        return str(report_path)
