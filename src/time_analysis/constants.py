"""Constants used throughout the time analysis application."""

from typing import Dict

# Activity type mappings
ACTIVITY_TYPES: Dict[str, str] = {
    "R": "Rest",
    "P": "Procrastination",
    "G": "Guilt-free Play",
    "M": "Mandatory Work",
    "W": "Productive Work",
}

# Time configuration
HOURS_PER_BLOCK: float = 0.5  # Each block represents 30 minutes

# Day order for consistent display
DAY_ORDER = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

# Default year
DEFAULT_YEAR = 2024

# Output directory
DEFAULT_OUTPUT_DIR = "time_analysis_output"
