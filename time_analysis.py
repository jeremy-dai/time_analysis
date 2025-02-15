import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import numpy as np
import argparse
import sys
import warnings
from datetime import datetime

# Suppress openpyxl warnings
warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')

class TimeAnalyzer:
    def __init__(self, excel_path, year=2024):
        self.excel_path = excel_path
        self.year = year
        self.activity_types = {
            'R': 'Rest',
            'P': 'Procrastination',
            'G': 'Guilt-free Play',
            'M': 'Mandatory Work',
            'W': 'Productive Work'
        }
        self.data = None
        self.processed_data = None
    
    def parse_sheet_name(self, sheet_name):
        """Convert sheet name (x.y) to month and week number"""
        print(f"Parsing sheet name: {sheet_name} (type: {type(sheet_name)})")
        
        if isinstance(sheet_name, float):
            sheet_name = str(int(sheet_name))
        if sheet_name.lower() == 'sample':
            return None, None
            
        month, week = map(int, sheet_name.split('.'))
        print(f"Parsed month: {month}, week: {week}")
        return month, week
    
    def load_data(self):
        """Load all sheets from the Excel file and combine them"""
        print(f"\nLoading Excel file: {self.excel_path}")
        excel_file = pd.ExcelFile(self.excel_path)
        print(f"Found sheets: {excel_file.sheet_names}")
        
        all_sheets = []
        for sheet_name in excel_file.sheet_names:
            print(f"\nProcessing sheet: {sheet_name}")
            
            # Parse sheet name
            try:
                month, week = self.parse_sheet_name(sheet_name)
            except Exception as e:
                print(f"Error parsing sheet name: {str(e)}")
                continue
                
            if month is None:
                print("Skipping sheet (invalid name format)")
                continue
            
            # Read the sheet, skipping the first row and using second row as header
            df = pd.read_excel(
                self.excel_path,
                sheet_name=sheet_name,
                skiprows=1,  # Skip the first row (SAMPLE)
                usecols="A:H"  # Only use columns A through H
            )            
            # Rename columns to standard format
            weekdays = ['Time', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
            df.columns = weekdays            
            # Melt the dataframe to convert days to rows
            df_melted = df.melt(
                id_vars=['Time'],
                value_vars=weekdays[1:],  # All days except Time
                var_name='Day',
                value_name='Activity'
            )
            
            df_melted['Month'] = month
            df_melted['Week'] = week
            all_sheets.append(df_melted)
            print(f"Successfully processed sheet {sheet_name}")
        
        if not all_sheets:
            print("No valid sheets were processed!")
            sys.exit(1)
        
        self.data = pd.concat(all_sheets, ignore_index=True)
        print(f"\nFinal combined data shape: {self.data.shape}")
        print(f"Final columns: {self.data.columns.tolist()}")
        return self
    
    def process_data(self):
        """Process the raw data into a format suitable for analysis"""
        if self.data is None:
            self.load_data()
        
        print("\nProcessing data...")
        processed_rows = []
        for idx, row in self.data.iterrows():          
            activity = str(row['Activity'])
            if pd.notna(activity) and activity.strip():
                activity_type = activity[0].upper() if activity else ''
                
                if activity_type in self.activity_types:
                    processed_rows.append({
                        'Month': row['Month'],
                        'Week': row['Week'],
                        'Day': row['Day'],
                        'Time': row['Time'],
                        'Activity_Type': self.activity_types[activity_type],
                        'Activity_Detail': activity[2:] if len(activity) > 2 else ''
                    })
        
        self.processed_data = pd.DataFrame(processed_rows)
        print(f"\nProcessed {len(processed_rows)} activities")
        print(f"Processed data shape: {self.processed_data.shape}")
        print(f"Sample of processed data:\n{self.processed_data.head()}")
        return self

    def plot_monthly_distribution(self):
        """Create a stacked bar chart showing monthly time distribution"""
        if self.processed_data is None:
            self.process_data()
        
        monthly_counts = self.processed_data.groupby(['Month', 'Activity_Type']).size().unstack(fill_value=0)
        monthly_hours = monthly_counts * 0.5
        
        fig = go.Figure()
        for activity in self.activity_types.values():
            if activity in monthly_hours.columns:
                fig.add_trace(go.Bar(
                    name=activity,
                    x=[f"Month {m}" for m in monthly_hours.index],
                    y=monthly_hours[activity],
                    text=monthly_hours[activity].round(1),
                    textposition='auto',
                ))
        
        fig.update_layout(
            title='Monthly Time Distribution',
            xaxis_title='Month',
            yaxis_title='Hours',
            barmode='stack',
            showlegend=True,
            height=600
        )
        
        return fig

    def plot_daily_distribution(self):
        """Create a stacked bar chart showing daily time distribution by day of week"""
        if self.processed_data is None:
            self.process_data()
        
        daily_counts = self.processed_data.groupby(['Day', 'Activity_Type']).size().unstack(fill_value=0)
        daily_hours = daily_counts * 0.5
        
        # Reorder days to start with Sunday
        day_order = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        daily_hours = daily_hours.reindex(day_order)
        
        fig = go.Figure()
        for activity in self.activity_types.values():
            if activity in daily_hours.columns:
                fig.add_trace(go.Bar(
                    name=activity,
                    x=daily_hours.index,
                    y=daily_hours[activity],
                    text=daily_hours[activity].round(1),
                    textposition='auto',
                ))
        
        fig.update_layout(
            title='Time Distribution by Day of Week',
            xaxis_title='Day',
            yaxis_title='Hours',
            barmode='stack',
            showlegend=True,
            height=600
        )
        
        return fig
    
    def plot_weekly_distribution(self):
        """Create a stacked bar chart showing weekly time distribution"""
        if self.processed_data is None:
            self.process_data()
        
        weekly_counts = self.processed_data.groupby(['Month', 'Week', 'Activity_Type']).size().unstack(fill_value=0)
        weekly_hours = weekly_counts * 0.5
        
        # Create week labels
        week_labels = [f"M{m}W{w}" for m, w in weekly_hours.index]
        
        fig = go.Figure()
        for activity in self.activity_types.values():
            if activity in weekly_hours.columns:
                fig.add_trace(go.Bar(
                    name=activity,
                    x=week_labels,
                    y=weekly_hours[activity],
                    text=weekly_hours[activity].round(1),
                    textposition='auto',
                ))
        
        fig.update_layout(
            title='Weekly Time Distribution',
            xaxis_title='Week',
            yaxis_title='Hours',
            barmode='stack',
            showlegend=True,
            height=600
        )
        
        return fig
    
    def plot_weekly_summary(self):
        """Create a pie chart showing overall time distribution"""
        if self.processed_data is None:
            self.process_data()
        
        activity_counts = self.processed_data['Activity_Type'].value_counts()
        activity_hours = activity_counts * 0.5
        
        fig = px.pie(
            values=activity_hours.values,
            names=activity_hours.index,
            title='Overall Time Distribution',
            hole=0.3
        )
        fig.update_traces(textinfo='percent+label')
        return fig
    
    def get_activity_stats(self):
        """Generate summary statistics for activities"""
        if self.processed_data is None:
            self.process_data()
        
        stats = {}
        
        # Total hours per activity type
        total_hours = self.processed_data['Activity_Type'].value_counts() * 0.5
        stats['total_hours'] = total_hours.to_dict()
        
        # Hours by day of week
        daily_hours = self.processed_data.groupby(['Day', 'Activity_Type']).size() * 0.5
        stats['daily_hours'] = daily_hours.to_dict()
        
        # Monthly averages
        monthly_hours = self.processed_data.groupby(['Month', 'Activity_Type']).size() * 0.5
        monthly_avg = monthly_hours.groupby('Activity_Type').mean()
        stats['monthly_averages'] = monthly_avg.to_dict()
        
        # Most common specific activities with cleaning
        activity_details = self.processed_data[self.processed_data['Activity_Detail'] != ''].copy()
        
        # Clean activity details
        activity_details['Activity_Detail'] = (
            activity_details['Activity_Detail']
            .str.strip()
            .str.replace(r'\s+', ' ')  # Replace multiple spaces with single space
            .str.replace(r'[/\\]', '-')  # Replace slashes with hyphens
        )
        
        # Group by both type and detail
        activity_counts = (
            activity_details
            .groupby(['Activity_Type', 'Activity_Detail'])
            .size()
            * 0.5
        )
        
        # Get top 10 activities with their types
        top_activities = {}
        for (activity_type, activity_detail), hours in activity_counts.nlargest(10).items():
            key = f"{activity_detail} ({activity_type})"
            top_activities[key] = hours
        
        stats['top_activities'] = top_activities
        
        return stats
    
    def save_plots(self, output_dir):
        """Save all plots to the specified directory"""
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        monthly_dist = self.plot_monthly_distribution()
        monthly_dist.write_html(Path(output_dir) / "monthly_distribution.html")
        
        weekly_dist = self.plot_weekly_distribution()
        weekly_dist.write_html(Path(output_dir) / "weekly_distribution.html")
        
        daily_dist = self.plot_daily_distribution()
        daily_dist.write_html(Path(output_dir) / "daily_distribution.html")
        
        overall_dist = self.plot_weekly_summary()
        overall_dist.write_html(Path(output_dir) / "overall_distribution.html")
        
        print(f"Plots saved to {output_dir}")
    
    def generate_report(self):
        """Generate a text report of the analysis"""
        if self.processed_data is None:
            self.process_data()
        
        stats = self.get_activity_stats()
        report = [f"Time Analysis Report ({self.year})", "=" * 30, ""]
        
        report.append("Total Hours per Activity Type:")
        report.append("-" * 28)
        for activity, hours in stats['total_hours'].items():
            report.append(f"{activity}: {hours:.1f} hours")
        
        report.append("\nMonthly Average Hours:")
        report.append("-" * 20)
        for activity, hours in stats['monthly_averages'].items():
            report.append(f"{activity}: {hours:.1f} hours/month")
        
        report.append("\nTop 10 Specific Activities:")
        report.append("-" * 25)
        for activity, hours in stats['top_activities'].items():
            report.append(f"{activity}: {hours:.1f} hours")
        
        return "\n".join(report)

    def generate_detailed_stats(self):
        """Generate detailed statistics in CSV format for further analysis"""
        if self.processed_data is None:
            self.process_data()
        
        stats = []
        
        # Daily statistics by activity type
        daily_stats = (
            self.processed_data
            .groupby(['Month', 'Week', 'Day', 'Activity_Type'])
            .agg({
                'Activity_Detail': 'count',  # Number of 30-min blocks
            })
            .reset_index()
        )
        daily_stats['Hours'] = daily_stats['Activity_Detail'] * 0.5
        daily_stats = daily_stats.rename(columns={'Activity_Detail': 'Blocks'})
        
        # Specific activity statistics
        activity_stats = (
            self.processed_data[self.processed_data['Activity_Detail'] != '']
            .groupby(['Month', 'Week', 'Day', 'Activity_Type', 'Activity_Detail'])
            .size()
            .reset_index(name='Blocks')
        )
        activity_stats['Hours'] = activity_stats['Blocks'] * 0.5
        
        # Time slot analysis
        time_stats = (
            self.processed_data
            .groupby(['Time', 'Activity_Type'])
            .size()
            .reset_index(name='Frequency')
        )
        
        # Save all statistics to separate CSV files
        output_dir = Path('time_analysis_output/detailed_stats')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Daily summary by activity type
        daily_stats.to_csv(output_dir / 'daily_activity_summary.csv', index=False)
        
        # Specific activities details
        activity_stats.to_csv(output_dir / 'specific_activities.csv', index=False)
        
        # Time slot patterns
        time_stats.to_csv(output_dir / 'time_slot_patterns.csv', index=False)
        
        # Generate summary statistics
        summary_stats = {
            'total_blocks_by_type': self.processed_data['Activity_Type'].value_counts().to_dict(),
            'total_hours_by_type': (self.processed_data['Activity_Type'].value_counts() * 0.5).to_dict(),
            'days_tracked': len(self.processed_data['Day'].unique()),
            'weeks_tracked': len(self.processed_data.groupby(['Month', 'Week'])),
            'most_common_activities': (
                self.processed_data[self.processed_data['Activity_Detail'] != '']
                ['Activity_Detail'].value_counts().head(20).to_dict()
            ),
            'activity_type_by_day': (
                self.processed_data
                .groupby('Day')['Activity_Type']
                .value_counts()
                .unstack(fill_value=0)
                .to_dict()
            )
        }
        
        # Save summary statistics as JSON
        import json
        with open(output_dir / 'summary_statistics.json', 'w') as f:
            json.dump(summary_stats, f, indent=2)
        
        print(f"\nDetailed statistics saved to {output_dir}/")
        print("Files generated:")
        print("- daily_activity_summary.csv: Daily statistics by activity type")
        print("- specific_activities.csv: Detailed breakdown of specific activities")
        print("- time_slot_patterns.csv: Activity patterns by time of day")
        print("- summary_statistics.json: Overall statistics and patterns")

def main():
    parser = argparse.ArgumentParser(description='Analyze time tracking data from Excel file')
    parser.add_argument('excel_file', help='Path to the Excel file containing time tracking data')
    parser.add_argument('--year', '-y', type=int, default=2024,
                       help='Year of the time tracking data (default: 2024)')
    parser.add_argument('--output', '-o', default='time_analysis_output',
                       help='Directory to save output plots (default: time_analysis_output)')
    
    args = parser.parse_args()
    
    analyzer = TimeAnalyzer(args.excel_file, args.year)
    analyzer.save_plots(args.output)
    analyzer.generate_detailed_stats()  # Generate detailed statistics
    
    report = analyzer.generate_report()
    print("\n" + report)
    
    report_path = Path(args.output) / "report.txt"
    report_path.write_text(report)
    print(f"\nReport saved to {report_path}")

if __name__ == "__main__":
    main() 