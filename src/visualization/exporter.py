"""Export visualizations to various formats."""

import plotly.graph_objects as go
from pathlib import Path
from typing import Optional, List, Dict
import json
import numpy as np


class VisualizationExporter:
    """Export charts and visualizations to files."""

    def __init__(self, output_dir: str = "output"):
        """
        Initialize exporter.

        Args:
            output_dir: Directory to save exported files
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_html(self, fig: go.Figure, filename: str):
        """
        Export figure as interactive HTML.

        Args:
            fig: Plotly Figure object
            filename: Output filename (without extension)
        """
        output_path = self.output_dir / f"{filename}.html"
        fig.write_html(str(output_path))
        print(f"Exported HTML: {output_path}")

    def export_image(self, fig: go.Figure, filename: str, format: str = 'png',
                    width: int = 1200, height: int = 800):
        """
        Export figure as static image.

        Args:
            fig: Plotly Figure object
            filename: Output filename (without extension)
            format: Image format ('png', 'jpg', 'svg', 'pdf')
            width: Image width in pixels
            height: Image height in pixels

        Note: Requires kaleido package
        """
        try:
            output_path = self.output_dir / f"{filename}.{format}"
            fig.write_image(str(output_path), width=width, height=height, format=format)
            print(f"Exported {format.upper()}: {output_path}")
        except Exception as e:
            print(f"Warning: Could not export image (install kaleido: pip install kaleido): {e}")
            # Fallback to HTML if image export fails
            self.export_html(fig, filename)

    def export_data(self, data: Dict, filename: str):
        """
        Export analysis data as JSON.

        Args:
            data: Dictionary with analysis data
            filename: Output filename (without extension)
        """
        def convert_numpy(obj):
            """Convert numpy types to native Python types."""
            if isinstance(obj, (np.integer, np.int64)):
                return int(obj)
            elif isinstance(obj, (np.floating, np.float64)):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            return obj

        output_path = self.output_dir / f"{filename}.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=convert_numpy)
        print(f"Exported JSON: {output_path}")

    def export_all_formats(self, fig: go.Figure, filename: str,
                          export_html: bool = True,
                          export_png: bool = True):
        """
        Export figure in multiple formats.

        Args:
            fig: Plotly Figure object
            filename: Output filename (without extension)
            export_html: Whether to export HTML
            export_png: Whether to export PNG
        """
        if export_html:
            self.export_html(fig, filename)

        if export_png:
            self.export_image(fig, filename, format='png')

    def create_index_html(self, report_files: List[str]):
        """
        Create an index HTML file linking to all reports.

        Args:
            report_files: List of HTML filenames
        """
        html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Time Analysis Reports</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: #f5f5f5;
        }
        h1 {
            color: #333;
            border-bottom: 3px solid #AA96DA;
            padding-bottom: 10px;
        }
        ul {
            list-style: none;
            padding: 0;
        }
        li {
            background: white;
            margin: 10px 0;
            padding: 15px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        a {
            color: #AA96DA;
            text-decoration: none;
            font-size: 18px;
        }
        a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <h1>Time Analysis Reports</h1>
    <ul>
"""

        for report_file in report_files:
            report_name = report_file.replace('.html', '').replace('_', ' ').title()
            html_content += f'        <li><a href="{report_file}">{report_name}</a></li>\n'

        html_content += """
    </ul>
</body>
</html>
"""

        index_path = self.output_dir / "index.html"
        index_path.write_text(html_content)
        print(f"Created index: {index_path}")
