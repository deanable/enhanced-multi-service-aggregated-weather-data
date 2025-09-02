import pandas as pd
import logging

logger = logging.getLogger(__name__)

class ExportService:
    """
    A service class dedicated to handling data export functionality.
    """
    @staticmethod
    def export_to_csv(df: pd.DataFrame, filepath: str):
        """
        Exports a pandas DataFrame to a CSV file.

        Args:
            df: The DataFrame to export.
            filepath: The path to save the CSV file to.

        Raises:
            Exception: If any error occurs during the file write operation.
        """
        try:
            logger.info(f"Exporting data to CSV at: {filepath}")
            df.to_csv(filepath, index=False)
            logger.info("CSV export successful.")
        except Exception as e:
            logger.error(f"Failed to export to CSV: {e}", exc_info=True)
            raise

    @staticmethod
    def export_to_excel(df: pd.DataFrame, filepath: str):
        """
        Exports a pandas DataFrame to an Excel (.xlsx) file.

        Args:
            df: The DataFrame to export.
            filepath: The path to save the Excel file to.

        Raises:
            Exception: If any error occurs during the file write operation.
        """
        try:
            logger.info(f"Exporting data to Excel at: {filepath}")
            # The 'openpyxl' engine is required for .xlsx files.
            df.to_excel(filepath, index=False, engine='openpyxl')
            logger.info("Excel export successful.")
        except Exception as e:
            logger.error(f"Failed to export to Excel: {e}", exc_info=True)
            raise
