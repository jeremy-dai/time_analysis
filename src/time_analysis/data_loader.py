"""Data loading functionality for CSV and Excel files."""

import logging
import sys
from pathlib import Path
from typing import List, Optional, Tuple

import pandas as pd

from .constants import DAY_ORDER

logger = logging.getLogger(__name__)


class DataLoader:
    """Handles loading time tracking data from various file formats."""

    def __init__(self, file_path: str) -> None:
        """Initialize the data loader.

        Args:
            file_path: Path to the data file (CSV or Excel)
        """
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

    def load_csv_files(self, directory: str) -> pd.DataFrame:
        """Load multiple CSV files from a directory (one per week).

        Expected filename format: YYYY_MM_WW.csv or YYYY-MM-WW.csv
        Example: 2024_01_01.csv (Year 2024, Month 01, Week 01)

        Args:
            directory: Directory containing weekly CSV files

        Returns:
            Combined DataFrame from all CSV files
        """
        dir_path = Path(directory)
        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        csv_files = list(dir_path.glob("*.csv"))
        if not csv_files:
            raise ValueError(f"No CSV files found in {directory}")

        logger.info(f"Found {len(csv_files)} CSV files in {directory}")
        all_data: List[pd.DataFrame] = []

        for csv_file in sorted(csv_files):
            logger.info(f"Processing {csv_file.name}")

            # Parse filename to extract year, month, week
            try:
                year, month, week = self._parse_filename(csv_file.stem)
            except ValueError as e:
                logger.warning(f"Skipping {csv_file.name}: {e}")
                continue

            # Load CSV file
            df = pd.read_csv(csv_file)

            # Validate and standardize column names
            df = self._standardize_columns(df)

            # Melt the dataframe to convert days to rows
            df_melted = df.melt(
                id_vars=["Time"],
                value_vars=DAY_ORDER,
                var_name="Day",
                value_name="Activity",
            )

            df_melted["Year"] = year
            df_melted["Month"] = month
            df_melted["Week"] = week
            all_data.append(df_melted)

        if not all_data:
            raise ValueError("No valid CSV files were processed")

        combined_df = pd.concat(all_data, ignore_index=True)
        logger.info(f"Combined data shape: {combined_df.shape}")
        return combined_df

    def load_excel_file(self) -> pd.DataFrame:
        """Load data from Excel file with multiple sheets (legacy format).

        Expected sheet name format: M.W (Month.Week), e.g., "1.1" for January Week 1

        Returns:
            Combined DataFrame from all sheets
        """
        logger.info(f"Loading Excel file: {self.file_path}")
        excel_file = pd.ExcelFile(self.file_path)
        logger.info(f"Found sheets: {excel_file.sheet_names}")

        all_sheets: List[pd.DataFrame] = []

        for sheet_name in excel_file.sheet_names:
            logger.info(f"Processing sheet: {sheet_name}")

            # Parse sheet name
            try:
                month, week = self._parse_sheet_name(sheet_name)
            except ValueError as e:
                logger.warning(f"Skipping sheet {sheet_name}: {e}")
                continue

            # Read the sheet, skipping the first row
            df = pd.read_excel(
                self.file_path, sheet_name=sheet_name, skiprows=1, usecols="A:H"
            )

            # Standardize columns
            df = self._standardize_columns(df)

            # Melt the dataframe
            df_melted = df.melt(
                id_vars=["Time"],
                value_vars=DAY_ORDER,
                var_name="Day",
                value_name="Activity",
            )

            df_melted["Month"] = month
            df_melted["Week"] = week
            all_sheets.append(df_melted)

        if not all_sheets:
            raise ValueError("No valid sheets were processed")

        combined_df = pd.concat(all_sheets, ignore_index=True)
        logger.info(f"Combined data shape: {combined_df.shape}")
        return combined_df

    def load(self) -> pd.DataFrame:
        """Load data from the file (auto-detect format).

        Returns:
            DataFrame with time tracking data
        """
        if self.file_path.suffix.lower() in [".xlsx", ".xls"]:
            return self.load_excel_file()
        elif self.file_path.suffix.lower() == ".csv":
            # Single CSV file - treat as one week
            logger.warning(
                "Loading single CSV file. Consider using load_csv_files() for multiple weeks."
            )
            df = pd.read_csv(self.file_path)
            df = self._standardize_columns(df)
            df_melted = df.melt(
                id_vars=["Time"],
                value_vars=DAY_ORDER,
                var_name="Day",
                value_name="Activity",
            )
            df_melted["Month"] = 1
            df_melted["Week"] = 1
            return df_melted
        else:
            raise ValueError(f"Unsupported file format: {self.file_path.suffix}")

    def _parse_filename(self, filename: str) -> Tuple[int, int, int]:
        """Parse filename to extract year, month, and week.

        Expected format: YYYY_MM_WW or YYYY-MM-WW

        Args:
            filename: Filename without extension

        Returns:
            Tuple of (year, month, week)
        """
        # Replace hyphens with underscores for consistent parsing
        filename = filename.replace("-", "_")
        parts = filename.split("_")

        if len(parts) != 3:
            raise ValueError(f"Invalid filename format: {filename}. Expected YYYY_MM_WW")

        try:
            year = int(parts[0])
            month = int(parts[1])
            week = int(parts[2])

            if not (1 <= month <= 12):
                raise ValueError(f"Invalid month: {month}")
            if not (1 <= week <= 5):
                raise ValueError(f"Invalid week: {week}")

            return year, month, week
        except (ValueError, IndexError) as e:
            raise ValueError(f"Could not parse filename {filename}: {e}")

    def _parse_sheet_name(self, sheet_name: str) -> Tuple[int, int]:
        """Parse Excel sheet name to extract month and week.

        Args:
            sheet_name: Sheet name in format M.W

        Returns:
            Tuple of (month, week)
        """
        if isinstance(sheet_name, float):
            sheet_name = str(int(sheet_name))

        if sheet_name.lower() == "sample":
            raise ValueError("Sample sheet")

        try:
            month, week = map(int, sheet_name.split("."))
            return month, week
        except (ValueError, AttributeError) as e:
            raise ValueError(f"Invalid sheet name format: {sheet_name}")

    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Standardize column names to expected format.

        Args:
            df: Input DataFrame

        Returns:
            DataFrame with standardized columns
        """
        expected_columns = ["Time"] + DAY_ORDER

        # If columns match expected, return as-is
        if list(df.columns) == expected_columns:
            return df

        # Otherwise, rename columns
        if len(df.columns) == len(expected_columns):
            df.columns = expected_columns
            return df

        raise ValueError(
            f"Unexpected number of columns. Expected {len(expected_columns)}, got {len(df.columns)}"
        )
