import sys
from datetime import date, timedelta
import pandas as pd
from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QTabWidget, QStatusBar,
    QGroupBox, QGridLayout, QLabel, QComboBox, QDateEdit, QSpinBox,
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog
)

# Backend imports
from emsawd.core.services import WeatherService
from emsawd.repositories.geocoding_repository import GeocodingRepository
from emsawd.repositories.weather_repository import WeatherRepository
from emsawd.core.export_service import ExportService
from .matplotlib_widget import MatplotlibCanvas


class MainWindow(QMainWindow):
    """
    The main window for the Historic Weather Data application.
    """
    def __init__(self, parent=None):
        """
        Initializes the main window.
        """
        super().__init__(parent)

        # Initialize backend services
        geocoding_repo = GeocodingRepository()
        weather_repo = WeatherRepository()
        self.weather_service = WeatherService(geocoding_repo, weather_repo)
        self.export_service = ExportService()

        # To hold the current data
        self.data_df = None

        self.setWindowTitle("Historic Weather Data Analyzer")
        self.setGeometry(100, 100, 1200, 800)  # x, y, width, height

        # Create the central widget and layout
        self.central_widget = QWidget()
        self.main_layout = QVBoxLayout(self.central_widget)
        self.setCentralWidget(self.central_widget)

        # Create the input panel
        self._create_input_panel()
        self.main_layout.addWidget(self.input_group_box)

        # Connect signals to slots
        self.preset_combo.currentTextChanged.connect(self._on_preset_changed)
        self.fetch_button.clicked.connect(self._on_fetch_data_clicked)
        self.export_csv_button.clicked.connect(self._on_export_csv_clicked)
        self.export_excel_button.clicked.connect(self._on_export_excel_clicked)
        self._on_preset_changed("Last 7 Days") # Set initial state

        # Create the tab widget for different views
        self.tab_widget = QTabWidget()
        self.main_layout.addWidget(self.tab_widget)

        # Create the tabs
        self._create_tabs()

        # Create the status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def _create_input_panel(self):
        """
        Creates the input panel with all the user controls.
        """
        self.input_group_box = QGroupBox("Query Configuration")
        layout = QGridLayout()

        # Date Range Presets
        layout.addWidget(QLabel("Date Range Preset:"), 0, 0)
        self.preset_combo = QComboBox()
        self.preset_combo.addItems([
            "Custom", "Last 7 Days", "Last 14 Days", "Last 30 Days",
            "Last 3 Months", "Last 6 Months", "Last 12 Months"
        ])
        layout.addWidget(self.preset_combo, 0, 1)

        # Start Date
        layout.addWidget(QLabel("Start Date:"), 1, 0)
        self.start_date_edit = QDateEdit(calendarPopup=True)
        self.start_date_edit.setQDate(QDate.currentDate().addDays(-7))
        self.start_date_edit.setEnabled(False)
        layout.addWidget(self.start_date_edit, 1, 1)

        # End Date
        layout.addWidget(QLabel("End Date:"), 1, 2)
        self.end_date_edit = QDateEdit(calendarPopup=True)
        self.end_date_edit.setQDate(QDate.currentDate())
        self.end_date_edit.setEnabled(False)
        layout.addWidget(self.end_date_edit, 1, 3)

        # Number of Past Years
        layout.addWidget(QLabel("Number of Past Years:"), 2, 0)
        self.years_spinbox = QSpinBox()
        self.years_spinbox.setRange(1, 20)
        self.years_spinbox.setValue(3)
        layout.addWidget(self.years_spinbox, 2, 1)

        # Location
        layout.addWidget(QLabel("Location (City):"), 2, 2)
        self.location_edit = QLineEdit()
        self.location_edit.setPlaceholderText("e.g., New York")
        layout.addWidget(self.location_edit, 2, 3)

        # Fetch Button
        self.fetch_button = QPushButton("Fetch Historical Data")
        layout.addWidget(self.fetch_button, 3, 0, 1, 2)

        # Export Buttons
        self.export_csv_button = QPushButton("Export to CSV")
        self.export_csv_button.setEnabled(False)
        layout.addWidget(self.export_csv_button, 3, 2)

        self.export_excel_button = QPushButton("Export to Excel")
        self.export_excel_button.setEnabled(False)
        layout.addWidget(self.export_excel_button, 3, 3)

        self.input_group_box.setLayout(layout)

    def _on_fetch_data_clicked(self):
        """
        Handles the button click to fetch and display weather data.
        """
        location = self.location_edit.text()
        if not location:
            self.status_bar.showMessage("Error: Location cannot be empty.", 5000)
            return

        try:
            self.status_bar.showMessage(f"Fetching data for {location}...")
            self.fetch_button.setEnabled(False)

            # Get parameters from UI
            start_date = self.start_date_edit.date().toPyDate()
            end_date = self.end_date_edit.date().toPyDate()
            years = self.years_spinbox.value()

            # Call the service
            records = self.weather_service.fetch_weather_for_range(
                location, start_date, end_date, years
            )

            # Populate the data grid with the records
            self.data_df = self._populate_data_grid(records)

            # Plot the graphs and manage button state
            if self.data_df is not None and not self.data_df.empty:
                self._plot_temperature_graph()
                self._plot_precipitation_graph()
                self.export_csv_button.setEnabled(True)
                self.export_excel_button.setEnabled(True)
                self.status_bar.showMessage(f"Successfully loaded {len(records)} records.", 5000)
            else:
                self.export_csv_button.setEnabled(False)
                self.export_excel_button.setEnabled(False)
                # Message is already shown by _populate_data_grid if no data

        except ValueError as e:
            self.status_bar.showMessage(f"Error: {e}", 10000)
            self.export_csv_button.setEnabled(False)
            self.export_excel_button.setEnabled(False)
        except Exception as e:
            self.status_bar.showMessage(f"An unexpected error occurred: {e}", 10000)
            self.export_csv_button.setEnabled(False)
            self.export_excel_button.setEnabled(False)
        finally:
            self.fetch_button.setEnabled(True)


    def _on_preset_changed(self, text: str):
        """
        Handles the logic when the date range preset is changed.
        """
        today = QDate.currentDate()
        self.end_date_edit.setQDate(today)

        if text == "Custom":
            self.start_date_edit.setEnabled(True)
            self.end_date_edit.setEnabled(True)
            return

        self.start_date_edit.setEnabled(False)
        self.end_date_edit.setEnabled(False)

        if text == "Last 7 Days":
            self.start_date_edit.setQDate(today.addDays(-7))
        elif text == "Last 14 Days":
            self.start_date_edit.setQDate(today.addDays(-14))
        elif text == "Last 30 Days":
            self.start_date_edit.setQDate(today.addDays(-30))
        elif text == "Last 3 Months":
            self.start_date_edit.setQDate(today.addMonths(-3))
        elif text == "Last 6 Months":
            self.start_date_edit.setQDate(today.addMonths(-6))
        elif text == "Last 12 Months":
            self.start_date_edit.setQDate(today.addMonths(-12))

    def _create_tabs(self):
        """
        Creates the tabs for the data grid and graphs.
        """
        # Data Grid Tab
        self.data_grid_tab = QWidget()
        self.data_grid_layout = QVBoxLayout(self.data_grid_tab)
        self.data_table = QTableWidget()
        self.data_grid_layout.addWidget(self.data_table)
        self.tab_widget.addTab(self.data_grid_tab, "Data Grid")

        # Temperature Graph Tab
        self.temp_chart = MatplotlibCanvas(self)
        self.tab_widget.addTab(self.temp_chart, "Temperature Graph")

        # Precipitation Graph Tab
        self.precip_chart = MatplotlibCanvas(self)
        self.tab_widget.addTab(self.precip_chart, "Precipitation Graph")

    def _populate_data_grid(self, records):
        """
        Populates the QTableWidget with the fetched weather records.
        Returns the created DataFrame.
        """
        if not records:
            self.data_table.setRowCount(0)
            self.data_table.setColumnCount(0)
            self.status_bar.showMessage("No data found for the selected criteria.", 5000)
            return None

        df = pd.DataFrame(records)

        # Reorder and rename columns for display
        df = df.rename(columns={
            'record_date': 'Date',
            'year': 'Year',
            'location': 'Location',
            'max_temp_c': 'Max Temp (°C)',
            'min_temp_c': 'Min Temp (°C)',
            'precipitation_mm': 'Precipitation (mm)'
        })
        # The location is empty in the record, so we'll fill it from the UI input
        df['Location'] = self.location_edit.text()

        headers = ['Date', 'Year', 'Location', 'Max Temp (°C)', 'Min Temp (°C)', 'Precipitation (mm)']
        df = df[headers]

        self.data_table.setRowCount(df.shape[0])
        self.data_table.setColumnCount(df.shape[1])
        self.data_table.setHorizontalHeaderLabels(df.columns)

        for row in range(df.shape[0]):
            for col in range(df.shape[1]):
                item = QTableWidgetItem(str(df.iat[row, col]))
                self.data_table.setItem(row, col, item)

        self.data_table.resizeColumnsToContents()
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        return df

    def _plot_temperature_graph(self):
        """
        Plots the max temperature line chart.
        """
        self.temp_chart.clear()

        # Prepare data for plotting
        self.data_df['Date'] = pd.to_datetime(self.data_df['Date'])
        self.data_df['MonthDay'] = self.data_df['Date'].dt.strftime('%m-%d')

        pivot_df = self.data_df.pivot(index='MonthDay', columns='Year', values='Max Temp (°C)')

        for year in pivot_df.columns:
            self.temp_chart.axes.plot(pivot_df.index, pivot_df[year], label=str(year))

        self.temp_chart.axes.set_title('Maximum Temperature Trends')
        self.temp_chart.axes.set_xlabel('Date (Month-Day)')
        self.temp_chart.axes.set_ylabel('Max Temperature (°C)')
        self.temp_chart.axes.legend()
        self.temp_chart.axes.grid(True)

        # Improve x-axis readability
        # Show fewer labels if there are many dates
        if len(pivot_df.index) > 20:
            step = len(pivot_df.index) // 10
            self.temp_chart.axes.set_xticks(self.temp_chart.axes.get_xticks()[::step])

        self.temp_chart.figure.tight_layout()
        self.temp_chart.draw()

    def _plot_precipitation_graph(self):
        """
        Plots the precipitation bar chart.
        """
        self.precip_chart.clear()

        # Use a copy to avoid SettingWithCopyWarning
        df_sorted = self.data_df.sort_values('Date').copy()
        df_sorted['DateStr'] = df_sorted['Date'].dt.strftime('%Y-%m-%d')

        self.precip_chart.axes.bar(df_sorted['DateStr'], df_sorted['Precipitation (mm)'])

        self.precip_chart.axes.set_title('Daily Precipitation')
        self.precip_chart.axes.set_xlabel('Date')
        self.precip_chart.axes.set_ylabel('Precipitation (mm)')
        self.precip_chart.axes.grid(axis='y')

        # Improve x-axis readability
        self.precip_chart.figure.autofmt_xdate(rotation=45, ha='right')
        if len(df_sorted['DateStr']) > 30:
             step = len(df_sorted['DateStr']) // 15
             self.precip_chart.axes.set_xticks(self.precip_chart.axes.get_xticks()[::step])

        self.precip_chart.figure.tight_layout()
        self.precip_chart.draw()


    def _on_export_csv_clicked(self):
        """
        Handles exporting the current data to a CSV file.
        """
        if self.data_df is None or self.data_df.empty:
            self.status_bar.showMessage("No data available to export.", 5000)
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save CSV File", "", "CSV Files (*.csv);;All Files (*)"
        )

        if filepath:
            try:
                self.status_bar.showMessage(f"Exporting to {filepath}...")
                self.export_service.export_to_csv(self.data_df, filepath)
                self.status_bar.showMessage("Successfully exported to CSV.", 5000)
            except Exception as e:
                self.status_bar.showMessage(f"Export failed: {e}", 10000)

    def _on_export_excel_clicked(self):
        """
        Handles exporting the current data to an Excel file.
        """
        if self.data_df is None or self.data_df.empty:
            self.status_bar.showMessage("No data available to export.", 5000)
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self, "Save Excel File", "", "Excel Files (*.xlsx);;All Files (*)"
        )

        if filepath:
            try:
                self.status_bar.showMessage(f"Exporting to {filepath}...")
                self.export_service.export_to_excel(self.data_df, filepath)
                self.status_bar.showMessage("Successfully exported to Excel.", 5000)
            except Exception as e:
                self.status_bar.showMessage(f"Export failed: {e}", 10000)


if __name__ == '__main__':
    # This is for testing the window directly
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
