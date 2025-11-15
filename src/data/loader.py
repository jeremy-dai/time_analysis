"""Data loader for CSV and Excel files."""

import pandas as pd
from pathlib import Path
from typing import List, Union, Optional
import re
import warnings

warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')


class DataLoader:
    """Load time tracking data from CSV or Excel files."""

    def __init__(self, data_path: Union[str, Path]):
        """
        Initialize data loader.

        Args:
            data_path: Path to a single file or directory containing data files
        """
        self.data_path = Path(data_path)
        self.raw_data = []

    def load(self) -> pd.DataFrame:
        """
        Load all data from the specified path.

        Returns:
            DataFrame with columns: Time, Day, Activity, Month, Week, Year
        """
        if self.data_path.is_file():
            self._load_single_file(self.data_path)
        elif self.data_path.is_dir():
            self._load_directory(self.data_path)
        else:
            raise ValueError(f"Path does not exist: {self.data_path}")

        if not self.raw_data:
            raise ValueError("No data was loaded")

        return pd.concat(self.raw_data, ignore_index=True)

    def _load_directory(self, directory: Path):
        """Load all CSV and Excel files from a directory."""
        # Find CSV files
        csv_files = sorted(directory.glob("*.csv"))
        for csv_file in csv_files:
            try:
                self._load_single_file(csv_file)
            except Exception as e:
                print(f"Warning: Failed to load {csv_file}: {e}")

        # Find Excel files
        excel_files = sorted(directory.glob("*.xlsx")) + sorted(directory.glob("*.xls"))
        for excel_file in excel_files:
            try:
                self._load_excel_file(excel_file)
            except Exception as e:
                print(f"Warning: Failed to load {excel_file}: {e}")

    def _load_single_file(self, file_path: Path):
        """Load a single file (CSV or Excel)."""
        if file_path.suffix.lower() == '.csv':
            self._load_csv_file(file_path)
        elif file_path.suffix.lower() in ['.xlsx', '.xls']:
            self._load_excel_file(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")

    def _parse_filename(self, filename: str) -> Optional[tuple]:
        """
        Parse filename to extract year, month, and week.

        Expected format: "YYYY Time-M.W.csv" or similar
        Example: "2023 Time-1.1.csv" -> (2023, 1, 1)
        """
        # Pattern: YYYY Time-M.W
        pattern = r'(\d{4})\s+[Tt]ime-(\d+)\.(\d+)'
        match = re.search(pattern, filename)

        if match:
            year = int(match.group(1))
            month = int(match.group(2))
            week = int(match.group(3))
            return year, month, week

        return None

    def _load_csv_file(self, csv_file: Path):
        """Load a single CSV file."""
        # Parse filename to get year, month, week
        parsed = self._parse_filename(csv_file.name)
        if not parsed:
            print(f"Warning: Could not parse filename {csv_file.name}, skipping")
            return

        year, month, week = parsed

        # Read CSV, skipping first row (header), using second row as column names
        df = pd.read_csv(csv_file, skiprows=1, encoding='utf-8-sig')

        # Expected columns: Time, Day1, Day2, ..., Day7
        # First column should be Time
        if len(df.columns) < 2:
            print(f"Warning: Insufficient columns in {csv_file.name}")
            return

        # Rename columns to standard format
        weekdays = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        time_col = df.columns[0]
        day_cols = df.columns[1:8]  # Next 7 columns are days

        # Keep only relevant rows (time slots, not summary rows at bottom)
        # Filter out rows where Time doesn't look like a time (e.g., "08:00")
        df = df[df[time_col].astype(str).str.match(r'^\d{2}:\d{2}$', na=False)]

        # Rename for consistency
        rename_dict = {time_col: 'Time'}
        for i, day_col in enumerate(day_cols):
            if i < len(weekdays):
                rename_dict[day_col] = weekdays[i]

        df = df.rename(columns=rename_dict)

        # Melt the dataframe
        df_melted = df.melt(
            id_vars=['Time'],
            value_vars=weekdays,
            var_name='Day',
            value_name='Activity'
        )

        # Add metadata
        df_melted['Month'] = month
        df_melted['Week'] = week
        df_melted['Year'] = year

        self.raw_data.append(df_melted)
        print(f"Loaded {csv_file.name}: {year}-M{month}W{week}")

    def _load_excel_file(self, excel_file: Path):
        """Load an Excel file with multiple sheets."""
        excel_data = pd.ExcelFile(excel_file)

        # Try to extract year from filename
        year_match = re.search(r'(\d{4})', excel_file.name)
        default_year = int(year_match.group(1)) if year_match else 2024

        for sheet_name in excel_data.sheet_names:
            try:
                self._load_excel_sheet(excel_file, sheet_name, default_year)
            except Exception as e:
                print(f"Warning: Failed to load sheet {sheet_name}: {e}")

    def _load_excel_sheet(self, excel_file: Path, sheet_name: str, year: int):
        """Load a single sheet from an Excel file."""
        # Parse sheet name (format: M.W or similar)
        if isinstance(sheet_name, float):
            sheet_name = str(int(sheet_name))

        if sheet_name.lower() == 'sample':
            return

        try:
            parts = sheet_name.split('.')
            if len(parts) != 2:
                return

            month, week = int(parts[0]), int(parts[1])
        except (ValueError, AttributeError):
            return

        # Read the sheet
        df = pd.read_excel(
            excel_file,
            sheet_name=sheet_name,
            skiprows=1,
            usecols="A:H"
        )

        # Rename columns
        weekdays = ['Time', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
        df.columns = weekdays

        # Melt the dataframe
        df_melted = df.melt(
            id_vars=['Time'],
            value_vars=weekdays[1:],
            var_name='Day',
            value_name='Activity'
        )

        df_melted['Month'] = month
        df_melted['Week'] = week
        df_melted['Year'] = year

        self.raw_data.append(df_melted)
        print(f"Loaded sheet {sheet_name} from {excel_file.name}")
