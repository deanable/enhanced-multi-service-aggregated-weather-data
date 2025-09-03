import pandas as pd
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class ExportService:
    """
    Service for exporting weather data to various formats.
    """

    def __init__(self):
        """Initialize the export service."""
        pass

    def export_to_csv(self, data_df: pd.DataFrame, filepath: str) -> None:
        """
        Export weather data to a CSV file.

        Args:
            data_df: DataFrame containing weather data
            filepath: Path to save the CSV file

        Raises:
            Exception: If export fails
        """
        try:
            # Ensure the directory exists
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)

            # Export to CSV
            data_df.to_csv(filepath, index=False)
            logger.info(f"Successfully exported data to CSV: {filepath}")

        except Exception as e:
            logger.error(f"Failed to export to CSV: {e}")
            raise

    def export_to_excel(self, data_df: pd.DataFrame, filepath: str) -> None:
        """
        Export weather data to an Excel file.

        Args:
            data_df: DataFrame containing weather data
            filepath: Path to save the Excel file

        Raises:
            Exception: If export fails
        """
        try:
            # Ensure the directory exists
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)

            # Export to Excel
            data_df.to_excel(filepath, index=False, engine='openpyxl')
            logger.info(f"Successfully exported data to Excel: {filepath}")

        except Exception as e:
            logger.error(f"Failed to export to Excel: {e}")
            raise